#!/usr/bin/env python3
"""Tests for the local photo-library people gallery."""
import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import people_gallery as gallery  # noqa: E402


class PeopleGalleryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.root = self.tmp / "library"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def add_person(self, status, name, count):
        folder = self.root / status / name
        photos = folder / "gallery"
        photos.mkdir(parents=True, exist_ok=True)
        for index in range(count):
            (photos / f"{name.lower().replace(' ', '_')}_{index:02}.jpg").write_bytes(b"photo")
        return f"{status}/{name}", folder

    def test_collect_limits_thumbnails_and_sorts_people_by_section_rules(self):
        people = [
            self.add_person("Angels", "Single", 1),
            self.add_person("Angels", "Zelda", 11),
            self.add_person("Angels", "Aster", 4),
            self.add_person("Sisters", "Zara", 11),
            self.add_person("Sisters", "Ayla", 4),
            self.add_person("Prospects", "Prospect", 2),
        ]
        with (
            mock.patch.object(gallery.likeness, "library_people", return_value=people),
            mock.patch.object(gallery.likeness, "status_of", side_effect=lambda key: key.split("/", 1)[0]),
            mock.patch.object(gallery, "thumb_bytes", return_value=b"thumbnail"),
        ):
            rows = gallery.collect({}, None, self.root, types.SimpleNamespace(by_key={}), ["Angels", "Sisters", "Prospects"])

        self.assertEqual(
            [(row["status"], row["folder"]) for row in rows],
            [("Sisters", "Ayla"), ("Sisters", "Zara"), ("Angels", "Aster"),
             ("Angels", "Single"), ("Angels", "Zelda"), ("Prospects", "Prospect")],
        )
        zelda = next(row for row in rows if row["folder"] == "Zelda")
        self.assertEqual(zelda["photos"], 11)
        self.assertEqual(len(zelda["gallery_photos"]), gallery.MAX_PHOTOS)
        self.assertEqual(zelda["gallery_photos"][0]["name"], zelda["source"])

    def test_prior_prospect_identity_is_shown_only_for_promoted_people(self):
        angel = self.root / "Angels" / "Nyxene"
        sister = self.root / "Sisters" / "Draknoxa"
        ordinary = self.root / "Angels" / "Angelica"
        for folder in (angel, sister, ordinary):
            (folder / "gallery").mkdir(parents=True)
        (angel / "gallery" / "z_sabine_vale.txt").write_text(
            "name: Sabine Vale\n2026-10-20 now the Angel Nyxene; promoted from Prospects\n",
            encoding="utf-8",
        )
        (sister / "gallery" / "z_sydney_sky.txt").write_text(
            "name: Sydney Sky\n2026-10-10 +4 from Prospects/Una Beck: merged from Prospects/Una Beck\n",
            encoding="utf-8",
        )
        (ordinary / "gallery" / "z_angelica.txt").write_text("name: Angelica\n", encoding="utf-8")

        self.assertEqual(gallery.prior_prospect_name(angel, "Angels"), "Sabine Vale")
        self.assertEqual(gallery.prior_prospect_name(sister, "Sisters"), "Sydney Sky")
        self.assertIsNone(gallery.prior_prospect_name(ordinary, "Angels"))

    def test_html_and_markdown_show_prospect_identity_after_chosen_label(self):
        folder = self.root / "Angels" / "Nyxene"
        (folder / "gallery").mkdir(parents=True)
        row = {
            "status": "Angels", "folder": "Nyxene", "photos": 1, "review": 0,
            "chosen": True, "prospect_name": "Sabine Vale", "score": 0.8,
            "source": "nyxene.jpg", "tags": {}, "gallery_path": folder / "gallery",
            "z_path": None, "gallery_photos": [],
        }
        html_output = gallery.render_html([row], "now", {"Angels": 1})
        self.assertIn("chosen source photo · Prospect identity: Sabine Vale", html_output)
        self.assertLess(html_output.index("chosen source photo"), html_output.index("Prospect identity"))

        md_output = gallery.render_md([row], "now", {"Angels": 1}, self.root / "files", "people_gallery.html")
        self.assertIn("chosen source photo · Prospect identity: Sabine Vale", md_output)

    def test_pairing_navigation_links_prospects_and_sorts_them_by_photo_count(self):
        sister = {"status": "Sisters", "folder": "Draknora", "photos": 0}
        best = {"status": "Prospects", "folder": "Best Fit", "photos": 6}
        next_fit = {"status": "Prospects", "folder": "Next Fit", "photos": 25}
        angel = {
            "status": "Angels",
            "folder": "Camaris",
            "paired_sister": "Draknora",
            "candidate_rankings": [
                {"name": "Best Fit", "cost": 0.05, "score": 0.28, "photos": 6},
                {"name": "Next Fit", "cost": 0.10, "score": 0.35, "photos": 25},
            ],
            "candidate_prospects": [
                {"name": "Best Fit", "cost": 0.05, "score": 0.28, "photos": 6},
                {"name": "Next Fit", "cost": 0.10, "score": 0.35, "photos": 25},
            ],
        }
        rows = [next_fit, angel, best, sister]

        gallery.add_pairing_navigation(rows)

        self.assertEqual([row["status"] for row in rows], ["Sisters", "Angels", "Prospects", "Prospects"])
        self.assertEqual(sister["paired_angel"], angel)
        self.assertEqual([item["name"] for item in sister["candidate_prospects"]], ["Best Fit", "Next Fit"])
        self.assertEqual([row["folder"] for row in rows if row["status"] == "Prospects"], ["Next Fit", "Best Fit"])
        self.assertEqual(best["best_angel_match"]["angel"], angel)
        self.assertEqual(best["best_angel_match"]["rank"], 1)

    def test_html_links_pairing_recommendations_between_sections(self):
        sister_path = self.root / "Sisters" / "Draknora" / "gallery"
        angel_path = self.root / "Angels" / "Camaris" / "gallery"
        prospect_path = self.root / "Prospects" / "Best Fit" / "gallery"
        sister_path.mkdir(parents=True)
        angel_path.mkdir(parents=True)
        prospect_path.mkdir(parents=True)
        prospect = {"name": "Best Fit", "cost": 0.03, "score": 0.28, "photos": 10,
                    "likeness_cost": 0.05, "photo_bonus": 0.02}
        sister = {
            "status": "Sisters", "folder": "Draknora", "photos": 0, "review": 0, "chosen": False, "score": None,
            "source": "", "tags": {}, "gallery_path": sister_path, "z_path": None, "gallery_photos": [],
            "paired_angel": {"folder": "Camaris"}, "candidate_prospects": [prospect],
        }
        angel = {
            "status": "Angels", "folder": "Camaris", "photos": 0, "review": 0, "chosen": False, "score": None,
            "source": "", "tags": {}, "gallery_path": angel_path, "z_path": None, "gallery_photos": [],
            "paired_sister": "Draknora", "hair_color": "", "candidate_prospects": [prospect],
            "candidate_rankings": [dict(prospect, cohesion=0.6)],
        }
        candidate = {
            "status": "Prospects", "folder": "Best Fit", "photos": 6, "review": 0, "chosen": False, "score": None,
            "source": "", "tags": {}, "gallery_path": prospect_path, "z_path": None, "gallery_photos": [],
            "usable": 0, "full_length": 0, "median_face_px": 0, "no_face": 0, "too_small": 0, "unreadable": 0,
            "sister_matches": [], "best_angel_match": {
                "angel": angel, "candidate": dict(prospect, cohesion=0.6), "rank": 1,
            },
        }

        output = gallery.render_html([sister, angel, candidate], "now", {"Sisters": 1, "Angels": 1, "Prospects": 1})

        self.assertIn('id="person-sisters-draknora"', output)
        self.assertIn('id="person-angels-camaris"', output)
        self.assertIn('id="person-prospects-best_fit"', output)
        self.assertIn('href="#person-angels-camaris">Camaris</a>', output)
        self.assertIn('href="#person-prospects-best_fit">Best Fit</a>', output)
        self.assertIn('href="#person-sisters-draknora">Draknora</a>', output)
        self.assertIn("Current Angel pairing:", output)
        self.assertIn("Top Prospect alternatives:", output)
        self.assertIn("Best Angel pairing fit:", output)

    def test_inspect_scores_full_length_from_face_size_and_clean_reel_bounds(self):
        from PIL import Image
        import screens

        photo = self.tmp / "photo.png"
        Image.new("RGB", (100, 2000)).save(photo)
        with mock.patch.object(screens, "is_reel_ui", return_value=False):
            self.assertEqual(gallery.inspect(photo, (0.4, 0.2, 0.1, 0.13)), (True, False))
            self.assertEqual(gallery.inspect(photo, (0.4, 0.2, 0.1, 0.15)), (False, False))

        with (
            mock.patch.object(screens, "is_reel_ui", return_value=True),
            mock.patch.object(screens, "head_clear", return_value=True),
            mock.patch.object(screens, "clean_box", return_value=(0, 200, 100, 1800)),
        ):
            self.assertEqual(gallery.inspect(photo, (0.4, 0.2, 0.1, 0.13)), (False, False))

        with (
            mock.patch.object(screens, "is_reel_ui", return_value=True),
            mock.patch.object(screens, "head_clear", return_value=False),
        ):
            self.assertEqual(gallery.inspect(photo, (0.4, 0.2, 0.1, 0.1)), (False, False))

    def test_html_links_photo_count_and_history_and_explains_prime_score(self):
        folder = self.root / "Prospects" / "Dara Ives"
        photo = folder / "gallery" / "dara_ives_01.jpg"
        history = folder / "gallery" / "z_dara_ives.txt"
        photo.parent.mkdir(parents=True)
        photo.write_bytes(b"photo")
        history.write_text("name: Dara Ives\n", encoding="utf-8")
        row = {
            "status": "Prospects",
            "folder": "Dara Ives",
            "photos": 1,
            "review": 0,
            "chosen": False,
            "score": 0.76,
            "source": photo.name,
            "tags": {"type": ["human"], "roles": ["artist", "mage"], "elements": ["Light"]},
            "gallery_path": photo.parent,
            "z_path": history,
            "gallery_photos": [{"name": photo.name, "path": photo, "thumb": b"thumbnail"}],
        }

        output = gallery.render_html([row], "now", {"Prospects": 1})

        self.assertIn('href="' + photo.resolve().as_uri() + '"', output)
        self.assertIn('href="' + photo.parent.resolve().as_uri() + '" title="Open this person\'s local gallery folder">Open folder', output)
        self.assertIn("1 photo", output)
        self.assertIn('href="' + history.resolve().as_uri() + '"', output)
        self.assertIn("Prime-start photo score 0.76", output)
        self.assertIn("photo suitability, not identity confidence", output)
        self.assertNotIn("best guess", output)
        self.assertIn("grid-template-columns:repeat(3", output)
        summary = gallery.profile_summary({"roles": ["one two three four five six seven"]})
        self.assertEqual(len(summary.split()), 6)
        self.assertTrue(summary.endswith("..."))

    def test_prospect_sister_matches_and_readiness_evidence_are_reported(self):
        _, folder = self.add_person("Prospects", "Dara Ives", 1)
        sister_vectors = {
            "Prospects/Dara Ives": np.array([1.0, 0.0]),
            "Sisters/Drak": np.array([0.8, 0.6]),
            "Sisters/Luna": np.array([0.2, 0.98]),
        }
        space = types.SimpleNamespace(
            by_key={},
            keys=["Sisters/Drak", "Sisters/Luna", "Prospects/Dara Ives"],
            centroid=lambda key: sister_vectors.get(key),
            photos=[],
        )
        with (
            mock.patch.object(gallery.likeness, "library_people", return_value=[("Prospects/Dara Ives", folder)]),
            mock.patch.object(gallery.likeness, "status_of", return_value="Prospects"),
            mock.patch.object(gallery, "thumb_bytes", return_value=b"thumbnail"),
        ):
            rows = gallery.collect({}, {}, self.root, space, ["Prospects"])

        matches = rows[0]["sister_matches"]
        self.assertEqual([item["name"] for item in matches], ["Drak", "Luna"])
        output = gallery.render_html(rows, "now", {"Prospects": 1})
        self.assertIn(
            'Closest sister matches (similarity): <a href="#person-sisters-drak">Drak</a> 0.80',
            output,
        )
        self.assertIn('<a href="#person-sisters-luna">Luna</a> 0.20', output)
        self.assertIn("Photo evidence: 0/1 usable faces", output)
        self.assertIn("does not estimate distinct poses", output)

    def test_angel_candidates_rank_by_fit_to_configured_sister_target_and_require_cohesion(self):
        vectors = {
            "Sisters/Drak": np.array([1.0, 0.0]),
            "Prospects/Best Fit": np.array([0.28, np.sqrt(1 - 0.28**2)]),
            "Prospects/Next Fit": np.array([0.40, np.sqrt(1 - 0.40**2)]),
            "Prospects/High Variety": np.array([0.30, np.sqrt(1 - 0.30**2)]),
            "Prospects/Low Cohesion": np.array([0.28, np.sqrt(1 - 0.28**2)]),
        }
        by_key = {
            "Sisters/Drak": [object()] * 5,
            "Prospects/Best Fit": [object()] * 6,
            "Prospects/Next Fit": [object()] * 5,
            "Prospects/High Variety": [object()] * 20,
            "Prospects/Low Cohesion": [object()] * 20,
        }
        space = types.SimpleNamespace(keys=list(by_key), by_key=by_key)

        def folder_core(_space, key, _identity):
            cohesion = 0.30 if key.endswith("Low Cohesion") else 0.60
            return by_key[key], [cohesion, cohesion], [], vectors[key]

        with (
            mock.patch.object(gallery.likeness, "identity", return_value={}),
            mock.patch.object(gallery.likeness, "folder_core", side_effect=folder_core),
            mock.patch.object(gallery.likeness, "identity_vec", side_effect=lambda core, _identity: core),
        ):
            ranked = gallery.angel_candidates(space, {}, {}, "Drak", limit=None)

        self.assertEqual([candidate["name"] for candidate in ranked], ["High Variety", "Best Fit", "Next Fit"])
        self.assertAlmostEqual(ranked[0]["score"], 0.30)
        self.assertEqual(ranked[0]["photo_bonus"], 0.06)
        self.assertAlmostEqual(ranked[0]["cost"], -0.04)

    def test_angel_card_shows_mapping_hair_alternatives_and_safe_promotion_command(self):
        folder = self.root / "Angels" / "Gavrielle"
        folder.mkdir(parents=True)
        row = {
            "status": "Angels",
            "folder": "Gavrielle",
            "photos": 0,
            "review": 0,
            "chosen": False,
            "score": None,
            "source": "",
            "tags": {},
            "gallery_path": folder / "gallery",
            "z_path": None,
            "gallery_photos": [],
            "paired_sister": "Draknava",
            "hair_color": "Soft golden-wheat blonde",
            "candidate_prospects": [{"name": "Esme Marsh", "score": 0.25, "cost": 0.03, "likeness_cost": 0.05, "photo_bonus": 0.02, "photos": 10}],
            "candidate_rankings": [{"name": "Esme Marsh", "score": 0.25, "photos": 10, "cohesion": 0.6, "likeness_cost": 0.05, "photo_bonus": 0.02, "cost": 0.03}],
        }

        output = gallery.render_html([row], "now", {"Angels": 1})

        self.assertIn('Paired Sister: <a href="#person-sisters-draknava">Draknava</a>', output)
        self.assertIn("Current hair: Soft golden-wheat blonde", output)
        self.assertIn('href="#person-prospects-esme_marsh">Esme Marsh</a> 1. adjusted fit 0.030 (likeness 0.050, +0.02 variety), 10 photos', output)
        self.assertIn('bin\\likeness.cmd promote &quot;Esme Marsh&quot; &quot;Gavrielle&quot;', output)
        self.assertIn("add <code>--apply</code> only after reviewing", output)
        self.assertIn("../comparisons/pairings/angel-prospect-candidates.md", output)

    def test_pairing_report_lists_the_full_ranked_candidate_set(self):
        angel = {
            "status": "Angels",
            "folder": "Gavrielle",
            "paired_sister": "Draknava",
            "hair_color": "Soft blonde",
            "candidate_rankings": [
                {"name": "Best Fit", "score": 0.28, "photos": 20, "cohesion": 0.61, "likeness_cost": 0.0, "photo_bonus": 0.06, "cost": -0.06},
                {"name": "Second Fit", "score": 0.34, "photos": 5, "cohesion": 0.56, "likeness_cost": 0.06, "photo_bonus": 0.0, "cost": 0.06},
            ],
        }

        report = gallery.render_pairing_report([angel], "now")

        self.assertIn("## Gavrielle → Draknava", report)
        self.assertIn("| 1 | Best Fit | 0.280 | 20 | 0.610 | 0.000 | 0.06 | -0.060 |", report)
        self.assertIn("| 2 | Second Fit | 0.340 | 5 | 0.560 | 0.060 | 0.00 | 0.060 |", report)

    def test_markdown_gallery_shows_pairing_recommendations_and_links_full_report(self):
        angel = {
            "status": "Angels",
            "folder": "Gavrielle",
            "photos": 1,
            "review": 0,
            "chosen": False,
            "score": None,
            "tags": {},
            "gallery_path": self.root / "Angels" / "Gavrielle" / "gallery",
            "z_path": None,
            "gallery_photos": [],
            "paired_sister": "Draknava",
            "candidate_prospects": [{
                "name": "Mara Carrington", "cost": -0.029, "likeness_cost": 0.031,
                "photo_bonus": 0.06, "photos": 20,
            }],
        }

        output = gallery.render_md([angel], "now", {"Angels": 1}, self.root / "files", "people_gallery.html")

        self.assertIn("Paired with Draknava", output)
        self.assertIn("Mara Carrington (adjusted -0.029, likeness 0.031, +0.06, 20 photos)", output)
        self.assertIn("[full rankings](../comparisons/pairings/angel-prospect-candidates.md)", output)


if __name__ == "__main__":
    unittest.main()
