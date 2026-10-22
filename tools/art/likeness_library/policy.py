"""Validated, declarative likeness thresholds and protection-aware decisions."""
import functools
import html
import json
import math
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_POLICY_PATH = ROOT / "data" / "art" / "likeness-engine-policy.json"
POLICY_STATUSES = {"draft", "approved"}


def _number(value, label, minimum=-1.0, maximum=1.0):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}")
    return float(value)


def validate_policy(policy):
    """Reject incomplete or internally inconsistent policy before any run uses it."""
    if not isinstance(policy, dict):
        raise ValueError("likeness policy must be a JSON object")
    required = {
        "schemaVersion",
        "version",
        "status",
        "categoryOrder",
        "scoreBands",
        "categoryAssignmentRules",
        "highCastSimilarityMinimum",
        "castReviewMinimum",
        "smallGroupCastReviewMinimum",
        "photoRouting",
        "identityActions",
        "lookalikeGroups",
        "categoryPolicies",
        "protection",
    }
    if set(policy) != required:
        missing = sorted(required - set(policy))
        extra = sorted(set(policy) - required)
        raise ValueError(f"likeness policy keys mismatch; missing={missing}, extra={extra}")
    if policy["schemaVersion"] != 1:
        raise ValueError("unsupported likeness policy schemaVersion")
    if not isinstance(policy["version"], str) or not policy["version"].strip():
        raise ValueError("likeness policy version must be a non-empty string")
    if policy["status"] not in POLICY_STATUSES:
        raise ValueError("likeness policy status must be draft or approved")

    categories = policy["categoryOrder"]
    if (
        not isinstance(categories, list)
        or not categories
        or any(not isinstance(category, str) or not category.strip() for category in categories)
        or len({category.casefold() for category in categories}) != len(categories)
    ):
        raise ValueError("categoryOrder must contain unique, non-empty category names")
    category_policies = policy["categoryPolicies"]
    if not isinstance(category_policies, dict) or set(category_policies) != set(categories):
        raise ValueError("categoryPolicies must define exactly the categories in categoryOrder")
    for category, rules in category_policies.items():
        required_category_keys = {
            "identityProtectedByDefault",
            "automaticMergeEnabled",
            "automaticSplitEnabled",
            "automaticPhotoRoutingEnabled",
            "identityCoreMinimumSimilarity",
            "reviewSuggestionBelowSimilarity",
            "splitCandidateBelowSimilarity",
            "minimumUsablePhotosForOutlierActions",
        }
        if set(rules) != required_category_keys:
            raise ValueError(f"categoryPolicies/{category} keys are incomplete or unsupported")
        for key in (
            "identityProtectedByDefault",
            "automaticMergeEnabled",
            "automaticSplitEnabled",
            "automaticPhotoRoutingEnabled",
        ):
            if not isinstance(rules[key], bool):
                raise ValueError(f"categoryPolicies/{category}/{key} must be boolean")
        core_min = _number(
            rules["identityCoreMinimumSimilarity"],
            f"{category} identity core minimum",
        )
        review_below = _number(
            rules["reviewSuggestionBelowSimilarity"],
            f"{category} review suggestion threshold",
        )
        split_below = _number(
            rules["splitCandidateBelowSimilarity"],
            f"{category} split candidate threshold",
        )
        if split_below > core_min or split_below > review_below:
            raise ValueError(f"categoryPolicies/{category} outlier thresholds conflict")
        minimum_photos = rules["minimumUsablePhotosForOutlierActions"]
        if isinstance(minimum_photos, bool) or not isinstance(minimum_photos, int) or minimum_photos < 1:
            raise ValueError(f"categoryPolicies/{category} minimum usable photo count must be positive")

    bands = policy["scoreBands"]
    if set(bands) != {"green", "yellow", "orange", "red"}:
        raise ValueError("scoreBands must define green, yellow, orange, and red")
    green = _number(bands["green"].get("minimum"), "green minimum")
    yellow = _number(bands["yellow"].get("minimum"), "yellow minimum")
    orange = _number(bands["orange"].get("minimum"), "orange minimum")
    if not green > yellow > orange:
        raise ValueError("score band minima must descend from green to orange")
    if _number(bands["red"].get("maximumExclusive"), "red maximum") != orange:
        raise ValueError("red maximum must equal the orange minimum")

    cast_review = _number(policy["castReviewMinimum"], "cast review minimum")
    high_cast = _number(policy["highCastSimilarityMinimum"], "high cast review minimum")
    if high_cast < cast_review:
        raise ValueError("high cast review minimum must be at or above cast review minimum")
    small_group_cast_review = _number(
        policy["smallGroupCastReviewMinimum"],
        "small-group cast review minimum",
    )
    if not cast_review <= small_group_cast_review < high_cast:
        raise ValueError(
            "small-group cast review minimum must be at or above cast review minimum "
            "and below the high cast review minimum"
        )
    assignment_rules = policy["categoryAssignmentRules"]
    if not isinstance(assignment_rules, list) or not assignment_rules:
        raise ValueError("categoryAssignmentRules must be a non-empty list")
    seen_routes = set()
    for index, rule in enumerate(assignment_rules):
        required_rule_keys = {"category", "minimumUsablePhotos"}
        optional_rule_keys = {
            "maximumUsablePhotos",
            "minimumCastSimilarity",
            "maximumCastSimilarityExclusive",
        }
        if (
            not isinstance(rule, dict)
            or not required_rule_keys <= set(rule)
            or set(rule) - required_rule_keys - optional_rule_keys
        ):
            raise ValueError(f"categoryAssignmentRules/{index} has invalid keys")
        category = rule["category"]
        if category not in category_policies:
            raise ValueError(f"categoryAssignmentRules/{index} references an unconfigured category")
        if category in seen_routes:
            raise ValueError(f"categoryAssignmentRules has duplicate route for {category}")
        seen_routes.add(category)
        minimum_photos = rule["minimumUsablePhotos"]
        maximum_photos = rule.get("maximumUsablePhotos")
        if isinstance(minimum_photos, bool) or not isinstance(minimum_photos, int) or minimum_photos < 1:
            raise ValueError(f"categoryAssignmentRules/{index} minimumUsablePhotos must be positive")
        if maximum_photos is not None and (
            isinstance(maximum_photos, bool)
            or not isinstance(maximum_photos, int)
            or maximum_photos < minimum_photos
        ):
            raise ValueError(f"categoryAssignmentRules/{index} maximumUsablePhotos is invalid")
        minimum_cast = rule.get("minimumCastSimilarity")
        maximum_cast = rule.get("maximumCastSimilarityExclusive")
        if minimum_cast is not None:
            minimum_cast = _number(minimum_cast, f"categoryAssignmentRules/{index} minimum cast score")
        if maximum_cast is not None:
            maximum_cast = _number(maximum_cast, f"categoryAssignmentRules/{index} maximum cast score")
        if minimum_cast is not None and maximum_cast is not None and minimum_cast >= maximum_cast:
            raise ValueError(f"categoryAssignmentRules/{index} cast score range is invalid")

    identity = policy["identityActions"]
    if set(identity) != {
        "matchReviewMinimum",
        "autoMergeMinimum",
        "autoMergeMinimumMargin",
        "autoMergeMinimumIndependentPhotos",
        "splitReviewMaximum",
        "splitMinimumAlternativeSimilarity",
        "splitMinimumMargin",
        "splitMinimumIndependentPhotos",
        "identityClusterMinimumSimilarity",
    }:
        raise ValueError("identityActions keys are incomplete or unsupported")
    merge_min = _number(identity["autoMergeMinimum"], "automatic merge minimum")
    _number(identity["identityClusterMinimumSimilarity"], "identity cluster minimum")
    review_min = _number(identity["matchReviewMinimum"], "match review minimum")
    split_max = _number(identity["splitReviewMaximum"], "split review maximum")
    alternative_min = _number(
        identity["splitMinimumAlternativeSimilarity"], "split alternative minimum"
    )
    _number(identity["autoMergeMinimumMargin"], "automatic merge margin", 0.0, 2.0)
    _number(identity["splitMinimumMargin"], "split minimum margin", 0.0, 2.0)
    for key in ("autoMergeMinimumIndependentPhotos", "splitMinimumIndependentPhotos"):
        if isinstance(identity[key], bool) or not isinstance(identity[key], int) or identity[key] < 2:
            raise ValueError(f"{key} must be an integer of at least 2")
    if merge_min < review_min or split_max > review_min or alternative_min < review_min:
        raise ValueError("identity action thresholds conflict with the review threshold")

    lookalikes = policy["lookalikeGroups"]
    if set(lookalikes) != {"suggestionMinimumSimilarity", "automaticAssociationEnabled"}:
        raise ValueError("lookalikeGroups keys are incomplete or unsupported")
    _number(lookalikes["suggestionMinimumSimilarity"], "lookalike suggestion minimum")
    if not isinstance(lookalikes["automaticAssociationEnabled"], bool):
        raise ValueError("lookalikeGroups automaticAssociationEnabled must be boolean")

    photo_routing = policy["photoRouting"]
    if set(photo_routing) != {
        "reviewMinimum",
        "automaticRouteMinimum",
        "minimumMargin",
        "minimumOwnCoreLead",
    }:
        raise ValueError("photoRouting keys are incomplete or unsupported")
    route_review = _number(photo_routing["reviewMinimum"], "photo route review minimum")
    route_auto = _number(photo_routing["automaticRouteMinimum"], "automatic route minimum")
    if route_auto < route_review:
        raise ValueError("automatic photo routing threshold must be at or above review minimum")
    _number(photo_routing["minimumMargin"], "photo route minimum margin", 0.0, 2.0)
    _number(photo_routing["minimumOwnCoreLead"], "photo route minimum own-core lead", 0.0, 2.0)

    protection = policy["protection"]
    if set(protection) != {
        "identityBlocksAutomaticMoves",
        "photoBlocksAutomaticRemoval",
        "photoBlocksReviewRouting",
        "protectedPhotoMayBeExcludedFromCore",
    } or any(not isinstance(value, bool) for value in protection.values()):
        raise ValueError("protection policy is incomplete or invalid")
    if not all(protection.values()):
        raise ValueError("protection policy must preserve every approved protection rule")
    return policy


def load_policy(path=None):
    """Load and validate the configured policy, failing explicitly on bad data."""
    policy_path = pathlib.Path(path) if path else DEFAULT_POLICY_PATH
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load likeness policy {policy_path}: {error}") from error
    return validate_policy(policy)


@functools.lru_cache(maxsize=1)
def default_policy():
    return load_policy()


def score_band(score, policy=None):
    """Return the configured display-only similarity color."""
    if score is None:
        raise ValueError("similarity score cannot be None")
    score = _number(score, "similarity score", -1.0, 1.0)
    bands = (policy or default_policy())["scoreBands"]
    if score >= bands["green"]["minimum"]:
        return "green"
    if score >= bands["yellow"]["minimum"]:
        return "yellow"
    if score >= bands["orange"]["minimum"]:
        return "orange"
    return "red"


def render_score_legend(policy=None):
    config = policy or default_policy()
    bands = config["scoreBands"]
    labels = (
        ("green", f"≥{bands['green']['minimum']:.2f}"),
        ("yellow", f"≥{bands['yellow']['minimum']:.2f}"),
        ("orange", f"≥{bands['orange']['minimum']:.2f}"),
        ("red", f"<{bands['red']['maximumExclusive']:.2f}"),
    )
    return "".join(
        f'<span class="score-badge score-{color}">{label}</span>'
        for color, label in labels
    )


def classify_category(
    usable_photo_count,
    cast_similarity=None,
    policy=None,
    *,
    best_cast_folder=None,
    second_cast_folder=None,
    cast_margin=None,
):
    """Classify a candidate group, holding small cast-like groups for review."""
    config = policy or default_policy()
    if isinstance(usable_photo_count, bool) or not isinstance(usable_photo_count, int):
        raise ValueError("usable photo count must be an integer")
    if usable_photo_count < 0:
        raise ValueError("usable photo count cannot be negative")
    if cast_similarity is not None:
        cast_similarity = _number(cast_similarity, "cast similarity")
    if cast_margin is not None:
        cast_margin = _number(cast_margin, "cast match margin", 0.0, 2.0)

    def review_result(reason):
        minimum_margin = config["photoRouting"]["minimumMargin"]
        destination = (
            f"{best_cast_folder}/review"
            if best_cast_folder
            and cast_margin is not None
            and cast_margin >= minimum_margin
            else None
        )
        alternatives = [
            folder for folder in (best_cast_folder, second_cast_folder) if folder
        ]
        return {
            "category": "Review",
            "reviewRequired": True,
            "reason": reason,
            "castSimilarity": cast_similarity,
            "reviewDestination": destination,
            "reviewAlternatives": alternatives,
        }

    if usable_photo_count == 0:
        return {
            "category": None,
            "reviewRequired": True,
            "reason": "no usable photos",
            "castSimilarity": cast_similarity,
            "reviewDestination": None,
            "reviewAlternatives": [],
        }
    if cast_similarity is not None and cast_similarity >= config["highCastSimilarityMinimum"]:
        reason = (
            "high cast similarity may indicate a same-person match; do not auto-classify"
        )
        if (
            second_cast_folder
            and cast_margin is not None
            and cast_margin < config["photoRouting"]["minimumMargin"]
        ):
            reason = "high similarity to multiple cast identities; hold for ambiguous cast review"
        return review_result(reason)
    if (
        usable_photo_count <= 4
        and cast_similarity is not None
        and cast_similarity >= config["smallGroupCastReviewMinimum"]
    ):
        if (
            second_cast_folder
            and cast_margin is not None
            and cast_margin < config["photoRouting"]["minimumMargin"]
        ):
            reason = "small group has close matches to multiple cast identities; hold for ambiguous cast review"
        else:
            reason = (
                "small group falls in the configured Model resemblance band; "
                "review cast match before assigning it as a Potential"
            )
        return review_result(reason)
    for rule in config["categoryAssignmentRules"]:
        if usable_photo_count < rule["minimumUsablePhotos"]:
            continue
        if rule.get("maximumUsablePhotos") is not None and usable_photo_count > rule["maximumUsablePhotos"]:
            continue
        if (
            rule.get("minimumCastSimilarity") is not None
            and (
                cast_similarity is None
                or cast_similarity < rule["minimumCastSimilarity"]
            )
        ):
            continue
        if (
            rule.get("maximumCastSimilarityExclusive") is not None
            and cast_similarity is not None
            and cast_similarity >= rule["maximumCastSimilarityExclusive"]
        ):
            continue
        review_required = (
            cast_similarity is not None
            and cast_similarity >= config["castReviewMinimum"]
        )
        category_rules = config["categoryPolicies"][rule["category"]]
        if category_rules["identityProtectedByDefault"]:
            return {
                "category": "Review",
                "reviewRequired": True,
                "reason": "configured destination category is identity-protected",
                "castSimilarity": cast_similarity,
                "reviewDestination": None,
                "reviewAlternatives": [],
            }
        return {
            "category": rule["category"],
            "reviewRequired": review_required,
            "reason": (
                "lookalike score meets the visual-review threshold"
                if review_required
                else f"matches configured {rule['category']} assignment rule"
            ),
            "castSimilarity": cast_similarity,
            "reviewDestination": None,
            "reviewAlternatives": [],
        }
    return review_result("no configured category-assignment rule matched")


def evaluate_photo_consistency(
    category,
    *,
    score,
    usable_photo_count,
    identity_protected=False,
    photo_protected=False,
    workflow_selected=False,
    policy=None,
):
    """Apply category-specific core, Review, and split-candidate thresholds."""
    config = policy or default_policy()
    rules = config["categoryPolicies"].get(category)
    if rules is None:
        raise ValueError(f"category has no likeness policy: {category}")
    if (
        isinstance(usable_photo_count, bool)
        or not isinstance(usable_photo_count, int)
        or usable_photo_count < 1
    ):
        raise ValueError("usable photo count must be a positive integer")
    if score is not None:
        score = _number(score, "photo core similarity")

    core_member = (
        usable_photo_count == 1
        if score is None
        else score >= rules["identityCoreMinimumSimilarity"]
    )
    if photo_protected and not (score is None and usable_photo_count == 1):
        core_member = False

    if score is None:
        return {
            "coreMember": core_member,
            "decision": "keep",
            "reason": "single or unscored photo; no outlier action",
        }
    if photo_protected or workflow_selected or identity_protected:
        return {
            "coreMember": core_member,
            "decision": "keep",
            "reason": "protection blocks automatic Review or split routing",
        }
    if usable_photo_count < rules["minimumUsablePhotosForOutlierActions"]:
        return {
            "coreMember": core_member,
            "decision": "keep",
            "reason": (
                "not enough usable photos for this category's outlier actions"
            ),
        }
    if score >= rules["reviewSuggestionBelowSimilarity"]:
        return {
            "coreMember": core_member,
            "decision": "keep",
            "reason": "score is above this category's Review suggestion threshold",
        }
    if (
        score < rules["splitCandidateBelowSimilarity"]
        and usable_photo_count >= rules["minimumUsablePhotosForOutlierActions"]
        and rules["automaticSplitEnabled"]
    ):
        return {
            "coreMember": core_member,
            "decision": "split-review",
            "reason": (
                "red outlier is excluded from the core; split/routing candidate "
                "requires review under the draft policy"
            ),
        }
    return {
        "coreMember": core_member,
        "decision": "review",
        "reason": (
            "score is below this category's Review suggestion threshold; "
            "the photo remains in the identity core when its core threshold allows it"
        ),
    }


def evaluate_identity_action(
    action,
    category,
    *,
    score,
    margin=None,
    evidence_count=1,
    identity_protected=False,
    photo_protected=False,
    policy=None,
):
    """Return a protection-aware action decision; draft policies never automate."""
    config = policy or default_policy()
    category_rules = config["categoryPolicies"].get(category)
    if category_rules is None:
        raise ValueError(f"category has no likeness policy: {category}")
    if action not in {"merge", "split"}:
        raise ValueError(f"unsupported identity action: {action}")
    if isinstance(evidence_count, bool) or not isinstance(evidence_count, int) or evidence_count < 1:
        raise ValueError("evidence count must be a positive integer")
    score = _number(score, "action score")

    if action == "merge":
        if photo_protected:
            return {"decision": "keep", "reason": "protected photo cannot be moved or review-routed"}
        if identity_protected or category_rules["identityProtectedByDefault"]:
            return {"decision": "blocked", "reason": "protected identity cannot be moved into or out of"}
        identity = config["identityActions"]
        if score < identity["matchReviewMinimum"]:
            return {"decision": "no-match", "reason": "below visual review threshold"}
        margin = _number(margin, "match margin", 0.0, 2.0) if margin is not None else 0.0
        qualifies = (
            config["status"] == "approved"
            and category_rules["automaticMergeEnabled"]
            and score >= identity["autoMergeMinimum"]
            and margin >= identity["autoMergeMinimumMargin"]
            and evidence_count >= identity["autoMergeMinimumIndependentPhotos"]
        )
        if qualifies:
            return {"decision": "auto-merge", "reason": "approved policy thresholds satisfied"}
        return {
            "decision": "review",
            "reason": (
                "draft policy; candidate requires visual review"
                if config["status"] == "draft"
                else "merge evidence does not meet every automatic threshold"
            ),
        }

    if identity_protected or category_rules["identityProtectedByDefault"]:
        return {"decision": "blocked", "reason": "protected identity cannot be split automatically"}
    identity = config["identityActions"]
    if score >= identity["splitReviewMaximum"]:
        return {"decision": "keep", "reason": "own-core score is not in the outlier band"}
    margin = _number(margin, "split margin", 0.0, 2.0) if margin is not None else 0.0
    alternative_score = _number(
        0.0 if margin is None else score + margin,
        "alternative similarity",
    )
    if photo_protected:
        return {
            "decision": "keep",
            "reason": "protected photo may remain workflow-usable outside the identity core",
        }
    qualifies = (
        config["status"] == "approved"
        and category_rules["automaticSplitEnabled"]
        and evidence_count >= identity["splitMinimumIndependentPhotos"]
        and alternative_score >= identity["splitMinimumAlternativeSimilarity"]
        and margin >= identity["splitMinimumMargin"]
    )
    if qualifies:
        return {"decision": "auto-split", "reason": "approved policy thresholds satisfied"}
    return {
        "decision": "review",
        "reason": (
            "low own-core score; inspect before splitting"
            if config["status"] == "draft"
            else "split evidence does not meet every automatic threshold"
        ),
    }


def evaluate_photo_route(
    category,
    *,
    score,
    margin,
    identity_protected=False,
    photo_protected=False,
    workflow_selected=False,
    policy=None,
):
    """Decide whether a candidate photo may be routed into an identity."""
    config = policy or default_policy()
    category_rules = config["categoryPolicies"].get(category)
    if category_rules is None:
        raise ValueError(f"category has no likeness policy: {category}")
    score = _number(score, "photo match score")
    margin = _number(margin, "photo match margin", 0.0, 2.0)
    if photo_protected or workflow_selected:
        return {"decision": "keep", "reason": "protected or workflow-selected photo"}
    if identity_protected or category_rules["identityProtectedByDefault"]:
        return {"decision": "blocked", "reason": "protected identity cannot receive automatic moves"}
    routing = config["photoRouting"]
    if score < routing["reviewMinimum"]:
        return {"decision": "no-match", "reason": "below visual review threshold"}
    if (
        config["status"] == "approved"
        and category_rules["automaticPhotoRoutingEnabled"]
        and score >= routing["automaticRouteMinimum"]
        and margin >= routing["minimumMargin"]
    ):
        return {"decision": "auto-route", "reason": "approved policy thresholds satisfied"}
    return {
        "decision": "review",
        "reason": (
            "draft policy; candidate requires visual review"
            if config["status"] == "draft"
            else "photo route does not meet every automatic threshold"
        ),
    }


def render_policy_panel(policy=None):
    """Render the complete, versioned policy in a compact gallery disclosure."""
    config = policy or default_policy()
    status_label = "Draft - review only" if config["status"] == "draft" else "Approved policy"
    raw = html.escape(json.dumps(config, indent=2, ensure_ascii=True))
    return (
        '<details class="policy-panel"><summary>'
        f'Likeness policy: {html.escape(status_label)} | inspect all thresholds'
        f"</summary><pre>{raw}</pre></details>"
    )
