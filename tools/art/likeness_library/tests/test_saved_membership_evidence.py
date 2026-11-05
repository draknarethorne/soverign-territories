"""Bounded saved-score diagnostics; optimistic envelopes are never routing authority."""
import copy
import pathlib
import unittest

from tools.art.likeness_library import clean_rebase, refinement
from tools.art.likeness_library.policy import load_policy


def optimistic_comparison(saved, target=None):
    """Keep actual scores, explicitly assume every unavailable evidence gate passes."""
    row = copy.deepcopy(saved)
    if target is not None:
        row["rivals"] = [copy.deepcopy(target)] + [
            rival for rival in saved.get("rivals", []) if rival["folder"] != target["folder"]
        ]
    row.update(
        ambiguousPhotoId=False, qualityEligible=True, metadataStale=False,
        identityProtected=False, rejectionHistory=False,
        bucket=pathlib.PurePosixPath(row["destination"]).parent.name,
    )
    rival = row["rivals"][0] if row.get("rivals") else None
    row["higherRival"] = bool(
        rival and row.get("ownScore") is not None and rival["score"] > row["ownScore"]
    )
    row["refinementTarget"] = {
        **rival, "independentSupport": 4, "identityProtected": False,
    } if rival else None
    return row


def inspect_saved_audit(plan, policy):
    audit = plan["finalMembershipAudit"]
    higher = [row for row in audit["rows"] if row.get("higherRival")]
    followups = [row for row in higher if row.get("followupCandidate")]
    followup_results = []
    for row in followups:
        followup_results.append({
            "photoId": row["photoId"], "source": row["source"], "destination": row["destination"],
            "ownScore": row["ownScore"], "rivals": row["rivals"],
            "savedEvidenceDecision": refinement.membership_decision(row, policy),
            "optimisticEvidenceDecision": refinement.membership_decision(optimistic_comparison(row), policy),
        })
    briar = [row for row in audit["rows"] if "/Briar Cruz/" in row["destination"]]
    measured = []
    for row in briar:
        sammara = next((
            reference for reference in row.get("castReferences", [])
            if reference["folder"].casefold() == "angels/sammara"
            and reference.get("score") is not None
        ), None)
        if sammara is None:
            continue
        hypothetical = optimistic_comparison(row, sammara)
        measured.append({
            "photoId": row["photoId"], "source": row["source"], "ownScore": row["ownScore"],
            "sammaraScore": sammara["score"],
            "savedEvidenceDecision": refinement.membership_decision(row, policy),
            "optimisticSammaraDecision": refinement.membership_decision(hypothetical, policy),
        })
    return {
        "mode": "saved evidence only; no matching, embedding, routing, install or pixel changes",
        "limitations": [
            "Old rows lack qualityEligible, metadataStale, ambiguousPhotoId, identityProtected, rejectionHistory, bucket and refinementTarget.",
            "independentProtectionSupport is own-identity protection support, not independent destination-core support.",
            "Optimistic decisions assume quality/fresh bytes/unique IDs/no source or destination identity lock/no rejection/four independent destination references; they are score-only upper bounds, not authorized moves.",
            "Saved photo protection, anchor and workflow flags remain enforced even in the optimistic envelope.",
            "Only saved top-three rivals/cast references are available; omitted Sammara scores are unknown, not zero.",
            "No new measured/aligned-face or pose/core-coverage diagnosis is performed; E19 pixel-level acceptance remains open.",
        ],
        "higherRivalCount": len(higher), "followupCount": len(followups),
        "followups": followup_results,
        "briar": {
            "totalCount": len(briar), "usableOwnScoreCount": sum(row.get("ownScore") is not None for row in briar),
            "photoProtectedCount": sum(bool(row.get("protected")) for row in briar),
            "savedSammaraCount": len(measured),
            "sammaraScoreMinimum": min((row["sammaraScore"] for row in measured), default=None),
            "sammaraScoreMaximum": max((row["sammaraScore"] for row in measured), default=None),
            "rows": measured,
        },
    }


class SavedMembershipEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.policy = clean_rebase.core_protection_policy(load_policy())
        self.saved = {
            "source": "Various/gallery/incoming_image_123456.jpg",
            "destination": "Models/Briar Cruz/gallery/briar_cruz_image_123456.jpg",
            "photoId": "photo:image_123456", "ownScore": .335294,
            "rivals": [{"folder": "Prospects/Ruby Hartwell", "score": .4372},
                       {"folder": "Models/Bellamy Ives", "score": .279092}],
            "protected": False, "anchor": False, "workflowSelected": False,
            "higherRival": True, "followupCandidate": True,
            "independentProtectionSupport": 41,
        }

    def test_old_own_protection_support_does_not_substitute_destination_support(self):
        decision = refinement.membership_decision(self.saved, self.policy)
        self.assertEqual(decision["decision"], "hold")
        self.assertIn("saved comparison evidence unavailable", decision["reason"])
        self.assertIn("refinementTarget", decision["reason"])
        optimistic = optimistic_comparison(self.saved)
        self.assertEqual(refinement.membership_decision(optimistic, self.policy)["decision"], "move")
        optimistic["rivals"][0]["score"] = .7
        optimistic["refinementTarget"]["score"] = .7
        self.assertEqual(refinement.membership_decision(optimistic, self.policy)["decision"], "move")
        optimistic["refinementTarget"]["independentSupport"] = 0
        self.assertIn("independent", refinement.membership_decision(optimistic, self.policy)["reason"])

    def test_saved_sammara_maximum_and_cluster_score_are_not_gallery_authority(self):
        for score in (.103610, .435089, .4692):
            with self.subTest(score=score):
                row = optimistic_comparison(self.saved, {"folder": "Angels/sammara", "score": score})
                row["ownScore"] = -.1
                row["higherRival"] = True
                row["rivals"] = row["rivals"][:1]
                result = refinement.membership_decision(row, self.policy)
                self.assertEqual(result["decision"], "hold")
                self.assertIn("cast Review admission gates not met", result["reason"])
        protected = optimistic_comparison(self.saved)
        protected["protected"] = True
        self.assertIn("protected", refinement.membership_decision(protected, self.policy)["reason"])

    def test_bounded_report_keeps_missing_scores_unknown(self):
        row = copy.deepcopy(self.saved)
        row["castReferences"] = [{"folder": "Angels/sammara", "score": .435089}]
        omitted = {**copy.deepcopy(row), "source": "missing", "castReferences": []}
        report = inspect_saved_audit({"finalMembershipAudit": {"rows": [row, omitted]}}, self.policy)
        self.assertEqual(report["followupCount"], 2)
        self.assertEqual(report["briar"]["totalCount"], 2)
        self.assertEqual(report["briar"]["savedSammaraCount"], 1)
        self.assertEqual(report["briar"]["sammaraScoreMinimum"], .435089)
