"""Focused tests for the offline bounded reference-render gallery."""
import hashlib
import json
import pathlib
import tempfile
import unittest
import contextlib
import io
from html.parser import HTMLParser
from unittest import mock
from urllib.parse import urljoin

from PIL import Image

from tools.workflows import reference_gallery as gallery


class _ChromeParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                 "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, page):
        super().__init__()
        self.nodes = []
        self.stack = []
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "parents": tuple(self.stack)}
        self.nodes.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break

    def with_class(self, name):
        return [node for node in self.nodes
                if name in node["attrs"].get("class", "").split()]


class SharedGalleryChromeTests(unittest.TestCase):
    def pages(self):
        import artists_gallery
        import people_gallery
        from likeness_library import review_gallery
        from tools.workflows import reference_comparison, reference_outputs

        root = gallery.ROOT / ".gallery-chrome-fixture"
        return [
            ("_reports/library/people_gallery.html", "People",
             people_gallery.render_html([], "now", {})),
            ("_reports/library/people_gallery_review.html", "People",
             review_gallery.render_html([], "now")),
            *[("_reports/artists/" + filename, "Artists",
               artists_gallery.page([], detail=detail, stats="Empty fixture").decode("utf-8"))
              for filename, detail in (("artists_gallery.html", False),
                                       ("artists_gallery_review.html", True))],
            ("_generation/index.html", "Rendering", gallery.build_page(root, [], [])),
            ("_generation/outputs.html", "Outputs",
             reference_outputs.build_page(root, root / "ComfyUI Outputs", [], [])),
            ("_generation/comparison.html", "Comparison",
             reference_comparison._page(root, [], [])),
        ]

    def test_all_main_pages_keep_shared_chrome_in_the_same_layout(self):
        for filename, section, page in self.pages():
            with self.subTest(page=filename):
                dom = _ChromeParser(page)
                self.assertEqual(page.count(gallery.gallery_chrome.CSS), 1)
                self.assertEqual(len(dom.with_class("site-masthead")), 1)
                self.assertEqual(len(dom.with_class("site-page")), 1)
                self.assertEqual(len(dom.with_class("library-footer")), 1)
                frame = dom.with_class("site-page")[0]
                footer = dom.with_class("library-footer")[0]
                masthead = dom.with_class("site-masthead")[0]
                self.assertIs(footer["parents"][-1], frame)
                self.assertEqual(masthead["parents"][-1]["tag"], "body")
                self.assertEqual(len(dom.with_class("footer-brand")), 1)
                self.assertIn(f"Gallery UI v{gallery.gallery_chrome.GALLERY_VERSION}", page)
                self.assertTrue(any(node["tag"] == "a"
                                    and node["attrs"].get("href") == "#top"
                                    and footer in node["parents"] for node in dom.nodes))
                self.assertEqual(len(dom.with_class("site-menu")), 1)
                self.assertIn('<summary>Menu</summary>', page)
                self.assertIn(f'aria-current="page">{section}</a>', page)

    def test_masthead_navigation_and_banner_resolve_from_each_page(self):
        for filename, section, page in self.pages():
            with self.subTest(page=filename):
                dom = _ChromeParser(page)
                origin = "file:///library/" + filename
                expected = {
                    "file:///library/_reports/library/people_gallery.html",
                    "file:///library/_reports/artists/artists_gallery.html",
                    "file:///library/_generation/index.html",
                    "file:///library/_generation/outputs.html",
                    "file:///library/_generation/comparison.html",
                }
                for nav in dom.with_class("site-sections"):
                    links = [node for node in dom.nodes
                             if node["tag"] == "a" and node["parents"][-1] is nav]
                    self.assertEqual({urljoin(origin, link["attrs"]["href"]) for link in links},
                                     expected)
                    active = [link for link in links
                              if link["attrs"].get("aria-current") == "page"]
                    self.assertEqual(len(active), 1)
                    active_target = {
                        "People": "_reports/library/people_gallery.html",
                        "Artists": "_reports/artists/artists_gallery.html",
                        "Rendering": "_generation/index.html",
                        "Outputs": "_generation/outputs.html",
                        "Comparison": "_generation/comparison.html",
                    }[section]
                    self.assertEqual(urljoin(origin, active[0]["attrs"]["href"]),
                                     "file:///library/" + active_target)
                    self.assertEqual([link["attrs"]["href"].rsplit("/", 1)[-1] for link in links],
                                     ["people_gallery.html", "artists_gallery.html",
                                      "index.html", "outputs.html", "comparison.html"])
                masthead = dom.with_class("site-masthead")[0]
                banner = masthead["attrs"]["style"].split('url("')[1].split('")')[0]
                self.assertEqual(urljoin(origin, banner),
                                 "file:///library/_reports/_assets/gallery-banner.jpg")


class ReferenceGalleryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.sources = []
        for index in range(4):
            relative = f"Various/gallery/source-{index}.png"
            path = self.root / pathlib.Path(*relative.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f"image bytes {index}".encode()
            path.write_bytes(data)
            self.sources.append({
                "path": relative,
                "sha256": hashlib.sha256(data).hexdigest(),
                "domain": "general",
                "displayName": f"Source {index}",
                "personId": "person-1",
            })
        self.recipes = [
            {"id": "manual-0c-cleanup-basic", "label": "0c Cleanup Basic",
             "stage": "0_Edit", "available": True},
            {"id": "manual-0c-cleanup", "label": "0c Cleanup",
             "stage": "0_Edit", "available": True},
            {"id": "manual-0e-enhance", "label": "0e Enhance",
             "stage": "0_Edit", "available": True},
            {"id": "manual-0f-full", "label": "0f Full",
             "stage": "0_Edit", "available": True},
            {"id": "pending-0d_deluxe", "label": "0d Deluxe",
             "stage": "0_Edit", "available": False, "prompt": "Do not display this prompt"},
            {"id": "pending-a-pose", "label": "A-pose",
             "stage": "1_Alpha", "available": False,
             "reason": "Template migration pending; must not leak prompt text"},
            {"id": "pending-studies", "label": "Studies",
             "stage": "2_Studies", "available": False},
            {"id": "pending-optional_diagnostics", "label": "Optional diagnostics",
             "stage": "Bench", "available": False},
        ]

    def test_display_metadata_is_escaped_and_names_are_not_guessed(self):
        source = dict(self.sources[0], displayName='</script><img src=x onerror="alert(1)">')
        page = gallery.build_page(self.root, [source], self.recipes)

        self.assertNotIn('</script><img', page)
        self.assertIn("\\u003c/script\\u003e", page)
        self.assertIn("Various/gallery/source-0.png", page)
        self.assertIn("Unnamed source", gallery.build_page(
            self.root, [dict(source, displayName=None)], self.recipes
        ))

    def test_source_path_traversal_and_domain_mismatch_are_refused(self):
        for path in ("../secret.png", "Various/gallery/../secret.png",
                     "_generation/gallery/image.png", "Various\\gallery\\image.png"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                gallery.build_page(self.root, [dict(self.sources[0], path=path)], self.recipes)
        with self.assertRaisesRegex(ValueError, "domain mismatch"):
            gallery.build_page(
                self.root, [dict(self.sources[0], path="Artists/House/gallery/photo.png")],
                self.recipes,
            )

    def test_recipe_stage_filtering_and_disabled_capability_are_visible(self):
        page = gallery.build_page(self.root, self.sources, self.recipes)

        self.assertIn('data-stage="0_Edit"', page)
        self.assertIn('data-stage="1_Alpha"', page)
        self.assertIn('>A-pose [target recipe]', page)
        self.assertIn('>Studies [target recipe]', page)
        self.assertIn('>0d Deluxe [target recipe]', page)
        self.assertIn('>Optional diagnostics [target recipe]', page)
        self.assertIn("data-available=\"false\" disabled", page)
        self.assertIn("group.dataset.stage !== stage", page)
        self.assertIn("provisional clothed transport pilot; not exact manual prompt migration", page)
        self.assertIn("Manual source prompts may contain contradictory instructions and are never", page)
        self.assertIn("Per-job appearance-profile changes and other Prime/Studies execution remain unavailable", page)
        self.assertNotIn("Do not display this prompt", page)
        self.assertNotIn("must not leak prompt text", page)
        self.assertIn("Four coordinated tracks", page)
        self.assertIn("stage/template migration", page)
        request = gallery.make_request(self.root, self.sources, self.recipes[0], 2, "gallery-test")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            gallery.make_request(self.root, self.sources, self.recipes[4], 2, "gallery-test")

    def test_shared_cleanup_basic_is_selectable_and_preserves_request_id(self):
        recipe = {"id": "shared-0c-cleanup-basic", "label": "catalogue label",
                  "stage": "0_Edit", "available": True}
        cleaned = gallery._validate_recipes([recipe])[0]
        self.assertEqual(cleaned["label"], "0c Cleanup Basic (shared)")
        self.assertTrue(cleaned["available"])
        self.assertEqual(cleaned["promptPolicy"], "shared-clothed-reference-v1")
        page = gallery.build_page(self.root, self.sources[:1], [recipe])
        self.assertIn('value="shared-0c-cleanup-basic" data-available="true"', page)
        request = gallery.make_request(self.root, self.sources[:1], recipe, 1, "cleanup-basic-test")
        self.assertEqual(request["jobs"][0]["recipe"], recipe["id"])
        self.assertFalse(gallery._validate_recipes([dict(recipe, stage="1_Alpha")])[0]["available"])

    def test_shared_pose_entries_show_generated_prompt_policy(self):
        recipes = [
            {"id": recipe_id, "label": "unused label", "stage": "0_Edit", "available": True}
            for recipe_id in ("shared-0d-relaxed-three-quarter", "shared-0d-grounded-three-quarter")
        ]
        page = gallery.build_page(self.root, self.sources, recipes)
        self.assertIn("0d Legacy studio pose pilot relaxed 3/4 (shared, clothed)", page)
        self.assertIn("0d Legacy studio pose pilot forward-foot 3/4 (shared, clothed)", page)
        self.assertIn("shared templates/JSON; inspected Qwen transport", page)
        self.assertIn("shared-clothed-reference-v1", page)

    def test_bedroom_deluxe_recipes_are_selectable_in_edit_and_keep_request_ids(self):
        for pose in ("seated", "relaxing", "side-resting", "resting"):
            recipe_id = f"shared-0d-deluxe-{pose}"
            recipe = {"id": recipe_id, "label": "catalogue label", "stage": "0_Edit",
                      "available": True}
            with self.subTest(recipe=recipe_id):
                cleaned = gallery._validate_recipes([recipe])[0]
                self.assertEqual(cleaned["id"], recipe_id)
                self.assertEqual(cleaned["label"], f"Bedroom {pose} (shared, clothed)")
                self.assertTrue(cleaned["available"])
                self.assertEqual(cleaned["stage"], "0_Edit")
                page = gallery.build_page(self.root, self.sources[:1], [recipe])
                self.assertIn(f'value="{recipe_id}" data-available="true"', page)
                request = gallery.make_request(self.root, self.sources[:1], recipe, 1, "bedroom-test")
                self.assertEqual(request["jobs"][0]["recipe"], recipe_id)
                self.assertFalse(gallery._validate_recipes([dict(recipe, stage="1_Alpha")])[0]["available"])

    def test_prime_outfit_recipes_are_selectable_only_in_alpha_and_keep_request_ids(self):
        recipes = [
            {"id": recipe_id, "label": "catalogue label", "stage": "1_Alpha", "available": True}
            for recipe_id in ("shared-1a-prime-outfit-relaxed", "shared-1a-prime-outfit-grounded")
        ]
        page = gallery.build_page(self.root, self.sources, recipes)
        self.assertIn("Prime outfit relaxed (shared, clothed)", page)
        self.assertIn("Prime outfit forward-foot (shared, clothed)", page)
        self.assertIn('<fieldset class="recipe-group" data-stage="1_Alpha">', page)
        for recipe in recipes:
            with self.subTest(recipe=recipe["id"]):
                self.assertIn(f'value="{recipe["id"]}" data-available="true"', page)
                request = gallery.make_request(self.root, self.sources[:1], recipe, 1, "prime-test")
                self.assertEqual(request["jobs"][0]["recipe"], recipe["id"])
                self.assertEqual(request["jobs"][0]["source"]["path"], self.sources[0]["path"])
                self.assertFalse(gallery._validate_recipes([dict(recipe, stage="0_Edit")])[0]["available"])

    def test_legacy_studio_pilots_keep_ids_and_supported_status_without_deluxe_claim(self):
        for recipe_id in ("manual-0d-deluxe-pose", "shared-0d-relaxed-three-quarter",
                          "shared-0d-grounded-three-quarter"):
            with self.subTest(recipe=recipe_id):
                recipe = {"id": recipe_id, "label": "Old Deluxe claim", "stage": "0_Edit",
                          "available": True}
                cleaned = gallery._validate_recipes([recipe])[0]
                self.assertEqual(cleaned["id"], recipe_id)
                self.assertTrue(cleaned["available"])
                self.assertIn("Legacy studio pose pilot", cleaned["label"])
                self.assertNotIn("Deluxe", cleaned["label"])
                request = gallery.make_request(self.root, self.sources[:1], recipe, 1, "legacy-test")
                self.assertEqual(request["jobs"][0]["recipe"], recipe_id)
                self.assertFalse(gallery._validate_recipes([dict(recipe, stage="1_Alpha")])[0]["available"])

    def test_one_source_expands_samples_deterministically_and_rechecks_hashes(self):
        recipe = self.recipes[0]
        request = gallery.make_request(
            self.root, self.sources[:1], recipe, 2, "gallery-test", seeds=[17, 29]
        )

        self.assertEqual(request["schemaVersion"], 1)
        self.assertEqual(request["batchId"], "gallery-test")
        self.assertEqual(request["workspace"], "Sovereign Females")
        self.assertEqual(len(request["jobs"]), 2)
        self.assertEqual(request["jobs"][0], {
            "id": "job-01",
            "source": {
                "path": self.sources[0]["path"],
                "sha256": self.sources[0]["sha256"],
                "domain": "general",
            },
            "workflowMode": "reference",
            "recipe": "manual-0c-cleanup-basic",
            "profile": "reference-faithful",
            "seed": 17,
            "displayName": "Source 0",
            "personId": "person-1",
        })
        with self.assertRaisesRegex(ValueError, "at least one source"):
            gallery.make_request(self.root, [], recipe, 8, "gallery-test")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            gallery.make_request(self.root, self.sources, self.recipes[-1], 2, "gallery-test")

        (self.root / pathlib.Path(*self.sources[0]["path"].split("/"))).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "hash changed"):
            gallery.make_request(self.root, self.sources[:1], recipe, 2, "gallery-test")

    def test_all_selected_sources_expand_and_64_job_cap_is_never_truncated(self):
        request = gallery.make_request(
            self.root, self.sources[:2], self.recipes[0], 4, "gallery-test",
            seeds=list(range(8)),
        )
        self.assertEqual(len(request["jobs"]), 8)
        self.assertEqual([job["id"] for job in request["jobs"]],
                         [f"job-{index:02d}" for index in range(1, 9)])
        self.assertEqual([job["source"]["path"] for job in request["jobs"]],
                         [self.sources[0]["path"]] * 4 + [self.sources[1]["path"]] * 4)
        with self.assertRaisesRegex(ValueError, "would create 128"):
            gallery.make_request(self.root, self.sources, self.recipes[:2], 16, "gallery-test")
        page = gallery.build_page(self.root, self.sources, self.recipes)
        self.assertIn("A batch is capped at 64 jobs", page)
        self.assertIn("Samples per workflow", page)
        self.assertIn("2 samples/workflow", page)
        self.assertIn("Every selected source is expanded in display order, then workflow", page)
        self.assertIn("for (const source of chosen) for (const recipe of chosenRecipes)", page)
        self.assertIn("jobs > 64", page)

    def test_multiple_recipes_expand_source_recipe_sample_order(self):
        request = gallery.make_request(
            self.root, self.sources[:2], self.recipes[:2], 1, "gallery-multi", seeds=[1, 2, 3, 4],
        )
        self.assertEqual([(job["source"]["path"], job["recipe"]) for job in request["jobs"]], [
            (self.sources[0]["path"], "manual-0c-cleanup-basic"),
            (self.sources[0]["path"], "manual-0c-cleanup"),
            (self.sources[1]["path"], "manual-0c-cleanup-basic"),
            (self.sources[1]["path"], "manual-0c-cleanup"),
        ])
        with self.assertRaisesRegex(ValueError, "unavailable"):
            gallery.make_request(self.root, self.sources[:1], [self.recipes[0], self.recipes[4]], 1, "gallery-multi")

    def test_cleanup_hints_filter_select_all_and_reject_unknown_hint(self):
        hinted = [dict(self.sources[0], cleanup="needs-cleanup"), dict(self.sources[1], cleanup="repainted"),
                  self.sources[2]]
        page = gallery.build_page(self.root, hinted, self.recipes)
        self.assertIn('class="hint hint-needs-cleanup"', page)
        self.assertIn("Needs cleanup (overlay left)", page)
        self.assertIn('id="cleanup-filter"', page)
        self.assertIn('id="select-visible"', page)
        self.assertIn('id="clear-selection"', page)
        self.assertIn(".source-card:not([hidden]) .source-choice:not(:disabled)", page)
        with self.assertRaisesRegex(ValueError, "Unknown cleanup hint"):
            gallery.build_page(self.root, [dict(self.sources[0], cleanup="guess")], self.recipes)

    def test_selected_render_preserves_kind_and_requires_retained_provenance(self):
        relative = "_generation/selected/source-batch/job-01/selected.png"
        path = self.root.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True)
        Image.new("RGB", (8, 8), "blue").save(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        sidecar = path.with_suffix(".png.json")
        provenance = {
            "synthetic": True, "identityCoreEligible": False,
            "sha256": digest, "batchId": "source-batch", "jobId": "job-01",
            "domain": "artists",
        }
        source = {
            "path": relative, "kind": "selected-render", "sha256": digest,
            "domain": "artists", "displayName": "Authoritative Name", "personId": "person-2",
        }
        with self.assertRaisesRegex(ValueError, "held"):
            gallery.build_page(self.root, [source], self.recipes)
        sidecar.write_text(json.dumps(provenance), encoding="utf-8")
        page = gallery.build_page(self.root, [source], self.recipes)
        self.assertIn("Synthetic selected render", page)
        self.assertIn("Never an identity original", page)
        self.assertIn("if (source.kind !== undefined) job.source.kind = source.kind", page)
        request = gallery.make_request(
            self.root, [source], self.recipes[0], 2, "next-stage"
        )
        self.assertEqual(request["jobs"][0]["source"], {
            "path": relative, "sha256": digest, "domain": "artists", "kind": "selected-render",
        })
        self.assertEqual(request["jobs"][1]["personId"], "person-2")
        with self.assertRaises(ValueError):
            gallery.build_page(self.root, [dict(source, path=
                "_generation/selected/source-batch/job-01/../selected.png")], self.recipes)
        provenance["identityCoreEligible"] = True
        sidecar.write_text(json.dumps(provenance), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "held"):
            gallery.make_request(self.root, [source], self.recipes[0], 2, "next-stage")

    def test_source_query_prefills_card_and_source_search_is_non_destructive(self):
        page = gallery.build_page(self.root, self.sources, self.recipes)
        self.assertIn('new URLSearchParams(window.location.search).get("source")', page)
        self.assertIn("source.path === requestedSource", page)
        self.assertIn("card.classList.add(\"is-deep-link\")", page)
        self.assertIn('id="source-filter"', page)
        self.assertIn("searchable.includes(query)", page)
        self.assertIn("Every selected source is expanded", page)

    def test_execution_receipts_link_existing_outputs_and_mark_missing_files(self):
        output = self.root / "ComfyUI Outputs" / "render one.png"
        output.parent.mkdir(parents=True)
        output.write_bytes(b"rendered")
        output_hash = hashlib.sha256(output.read_bytes()).hexdigest()
        batch = self.root / "_generation" / "reference" / "render-batch"
        batch.mkdir(parents=True)
        request = {
            "schemaVersion": 1,
            "batchId": "render-batch",
            "workspace": "Sovereign Females",
            "jobs": [
                {
                    "id": "job-01", "displayName": "Gallery Name",
                    "source": {key: self.sources[0][key] for key in ("path", "sha256", "domain")},
                    "recipe": "manual-0c-cleanup-basic", "seed": 55,
                },
                {
                    "id": "job-02", "displayName": "Second",
                    "source": {key: self.sources[1][key] for key in ("path", "sha256", "domain")},
                    "recipe": "manual-0f-full", "seed": 66,
                },
            ],
        }
        execution = {
            "schemaVersion": 1,
            "batchId": "render-batch",
            "endpoint": "http://127.0.0.1:8188",
            "inputRoot": r"C:\ComfyUI\Input",
            "outputRoot": str(output.parent),
            "jobs": {
                "job-01": {
                    "state": "completed",
                    "promptId": "prompt-1",
                    "promptPolicy": "clothed-preservation-pilot-v1",
                    "promptOverride": "SECRET ORIGINAL PROMPT MUST NOT BE COPIED",
                    "outputs": [{
                        "filename": output.name, "subfolder": "", "type": "output",
                        "path": str(output), "sha256": output_hash,
                    }],
                },
                "job-02": {
                    "state": "completed",
                    "outputs": [{
                        "filename": "missing.png", "subfolder": "", "type": "output",
                        "path": str(output.parent / "missing.png"), "sha256": "f" * 64,
                    }],
                },
            },
        }
        (batch / "request.json").write_text(json.dumps(request), encoding="utf-8")
        (batch / "execution.json").write_text(json.dumps(execution), encoding="utf-8")
        historical = batch / "jobs" / "job-01" / "input" / "source.png"
        historical.parent.mkdir(parents=True)
        historical.write_bytes((self.root / pathlib.Path(*self.sources[0]["path"].split("/"))).read_bytes())
        (batch / "run.json").write_text(json.dumps({
            "jobs": [{"id": "job-01", "input": "jobs/job-01/input/source.png"},
                     {"id": "job-02", "input": "jobs/job-02/input/source.png"}]
        }), encoding="utf-8")

        original = self.root / pathlib.Path(*self.sources[0]["path"].split("/"))
        original.rename(original.with_name("moved-source.png"))
        page = gallery.build_page(self.root, self.sources, self.recipes)

        self.assertIn("Gallery Name", page)
        self.assertIn("clothed-preservation-pilot-v1", page)
        self.assertIn("Pilot prompt override recorded; text withheld.", page)
        self.assertNotIn("SECRET ORIGINAL PROMPT MUST NOT BE COPIED", page)
        self.assertIn(output.as_uri(), page)
        self.assertIn("Output file missing", page)
        self.assertIn("reference-promotion-manifest.json", page)
        self.assertIn("outputSha256", page)
        self.assertIn("does not promote or retain files", page)
        self.assertIn("reference/render-batch/jobs/job-01/input/source.png", page)
        self.assertIn("View historical prepared input snapshot", page)

    def test_execution_receipt_diagnostics_distinguish_prepared_and_corrupt_batches(self):
        missing = self.root / "_generation" / "reference" / "receipt-missing"
        prepared = self.root / "_generation" / "reference" / "receipt-prepared"
        corrupt = self.root / "_generation" / "reference" / "receipt-corrupt"
        missing.mkdir(parents=True)
        (missing / "request.json").write_text("{}", encoding="utf-8")
        prepared.mkdir(parents=True)
        (prepared / "request.json").write_text("{}", encoding="utf-8")
        (prepared / "run.json").write_text(json.dumps({
            "state": "inputs-only-not-render-ready",
        }), encoding="utf-8")
        corrupt.mkdir()
        (corrupt / "request.json").write_text('{"batchId":"receipt-corrupt","jobs":[]}', encoding="utf-8")
        (corrupt / "execution.json").write_text(
            '{"promptOverride":"PRIVATE TEXT MUST NOT LEAK"', encoding="utf-8"
        )
        page = gallery.build_page(self.root, self.sources, self.recipes)
        self.assertIn("receipt-missing", page)
        self.assertIn("Missing execution.json receipt", page)
        self.assertIn("receipt-prepared", page)
        self.assertIn("Inputs prepared; no executable receipt yet", page)
        self.assertIn("receipt-corrupt", page)
        self.assertIn("Unreadable or corrupt batch metadata JSON", page)
        self.assertNotIn("PRIVATE TEXT MUST NOT LEAK", page)

    def test_gallery_chrome_and_reports_navigation_are_shared(self):
        page = gallery.build_page(self.root, self.sources, self.recipes)
        self.assertIn(gallery.gallery_chrome.CSS, page)
        self.assertIn('aria-current="page">Rendering</a>', page)
        self.assertIn("../_reports/library/people_gallery.html", page)
        self.assertIn("../_reports/artists/artists_gallery.html", page)
        self.assertIn("CLI retention command:", page)
        self.assertNotIn("Planned retention form:", page)
        self.assertIn("gallery_chrome.reports_prefix", pathlib.Path(gallery.__file__).read_text())

    def test_cli_dry_run_apply_and_check_use_only_the_index_page(self):
        catalog_path = self.root / "catalog.json"
        sources_path = self.root / "sources.json"
        catalog_path.write_text(json.dumps({"recipes": self.recipes}), encoding="utf-8")
        sources_path.write_text(json.dumps({"sources": self.sources}), encoding="utf-8")
        args = ["--root", str(self.root), "--catalog", str(catalog_path),
                "--sources", str(sources_path)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gallery.main([*args, "--dry-run"]), 0)
        output = self.root / "_generation" / "index.html"
        self.assertFalse(output.exists())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gallery.main([*args, "--apply"]), 0)
            self.assertEqual(gallery.main([*args, "--check"]), 0)
        self.assertTrue(output.is_file())
        self.assertFalse((self.root / "_generation" / "reference").exists())
        with mock.patch.object(gallery.reference_execution, "catalog", return_value=self.recipes) as catalog, \
                mock.patch.object(gallery.reference_execution, "gallery_sources", return_value=self.sources) as discovery, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gallery.main(["--root", str(self.root), "--dry-run"]), 0)
        catalog.assert_called_once_with()
        discovery.assert_called_once_with(self.root.resolve())

    def test_configured_storage_roots_route_gallery_output_and_navigation(self):
        config = gallery.cw.load_cfg()
        config = {
            **config,
            "storageRoots": {
                **config["storageRoots"],
                "generation": "_generated",
                "reports": "_history",
            },
        }
        catalog_path = self.root / "catalog.json"
        sources_path = self.root / "sources.json"
        catalog_path.write_text(json.dumps({"recipes": self.recipes}), encoding="utf-8")
        sources_path.write_text(json.dumps({"sources": self.sources}), encoding="utf-8")
        args = ["--root", str(self.root), "--catalog", str(catalog_path),
                "--sources", str(sources_path), "--apply"]
        with mock.patch.object(gallery.cw, "load_cfg", return_value=config), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gallery.main(args), 0)
        output = self.root / "_generated" / "index.html"
        self.assertTrue(output.is_file())
        page = output.read_text(encoding="utf-8")
        self.assertIn("../_history/library/people_gallery.html", page)
        self.assertIn("../_history/artists/artists_gallery.html", page)
        self.assertFalse((self.root / "_generation").exists())

    def test_failed_gallery_publication_preserves_previous_whole_page(self):
        output = self.root / "_generation" / "index.html"
        output.parent.mkdir(parents=True)
        output.write_text("previous whole page", encoding="utf-8")
        with mock.patch.object(gallery.reference_execution, "catalog", return_value=self.recipes), \
                mock.patch.object(gallery.reference_execution, "gallery_sources", return_value=self.sources), \
                mock.patch.object(gallery.report_assets, "replace_file", side_effect=PermissionError("locked")), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gallery.main(["--root", str(self.root), "--apply"]), 1)
        self.assertEqual(output.read_text(encoding="utf-8"), "previous whole page")
        temporary_root = gallery.cw.storage_root(gallery.cw.load_cfg(), "temporary", root=self.root)
        self.assertEqual(list(temporary_root.glob(".render-gallery-*")), [])

    def test_build_page_does_not_guess_display_name_from_filename(self):
        source = dict(self.sources[0], displayName=None, personId=None)
        page = gallery.build_page(self.root, [source], self.recipes)
        self.assertIn("Unnamed source", page)
        self.assertNotIn("<h3>source-0.png</h3>", page)


if __name__ == "__main__":
    unittest.main()
