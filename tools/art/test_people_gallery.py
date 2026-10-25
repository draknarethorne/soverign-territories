#!/usr/bin/env python3
"""Tests for the local photo-library people gallery."""
import pathlib
import copy
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import people_gallery as gallery  # noqa: E402
from likeness_library.policy import validate_policy  # noqa: E402


class PeopleGalleryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.root = self.tmp / "library"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_models_are_a_distinct_active_category_not_a_sister_alias(self):
        self.assertEqual(gallery.likeness.status_of("Models/Freya"), "Models")
        self.assertFalse(gallery.likeness.is_sister("Models/Freya"))

    def test_identity_rankings_follow_library_hierarchy_then_similarity(self):
        vectors = {
            "Angels/Camaris": np.array([1.0, 0.0]),
            "Sisters/Draknora": np.array([0.8, 0.6]),
            "Models/Freya": np.array([0.8, 0.6]),
            "Artists/Portrait House/Freya": np.array([0.0, 1.0]),
            "Prospects/Una": np.array([-1.0, 0.0]),
        }
        space = types.SimpleNamespace(centroid=vectors.get)

        rankings = gallery.rank_identity_centroids(space, list(vectors))

        matches = rankings["Angels/Camaris"]
        self.assertEqual(
            [(match["category"], match["name"]) for match in matches],
            [
                ("Sisters", "Draknora"),
                ("Models", "Freya"),
                ("Prospects", "Una"),
                ("Artists", "Portrait House/Freya"),
            ],
        )
        self.assertEqual([match["score"] for match in matches], [0.8, 0.8, -1.0, 0.0])
        self.assertEqual(
            [match["category"] for match in rankings["Prospects/Una"]],
            ["Sisters", "Angels", "Models", "Artists"],
        )
        legacy_categories = gallery.rank_identity_centroids(
            space, list(vectors), categories={"Models/Freya": "Sisters"}
        )
        self.assertEqual(legacy_categories["Angels/Camaris"][0]["category"], "Sisters")

    def test_identity_rankings_sort_by_similarity_inside_each_category(self):
        vectors = {
            "Prospects/Focus": np.array([1.0, 0.0]),
            "Sisters/Lower": np.array([0.2, np.sqrt(1 - 0.2**2)]),
            "Sisters/Higher": np.array([0.8, np.sqrt(1 - 0.8**2)]),
            "Angels/Pair": np.array([0.95, np.sqrt(1 - 0.95**2)]),
        }
        ranked = gallery.rank_identity_centroids(
            types.SimpleNamespace(centroid=vectors.get), ["Prospects/Focus", "Sisters/Lower", "Sisters/Higher", "Angels/Pair"]
        )["Prospects/Focus"]

        self.assertEqual(
            [(match["category"], match["name"]) for match in ranked],
            [("Sisters", "Higher"), ("Sisters", "Lower"), ("Angels", "Pair")],
        )

    def test_custom_policy_category_is_rendered_and_controls_ranking_order(self):
        policy = copy.deepcopy(gallery.default_policy())
        policy["categoryOrder"].insert(3, "Demons")
        policy["categoryPolicies"]["Demons"] = copy.deepcopy(
            policy["categoryPolicies"]["Prospects"]
        )
        validate_policy(policy)

        page = gallery.render_html([], "now", {"Demons": 1}, policy=policy)
        self.assertIn('href="#demons">Demons (1)', page)

        rankings = gallery.rank_identity_centroids(
            None,
            ["Prospects/A", "Demons/B"],
            categories={"Prospects/A": "Prospects", "Demons/B": "Demons"},
            centroids={
                "Prospects/A": np.array([0.99, 0.1]),
                "Demons/B": np.array([1.0, 0.0]),
            },
            category_order=policy["categoryOrder"],
        )
        self.assertEqual(rankings["Prospects/A"][0]["category"], "Demons")

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
            self.add_person("Models", "Freya", 8),
            self.add_person("Sisters", "Zara", 11),
            self.add_person("Sisters", "Ayla", 4),
            self.add_person("Prospects", "Prospect", 2),
        ]
        with (
            mock.patch.object(gallery.likeness, "library_people", return_value=people),
            mock.patch.object(gallery.likeness, "status_of", side_effect=lambda key: key.split("/", 1)[0]),
            mock.patch.object(gallery, "thumb_bytes", return_value=b"thumbnail"),
        ):
            rows = gallery.collect(
                {}, None, self.root, types.SimpleNamespace(by_key={}),
                ["Angels", "Sisters", "Models", "Prospects"],
            )

        self.assertEqual(
            [(row["status"], row["folder"]) for row in rows],
            [("Sisters", "Ayla"), ("Sisters", "Zara"), ("Angels", "Aster"),
             ("Angels", "Single"), ("Angels", "Zelda"), ("Models", "Freya"),
             ("Prospects", "Prospect")],
        )
        zelda = next(row for row in rows if row["folder"] == "Zelda")
        self.assertEqual(zelda["photos"], 11)
        self.assertEqual(len(zelda["gallery_photos"]), gallery.MAX_PHOTOS)
        self.assertEqual(zelda["gallery_photos"][0]["name"], zelda["source"])

    def test_top_nine_use_shared_identity_priority_or_identity_score(self):
        photos = [types.SimpleNamespace(name=f"photo_{index:02}.jpg") for index in range(12)]
        scores = {photo.name: index / 10 for index, photo in enumerate(photos)}
        identity_scores = {photo.name: index / 20 for index, photo in enumerate(photos)}
        priorities = {
            photo.name: gallery.identity_order_key(index < 2, 2 <= index < 5, identity_scores[photo.name], photo.name)
            for index, photo in enumerate(photos)
        }
        ranked = gallery.top_gallery_photos(
            photos, scores, identity_scores=identity_scores, priorities=priorities
        )
        score_ranked = gallery.top_gallery_photos(
            photos, scores, identity_scores=identity_scores, priorities=priorities, sort_mode="score"
        )
        self.assertEqual(
            [photo.name for photo in ranked],
            ["photo_01.jpg", "photo_00.jpg", "photo_04.jpg", "photo_03.jpg", "photo_02.jpg",
             "photo_11.jpg", "photo_10.jpg", "photo_09.jpg", "photo_08.jpg"],
        )
        self.assertEqual(
            [photo.name for photo in score_ranked],
            [f"photo_{index:02}.jpg" for index in range(11, 2, -1)],
        )

    def test_person_name_is_shown_for_angels_and_sisters(self):
        angel = self.root / "Angels" / "Nyxene"
        sister = self.root / "Sisters" / "Draknoxa"
        prospect = self.root / "Prospects" / "Una Beck"
        for folder in (angel, sister):
            (folder / "gallery").mkdir(parents=True)
        (angel / "gallery" / "z_sabine_vale.txt").write_text(
            "name: Sabine Vale\n2026-10-20 now the Angel Nyxene; promoted from Prospects\n",
            encoding="utf-8",
        )
        (sister / "gallery" / "z_sydney_sky.txt").write_text(
            "name: Sydney Sky\n2026-10-10 +4 from Prospects/Una Beck: merged from Prospects/Una Beck\n",
            encoding="utf-8",
        )
        (prospect / "gallery").mkdir(parents=True)

        self.assertEqual(gallery.person_name(angel, "Angels"), "Sabine Vale")
        self.assertEqual(gallery.person_name(sister, "Sisters"), "Sydney Sky")
        self.assertIsNone(gallery.person_name(prospect, "Prospects"))

    def test_workflow_photo_outside_top_nine_is_shown_last_without_changing_rankings(self):
        key, folder = self.add_person("Angels", "Example", 12)
        paths = sorted((folder / "gallery").glob("*.jpg"))
        for index, path in enumerate(paths):
            path.rename(path.with_name(f"example_image_{index + 1}.jpg"))
        paths = sorted((folder / "gallery").glob("*.jpg"))
        chosen = paths[-1]
        photos = []
        for path in paths:
            photo = gallery.likeness.Photo(path, "Angels", "Example", path.stem, {
                "v": [0., 1.] if path == chosen else [1., 0.],
                "faces": 1, "px": 200, "box": [.2, .2, .4, .4], "s": .95,
            })
            photos.append(photo)
        st = gallery.likeness.settings({})
        space = gallery.likeness.Space(photos, st, mean=[0., 0.])
        cfg = {"photos": {"Example": chosen.stem + "_944x1104.png"}}
        with (
            mock.patch.object(gallery.likeness, "library_people", return_value=[(key, folder)]),
            mock.patch.object(gallery, "thumb_bytes", return_value=b"thumbnail"),
            mock.patch.object(gallery, "inspect", return_value=(True, False)),
        ):
            rows = gallery.collect(cfg, st, self.root, space, ["Angels"], catalog={
                "schemaVersion": 1, "people": {}, "photos": {}, "actions": [],
            })
        row = rows[0]
        self.assertTrue(row["chosen"])
        self.assertNotIn(chosen, row["gallery_photos_identity"])
        self.assertNotIn(chosen, row["gallery_photos_score"])
        self.assertIn(chosen.name, [photo["name"] for photo in row["gallery_photos"]])
        before = copy.deepcopy(row["gallery_photos"])
        arranged, pinned = gallery.arrange_workflow_photo(row["gallery_photos"], chosen.name)
        self.assertTrue(pinned)
        self.assertEqual(arranged[8]["name"], chosen.name)
        self.assertEqual(row["gallery_photos"], before)
        page = gallery.render_html(rows, "now", {"Angels": 1})
        self.assertIn("workflow-extra", page)
        self.assertIn("(shown last; outside top nine)", page)
        self.assertIn("outline:5px solid", page)
        self.assertIn("outline-style:dashed", page)
        self.assertIn("ordered.splice(8,0", page)
        self.assertNotIn("(not shown)</span>", page)
        md = gallery.render_md(rows, "now", {"Angels": 1}, self.tmp / "files", "people_gallery.html")
        self.assertIn("(shown last; outside top nine)", md)
        self.assertEqual(md.count("[!["), 9)

    def test_workflow_grid_pinning_boundary_missing_photo_and_no_selected_photo(self):
        photos = [{"name": str(index)} for index in range(12)]
        for index in range(12):
            with self.subTest(index=index):
                ordered, pinned = gallery.arrange_workflow_photo(photos, str(index))
                self.assertEqual(pinned, index >= 9)
                self.assertEqual(len(ordered), len(photos))
                self.assertEqual(len({photo["name"] for photo in ordered}), len(photos))
                self.assertEqual(ordered[min(index, 8)]["name"], str(index))
        for name in (None, "missing"):
            ordered, pinned = gallery.arrange_workflow_photo(photos, name)
            self.assertEqual(ordered, photos)
            self.assertFalse(pinned)
        self.assertEqual(gallery.arrange_workflow_photo([], "none"), ([], False))

    def test_html_and_markdown_show_person_name_after_chosen_label(self):
        folder = self.root / "Angels" / "Nyxene"
        gallery_dir = folder / "gallery"
        gallery_dir.mkdir(parents=True)
        source_path = gallery_dir / "nyxene.jpg"
        source_path.write_bytes(b"chosen photo")
        row = {
            "status": "Angels", "folder": "Nyxene", "photos": 1, "review": 0,
            "chosen": True, "person_name": "Sabine Vale", "score": 0.8,
            "source": "nyxene.jpg", "tags": {}, "gallery_path": folder / "gallery",
            "source_path": source_path, "source_identity_score": 0.4,
            "z_path": None, "gallery_photos": [],
        }
        html_output = gallery.render_html([row], "now", {"Angels": 1})
        self.assertIn('href="' + source_path.resolve().as_uri() + '"', html_output)
        self.assertIn("Workflow photo", html_output)
        self.assertIn("(not shown)", html_output)
        self.assertIn('class="score-badge score-yellow"', html_output)
        self.assertIn("Person: Sabine Vale", html_output)
        self.assertLess(html_output.index("Person: Sabine Vale"), html_output.index("Workflow photo"))
        self.assertIn('Workflow photo</a> <span class="score-badge score-yellow"', html_output)
        self.assertIn('class="page-header"', html_output)
        self.assertIn('class="score-legend"', html_output)
        self.assertIn(">workflow</span>", html_output)
        self.assertIn('class="category-badge photo-count">1 photo</span>', html_output)

        md_output = gallery.render_md([row], "now", {"Angels": 1}, self.root / "files", "people_gallery.html")
        self.assertIn("[workflow photo · likeness 0.40 (not shown)](" + source_path.resolve().as_uri() + ")", md_output)
        self.assertIn("Person: Sabine Vale", md_output)
        self.assertIn("1 photo · workflow", md_output)
        self.assertLess(md_output.index("Person: Sabine Vale"), md_output.index("[workflow photo"))

        visible_row = dict(row)
        visible_row["gallery_photos"] = [{
            "name": "nyxene.jpg", "path": source_path, "score": 0.8,
            "identity_score": 0.4, "identity_priority": 1, "identity_anchor": False,
            "thumbnail": None, "thumbnail_head": None,
            "thumb": b"thumbnail", "thumb_head": b"thumbnail",
        }]
        visible_html = gallery.render_html([visible_row], "now", {"Angels": 1})
        self.assertIn('class="workflow-photo score-yellow"', visible_html)
        self.assertIn("Workflow photo</a>", visible_html)
        self.assertIn("class=\"person-title\"", visible_html)
        self.assertIn("class=\"identity-tags\"", visible_html)

    def test_html_name_links_to_person_review_and_framing_switch_is_available(self):
        folder = self.root / "Prospects" / "Sydney Sky"
        (folder / "gallery").mkdir(parents=True)
        row = {
            "status": "Prospects", "folder": "Sydney Sky", "key": "Prospects/Sydney Sky",
            "photos": 1, "review": 0, "chosen": False, "score": 0.8, "source": "one.jpg",
            "tags": {}, "gallery_path": folder / "gallery", "z_path": folder / "gallery" / "z_sydney_sky.txt",
            "gallery_photos": [{"name": "one.jpg", "path": folder / "gallery" / "one.jpg",
                                "score": 0.8, "thumb": b"chest", "thumb_head": b"head",
                                "thumbnail": "people_gallery_review_files/one_chest_abc.jpg"}],
        }
        output = gallery.render_html([row], "now", {"Prospects": 1})

        self.assertIn(gallery.gallery_chrome.CARD_USE_GUIDANCE["Prospects"], output)
        self.assertIn("Not a rarity rule or automatic assignment.", output)
        for category in ("Potentials", "Models"):
            alternate = dict(row, status=category, key=f"{category}/Sydney Sky")
            page = gallery.render_html([alternate], "now", {category: 1})
            self.assertIn(gallery.gallery_chrome.CARD_USE_GUIDANCE[category], page)
        self.assertIn(
            'href="people_gallery_review.html?person=Prospects%2FSydney+Sky&amp;bucket=Gallery&amp;sort=identity"',
            output,
        )
        self.assertIn('target="_blank" rel="noopener noreferrer" title="Open this person', output)
        self.assertIn('class="history"', output)
        self.assertIn('id="thumbnail-framing"', output)
        self.assertIn("data-head=", output)
        self.assertIn("Prime-start score 0.800", output)
        self.assertNotIn('aria-label="Stay at Sydney Sky"', output)
        self.assertIn("people_gallery_review.html?person=Prospects%2FSydney+Sky", output)
        with_review = gallery.render_html([dict(row, review=3)], "now", {"Prospects": 1})
        self.assertIn(
            'person=Prospects%2FSydney+Sky&amp;bucket=Review&amp;sort=identity', with_review,
        )
        self.assertIn('class="badge review-count"', with_review)
        self.assertEqual(with_review.count("3 in review"), 1)

        shared_thumbnails = self.root / "people_gallery_review_files"
        shared_thumbnails.mkdir()
        (shared_thumbnails / "one_chest_abc.jpg").write_bytes(b"chest")
        markdown = gallery.render_md(
            [row], "now", {"Prospects": 1}, shared_thumbnails, "people_gallery.html"
        )
        self.assertIn(
            "[Sydney Sky](people_gallery_review.html?person=Prospects%2FSydney+Sky&bucket=Gallery&sort=identity)",
            markdown,
        )
        self.assertIn("people_gallery_review_files/one_chest_abc.jpg", markdown)
        self.assertIn("[history](", markdown)

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
            "identity_rankings": [
                {"category": "Angels", "name": "Camaris", "score": 0.41},
            ],
        }
        angel = {
            "status": "Angels", "folder": "Camaris", "photos": 0, "review": 0, "chosen": False, "score": None,
            "source": "", "tags": {}, "gallery_path": angel_path, "z_path": None, "gallery_photos": [],
            "paired_sister": "Draknora", "hair_color": "", "candidate_prospects": [prospect],
            "identity_rankings": [
                {"category": "Sisters", "name": "Draknora", "score": 0.30},
            ],
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
        self.assertIn('person=Angels%2FCamaris', output)
        self.assertIn('person=Prospects%2FBest+Fit', output)
        self.assertIn('person=Sisters%2FDraknora', output)
        self.assertIn('href="#person-angels-camaris"', output)
        self.assertIn('href="#person-prospects-best_fit"', output)
        self.assertNotIn('aria-label="Stay at Draknora"', output)
        self.assertIn("Current Angel:", output)
        self.assertNotIn("Current Angel pairing:", output)
        self.assertIn('title="Jump to this person · likeness 0.41">▶</a>', output)
        self.assertIn('title="Current Angel likeness score">0.41</span>', output)
        self.assertIn('title="Jump to this person · likeness 0.30">▶</a>', output)
        self.assertIn('title="Paired Sister likeness score">0.30</span>', output)
        self.assertIn('Best Angel: <a href="people_gallery_review.html?person=Angels%2FCamaris&amp;bucket=Gallery&amp;sort=identity"', output)
        self.assertIn('title="Jump to this person · likeness 0.28">▼</a>', output)
        self.assertIn('title="Best Angel likeness score">0.28</span>', output)
        self.assertNotIn("Best Angel fit:", output)
        self.assertIn("Top Prospect alternatives:", output)
        self.assertIn('<div class="pairing-subsection">Top Prospect alternatives:<br><div>1.', output)
        self.assertIn("Fit ", output)
        self.assertIn('title="Prospect likeness to Sister">0.28</span>', output)
        self.assertIn('title="Adjusted fit cost; lower is better">0.030</span>', output)
        self.assertIn('title="Likeness fit cost; lower is better">0.050</span>', output)
        self.assertIn('title="Variety bonus reduces adjusted fit cost">+0.02</span>', output)
        self.assertIn("10 photos", output)
        self.assertIn("score-yellow", output)
        self.assertIn(">▼</a>", output)
        self.assertIn("Best Angel:", output)

        markdown = gallery.render_md(
            [sister, angel, candidate], "now", {"Sisters": 1, "Angels": 1, "Prospects": 1},
            self.root / "markdown_thumbnails", "people_gallery.html",
        )
        self.assertIn("Top Prospect alternatives:<br>1. Best Fit", markdown)

    def test_adjusted_fit_badge_colors_lower_cost_as_better(self):
        self.assertIn("score-green", gallery.fit_badge(-0.025))
        self.assertIn("score-green", gallery.fit_badge(0.05))
        self.assertIn("score-yellow", gallery.fit_badge(0.051))
        self.assertIn("score-orange", gallery.fit_badge(0.101))
        self.assertIn("score-red", gallery.fit_badge(0.201))
        self.assertIn("lower is better", gallery.fit_badge(-0.025))

    def test_html_and_full_library_report_expose_category_rankings_in_details(self):
        row = {
            "status": "Angels",
            "folder": "Camaris",
            "photos": 1,
            "review": 0,
            "chosen": False,
            "score": 0.8,
            "source": "photo.jpg",
            "tags": {},
            "gallery_path": self.root / "Angels" / "Camaris" / "gallery",
            "z_path": None,
            "gallery_photos": [],
            "identity_matches_by_category": [
                {"category": "Sisters", "name": "Draknora", "score": 0.72},
                {"category": "Models", "name": "Freya", "score": 0.51},
            ],
            "identity_rankings": [
                {"category": "Sisters", "name": "Draknora", "score": 0.72},
                {"category": "Models", "name": "Freya", "score": 0.51},
            ],
        }

        output = gallery.render_html([row], "now", {"Angels": 1})
        report = gallery.render_identity_report([row], "now")

        self.assertIn('id="detail-level"', output)
        self.assertIn('body[data-detail-level="summary"] .full-details', output)
        self.assertIn("Closest by category:", output)
        self.assertIn("Sisters: Draknora", output)
        self.assertIn("Models: Freya", output)
        self.assertLess(output.index("Sisters: Draknora"), output.index("Models: Freya"))
        self.assertIn("score-yellow", output)
        self.assertIn("Full library rankings", output)
        self.assertIn("| 2 | Models | Freya | 0.510 |", report)

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
            "identity_protected": True,
            "tags": {"type": ["human"], "roles": ["artist", "mage"], "elements": ["Light"]},
            "gallery_path": photo.parent,
            "z_path": history,
            "gallery_photos": [{"name": photo.name, "path": photo, "thumb": b"thumbnail"}],
        }

        output = gallery.render_html([row], "now", {"Prospects": 1})

        self.assertIn('href="' + photo.resolve().as_uri() + '"', output)
        self.assertNotIn("Open folder", output)
        self.assertIn("1 photo", output)
        self.assertIn('class="category-badge photo-count">1 photo</span>', output)
        self.assertIn('class="category-badge protected-badge">Protected identity</span>', output)
        self.assertIn('href="' + history.resolve().as_uri() + '"', output)
        self.assertIn("Prime-start photo score 0.76", output)
        self.assertIn('class="score-badge score-green">≥0.55</span>', output)
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
        self.assertIn("Closest Sisters:<br>", output)
        self.assertIn('person=Sisters%2FDrak', output)
        self.assertIn('person=Sisters%2FLuna', output)
        self.assertIn("Usable faces: 0/1", output)

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

    def test_angel_card_shows_review_links_and_alternatives_without_action_preview(self):
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
            "identity_rankings": [{"category": "Sisters", "name": "Draknava", "score": 0.30}],
            "candidate_prospects": [{"name": "Esme Marsh", "score": 0.25, "cost": 0.03, "likeness_cost": 0.05, "photo_bonus": 0.02, "photos": 10}],
            "candidate_rankings": [{"name": "Esme Marsh", "score": 0.25, "photos": 10, "cohesion": 0.6, "likeness_cost": 0.05, "photo_bonus": 0.02, "cost": 0.03}],
        }

        output = gallery.render_html([row], "now", {"Angels": 1})

        self.assertIn("Paired Sister:", output)
        self.assertIn('person=Sisters%2FDraknava', output)
        self.assertIn('title="Jump to this person · likeness 0.30">▶</a>', output)
        self.assertIn('title="Paired Sister likeness score">0.30</span>', output)
        self.assertIn('person=Prospects%2FEsme+Marsh', output)
        self.assertIn('Fit <span class="score-badge score-green"', output)
        self.assertIn(">0.030</span>", output)
        self.assertNotIn("Promotion preview", output)
        self.assertNotIn("Current hair:", output)
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
            "identity_rankings": [{"category": "Sisters", "name": "Draknava", "score": 0.30}],
            "candidate_prospects": [{
                "name": "Mara Carrington", "cost": -0.029, "likeness_cost": 0.031,
                "photo_bonus": 0.06, "photos": 20,
            }],
        }

        output = gallery.render_md([angel], "now", {"Angels": 1}, self.root / "files", "people_gallery.html")

        self.assertIn("Paired Sister: Draknava (0.30)", output)
        self.assertIn("Mara Carrington (adjusted -0.029, fit 0.031, +0.06, 20 photos)", output)
        self.assertIn("[full rankings](../comparisons/pairings/angel-prospect-candidates.md)", output)


if __name__ == "__main__":
    unittest.main()
