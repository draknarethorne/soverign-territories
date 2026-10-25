"""Artist browser publication, domain isolation, repeat and bounded-storage tests."""
import contextlib
import hashlib
import io
import json
import pathlib
import re
import sys
import tempfile
import types
import unittest
from unittest import mock

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import artists_gallery as gallery  # noqa: E402
import people_gallery  # noqa: E402
from likeness_library import domains, gallery_chrome, report_assets, review_gallery  # noqa: E402


class ArtistGalleryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.cache = self.root / "cache.json"
        self.cache.write_text('{"emb":{}}', encoding="utf-8")
        self.source = self.add_image("Artists/Studio A/Aster/gallery/one.jpg")
        duplicate = self.root / "Artists" / "Studio A" / "Aster" / "review" / "two.jpg"
        duplicate.parent.mkdir(parents=True)
        duplicate.write_bytes(self.source.read_bytes())
        self.add_image("Artists/Studio B/review/unassigned.jpg", (20, 120, 40))
        self.add_image("Various/gallery/do-not-process.jpg")
        self.add_image("Artists/Studio A/_archive/gallery/ignored.jpg")
        self.add_image("Models/Person/gallery/person.jpg")
        self.out = self.root / "_reports" / "artists"
        self.config = mock.patch.object(gallery.likeness.cw, "load_cfg", return_value={})
        self.config.start()
        self.addCleanup(self.config.stop)

    def add_image(self, relative, color=(120, 40, 20)):
        path = self.root / pathlib.PurePosixPath(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (400, 600), color).save(path)
        return path

    def run_cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return gallery.main(["--root", str(self.root), "--cache", str(self.cache), *args])

    def files(self, path):
        return {p.relative_to(path).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in path.rglob("*") if p.is_file()}

    def test_preview_does_not_decode_or_write_and_inventory_is_artist_only(self):
        before = self.files(self.root)
        with mock.patch.object(gallery.Image, "open", side_effect=AssertionError("preview decoded")):
            self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertEqual(self.files(self.root), before)
        sources = gallery.inventory(self.root)
        self.assertEqual(len(sources), 3)
        self.assertTrue(all(source.relative_to(self.root).parts[0] == "Artists"
                            for _, _, _, source in sources))

    def test_publish_shared_thumbnails_and_exact_repeat_preserve_sources_and_cache(self):
        before = self.files(self.root)
        with mock.patch.object(gallery.likeness, "Embedder", side_effect=AssertionError("inference")):
            self.assertEqual(self.run_cli("--apply"), 0)
        for name, record in before.items():
            self.assertEqual(self.files(self.root)[name], record)
        manifest = json.loads((self.out / gallery.MANIFEST).read_text())
        self.assertEqual(manifest["thumbnailCount"], 2)
        self.assertLess(manifest["thumbnailBytes"], 100_000)
        self.assertIn("intake_runs.html", manifest["files"])
        self.assertTrue((self.out / "intake_runs.html").is_file())
        for path in (self.out / "thumbnails").glob("*.jpg"):
            with Image.open(path) as image:
                self.assertEqual(image.size, gallery.SIZE)
        published = self.files(self.out)
        self.assertEqual(self.run_cli("--check"), 0)
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertEqual(self.files(self.out), published)
        page = (self.out / "artists_gallery_review.html").read_text(encoding="utf-8")
        self.assertIn('loading=\'lazy\'', gallery.SCRIPT)
        self.assertNotIn("base64", page)
        self.assertIn("gallery-manifest.json", str(self.out / gallery.MANIFEST))
        self.assertIn("unassessed (no cached face result)", page)
        self.assertIn("library-footer", page)
        self.assertIn("aria-current", page)

    def test_check_detects_changed_inputs_without_writing(self):
        self.assertEqual(self.run_cli("--apply"), 0)
        self.source.write_bytes((self.root / "Artists/Studio B/review/unassigned.jpg").read_bytes())
        before = self.files(self.out)
        self.assertEqual(self.run_cli("--check"), 1)
        self.assertEqual(self.files(self.out), before)

    def test_refresh_prunes_only_proven_obsolete_thumbnails(self):
        self.assertEqual(self.run_cli("--apply"), 0)
        old = hashlib.sha256(self.source.read_bytes()).hexdigest()
        (self.source.parent.parent / "review" / "two.jpg").unlink()
        self.source.unlink()
        unknown = self.out / "thumbnails" / "custom.jpg"
        unknown.write_bytes(b"user asset")
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertFalse((self.out / "thumbnails" / f"{old}.jpg").exists())
        self.assertEqual(unknown.read_bytes(), b"user asset")

    def test_preserves_edited_report_and_reports_explicit_error(self):
        self.assertEqual(self.run_cli("--apply"), 0)
        report = self.out / "artists_gallery.html"
        report.write_text("manual edit", encoding="utf-8")
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertEqual(report.read_text(), "manual edit")

    def test_unreadable_photo_is_a_diagnostic_not_success(self):
        (self.source.parent / "broken.jpg").write_bytes(b"broken")
        self.assertEqual(self.run_cli("--apply"), 1)
        manifest = json.loads((self.out / gallery.MANIFEST).read_text())
        self.assertEqual(len(manifest["diagnostics"]), 1)
        self.assertIn("Thumbnail unavailable", manifest["diagnostics"][0])

    def test_json_content_cannot_break_out_of_script(self):
        page = gallery.page([{"artist": "</script><script>alert(1)</script>"}], detail=True, stats="test").decode()
        self.assertNotIn("</script><script>alert", page)
        self.assertIn("\\u003c/script", page)

    def test_general_pages_reject_legacy_artist_option_before_build(self):
        for main in (people_gallery.main, review_gallery.main):
            with self.subTest(main=main), mock.patch.object(gallery.likeness, "build") as build:
                with self.assertRaises(SystemExit) as error:
                    with contextlib.redirect_stderr(io.StringIO()):
                        main(["--artists"])
                self.assertEqual(error.exception.code, 2)
                build.assert_not_called()
                self.assertIsNone(domains.CURRENT.get())

    def test_supplied_mixed_spaces_are_refused_not_hidden(self):
        space = types.SimpleNamespace(keys=["Models/A", "Artists/Studio/Someone"], photos=[])
        with self.assertRaisesRegex(ValueError, "general-only"):
            people_gallery.collect({}, {}, self.root, space, ["Models"])
        with self.assertRaisesRegex(ValueError, "general-only"):
            review_gallery.collect_items({}, {}, self.root, None, space, {})

    def test_general_entry_build_context_is_general_and_read_only(self):
        def build(_args):
            self.assertEqual(domains.CURRENT.get(), "general")
            self.assertTrue(domains.READ_ONLY.get())
            raise ValueError("test stop before publication")
        for main in (people_gallery.main, review_gallery.main):
            with mock.patch.object(gallery.likeness, "build", side_effect=build):
                with self.assertRaisesRegex(ValueError, "test stop"):
                    main(["--no-renders"])
            self.assertIsNone(domains.CURRENT.get())

    def test_general_build_does_not_analyze_artist_or_reuse_artist_mean(self):
        cache = gallery.likeness.Cache(self.cache)
        cache.centering_mean = [100.0, 100.0]
        cache.centering_domain = "artists"
        cache.save()
        args = types.SimpleNamespace(root=str(self.root), cache=str(self.cache),
                                     embedder=lambda _: {"v": [1.0, 0.0], "faces": 1, "px": 100},
                                     policy=None)
        with domains.activate("general", read_only=True):
            _cfg, _st, _work, built_cache, space = gallery.likeness.build(args)
        self.assertEqual(built_cache.centering_domain, "general")
        self.assertIsNone(built_cache.centering_mean)
        self.assertEqual({photo.group for photo in space.photos}, {"Models", "Various"})

    def test_people_manifest_records_only_exact_regenerated_bytes(self):
        self.out.mkdir(parents=True)
        name = "people_gallery_review_files/source_chest_abcdef123456.jpg"
        target = self.out / name
        target.parent.mkdir()
        target.write_bytes(b"regenerated")
        with contextlib.redirect_stdout(io.StringIO()):
            report_assets.record(self.out, {name: b"regenerated"})
        manifest = json.loads((self.out / report_assets.MANIFEST).read_text())
        self.assertEqual(manifest["files"][name], hashlib.sha256(b"regenerated").hexdigest())
        target.write_bytes(b"manual change")
        with contextlib.redirect_stdout(io.StringIO()) as messages:
            report_assets.record(self.out, {name: b"regenerated"})
        self.assertIn("retained in backups", messages.getvalue())
        manifest = json.loads((self.out / report_assets.MANIFEST).read_text())
        self.assertNotIn(name, manifest["files"])
        self.assertEqual(target.read_bytes(), b"manual change")

    def test_people_manifest_merges_overview_review_and_preserves_unknown_assets(self):
        self.out.mkdir(parents=True)
        unknown = self.out / "notes.txt"
        unknown.write_bytes(b"user notes")
        for name in ("people_gallery.html", "people_gallery_review.html"):
            (self.out / name).write_bytes(name.encode())
            with contextlib.redirect_stdout(io.StringIO()):
                report_assets.record(self.out, {name: name.encode()})
        files = json.loads((self.out / report_assets.MANIFEST).read_text())["files"]
        self.assertEqual(set(files), {"people_gallery.html", "people_gallery_review.html"})
        self.assertEqual(unknown.read_bytes(), b"user notes")

    def test_atomic_report_publish_retries_lock_and_never_hides_persistent_failure(self):
        stage, target = self.root / "stage", self.root / "target"
        with mock.patch.object(report_assets.os, "replace", side_effect=[PermissionError("locked"), None]) as replace, \
                mock.patch.object(report_assets.time, "sleep"), contextlib.redirect_stdout(io.StringIO()) as messages:
            report_assets.replace_file(stage, target)
        self.assertEqual(replace.call_count, 2)
        self.assertIn("retrying atomic replacement", messages.getvalue())
        with mock.patch.object(report_assets.os, "replace", side_effect=PermissionError("locked")), \
                mock.patch.object(report_assets.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(PermissionError):
                report_assets.replace_file(stage, target)


class SharedChromeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.reports = pathlib.Path(self.temp.name) / "_reports"

    def test_banner_is_published_once_and_a_custom_banner_is_kept(self):
        with contextlib.redirect_stdout(io.StringIO()):
            target = gallery_chrome.publish_banner(self.reports)
        self.assertEqual(target, self.reports / "_assets" / gallery_chrome.BANNER_NAME)
        self.assertEqual(target.read_bytes(), gallery_chrome.BANNER_SOURCE.read_bytes())
        self.assertLess(target.stat().st_size, 120_000)
        target.write_bytes(b"user banner")
        with contextlib.redirect_stdout(io.StringIO()) as messages:
            gallery_chrome.publish_banner(self.reports)
        self.assertEqual(target.read_bytes(), b"user banner")
        self.assertIn("keeping the existing custom banner", messages.getvalue())
        self.assertEqual(sorted(p.name for p in target.parent.iterdir()), [gallery_chrome.BANNER_NAME])

    def test_masthead_links_are_relative_and_optional(self):
        page = gallery_chrome.masthead("Artists", "../", "Artist library")
        self.assertIn("../_assets/gallery-banner.jpg", page)
        self.assertIn('href="../library/people_gallery.html"', page)
        self.assertIn('href="../artists/artists_gallery.html" aria-current="page"', page)
        quiet = gallery_chrome.masthead(None, "../../", links=False)
        self.assertIn("../../_assets/gallery-banner.jpg", quiet)
        self.assertNotIn("<a ", quiet)
        self.assertNotIn("--st-banner", gallery_chrome.masthead("People", None))
        self.assertEqual(gallery_chrome.reports_prefix(self.reports / "library", self.reports), "../")
        self.assertEqual(gallery_chrome.reports_prefix(self.reports / "a" / "b", self.reports), "../../")

    def test_every_gallery_page_uses_the_shared_theme_first(self):
        pages = {
            "artists": gallery.page([], detail=False, stats="0 groups"),
            "people": people_gallery.render_html([], "now", {}).encode("utf-8"),
            "review": review_gallery.render_html([], "now").encode("utf-8"),
        }
        for name, page in pages.items():
            text = page.decode("utf-8")
            with self.subTest(name):
                self.assertIn("<style>" + gallery_chrome.CSS, text)
                self.assertIn('class="site-masthead"', text)
                self.assertIn('class="site-page"', text)
                self.assertIn('class="page-header"', text)
                self.assertIn("library-footer", text)
                self.assertEqual(text.count("<div"), text.count("</div>"))

    def test_mobile_menu_and_versioned_footer_are_shared_and_escaped(self):
        header = gallery_chrome.masthead("People", "../")
        self.assertIn('<details class="site-menu"><summary>Menu</summary>', header)
        self.assertIn('aria-label="Libraries menu"', header)
        self.assertEqual(header.count('href="../artists/artists_gallery.html"'), 2)
        self.assertNotIn('class="site-menu"', gallery_chrome.masthead(None, "../", links=False))
        footer = gallery_chrome.footer("<unsafe> & local")
        self.assertIn("Gallery UI v" + gallery_chrome.GALLERY_VERSION, footer)
        self.assertIn("&lt;unsafe&gt; &amp; local", footer)
        self.assertIn('href="#top"', footer)

    def test_gallery_badge_palette_has_one_owner(self):
        for selector in (
            ".category-sisters", ".category-angels", ".category-models",
            ".category-prospects", ".category-potentials",
            ".score-green", ".score-yellow", ".score-orange", ".score-red",
        ):
            with self.subTest(selector=selector):
                rule = r"(?:^|})\s*" + re.escape(selector) + r"\s*\{"
                self.assertEqual(len(re.findall(rule, gallery_chrome.CSS)), 1)
                for page_css in (gallery.CSS, people_gallery.CSS, review_gallery.CSS):
                    self.assertNotRegex(page_css, rule)
        self.assertIn("a:is(.badge,.category-badge,.score-badge,.history,.photo-count)", gallery_chrome.CSS)
        self.assertIn(".library-nav{position:sticky", gallery_chrome.CSS)
        self.assertIn("@media(max-width:760px),(max-height:500px){.library-nav{position:static}", gallery_chrome.CSS)

    def test_gallery_tiles_fit_below_their_preferred_width(self):
        self.assertIn("minmax(min(100%,300px),1fr)", people_gallery.CSS)
        self.assertIn("minmax(min(100%,var(--card-min)),1fr)", review_gallery.CSS)
        self.assertNotIn("white-space:nowrap", review_gallery.CSS)


if __name__ == "__main__":
    unittest.main()
