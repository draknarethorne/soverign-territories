"""Batch calibration and leave-one-out folder diagnostics for a likeness Space."""
import csv
import itertools
import pathlib

import numpy as np

ACTIVE_ROOTS = ("Sisters", "Angels", "Models", "Prospects", "Potentials")
SOLID_SCORE = 0.25


def _percentile(values, percentile):
    return float(np.percentile(values, percentile)) if values else None


def collect_diagnostics(space, settings):
    """Calculate calibration and eligible active-person folder evidence in one pass."""
    photo_rows = []
    calibration_photo_rows = []
    folder_rows = []
    own_scores = []
    other_scores = []
    correct = confident_right = confident_wrong = 0
    calibrated_count = 0

    for key in space.keys:
        photos = space.by_key[key]
        root = key.split("/", 1)[0]
        eligible = root in ACTIVE_ROOTS and len(photos) >= 3
        scores = []
        states = {"agree": 0, "borderline": 0, "outlier": 0}

        for photo in photos:
            if len(photos) >= 2:
                own_centroid = space.centroid(key, skip=photo)
                own_score = float(photo.vec @ own_centroid) if own_centroid is not None else None
                ranking = space.ranking(photo.vec, skip=photo, own=key, source=key)
                best_other = next(
                    ((score, candidate) for score, candidate in ranking if candidate != key),
                    None,
                )
                if own_score is not None and best_other is not None:
                    calibrated_count += 1
                    own_scores.append(own_score)
                    other_scores.append(best_other[0])
                    correct += own_score > best_other[0]
                    if own_score >= settings["assign"] and own_score - best_other[0] >= settings["margin"]:
                        confident_right += 1
                    if best_other[0] >= settings["assign"] and best_other[0] - own_score >= settings["margin"]:
                        confident_wrong += 1
                    if own_score >= settings["assign"] and own_score - best_other[0] >= settings["margin"]:
                        threshold_result = "confident-correct"
                    elif best_other[0] >= settings["assign"] and best_other[0] - own_score >= settings["margin"]:
                        threshold_result = "confident-incorrect"
                    else:
                        threshold_result = "no-confident-assignment"
                    calibration_photo_rows.append({
                        "identity": key,
                        "photo": photo.name,
                        "own_folder_score": own_score,
                        "best_other_identity": best_other[1],
                        "best_other_score": best_other[0],
                        "top_rank_correct": own_score > best_other[0],
                        "threshold_result": threshold_result,
                        "assign_threshold": settings["assign"],
                        "margin_threshold": settings["margin"],
                    })
            else:
                own_score, best_other = None, None

            if eligible:
                state = (
                    "outlier" if own_score is not None and own_score < settings["odd"]
                    else "borderline" if own_score is not None and own_score < SOLID_SCORE
                    else "agree" if own_score is not None else "unscored"
                )
                states[state] += 1
                scores.append(own_score)
                photo_rows.append({
                    "category": root,
                    "identity": key,
                    "photo": photo.name,
                    "folder_score": own_score,
                    "folder_state": state,
                    "best_other_identity": best_other[1] if best_other else "",
                    "best_other_score": best_other[0] if best_other else None,
                    "odd_threshold": settings["odd"],
                    "solid_threshold": SOLID_SCORE,
                    "assign_threshold": settings["assign"],
                    "margin_threshold": settings["margin"],
                })

        if root not in ACTIVE_ROOTS:
            continue
        total = len(photos)
        agree_rate = states["agree"] / total if eligible and total else None
        one_person = (
            eligible and agree_rate >= 0.9
            and states["outlier"] <= max(1, total // 20)
        )
        verdict = (
            "one person"
            if one_person else
            "probably multiple people"
            if eligible and states["outlier"] > total // 10 else
            "mostly one person; inspect flagged photos"
            if eligible else
            "not evaluated: fewer than 3 usable photos"
        )
        folder_rows.append({
            "category": root,
            "identity": key,
            "usable_photos": total,
            "eligible": eligible,
            "agree": states["agree"],
            "borderline": states["borderline"],
            "outlier": states["outlier"],
            "agree_rate": agree_rate,
            "verdict": verdict,
            "odd_threshold": settings["odd"],
            "solid_threshold": SOLID_SCORE,
        })

    pair_scores = list(space.pair_matrix()[1].values())
    same_photo_scores = [
        float(first.vec @ second.vec)
        for key in space.keys
        for first, second in itertools.combinations(space.by_key[key], 2)
    ]
    different_photo_scores = [
        float(first.vec @ second.vec)
        for first_key, second_key in itertools.combinations(space.keys, 2)
        for first in space.by_key[first_key][:4]
        for second in space.by_key[second_key][:4]
    ]

    calibration = {
        "photo_count": len(space.person),
        "identity_count": len(space.keys),
        "eligible_photo_count": calibrated_count,
        "correct_top_rank": correct,
        "correct_top_rank_rate": correct / calibrated_count if calibrated_count else None,
        "confident_right": confident_right,
        "confident_wrong": confident_wrong,
        "assign_threshold": settings["assign"],
        "margin_threshold": settings["margin"],
        "own_p10": _percentile(own_scores, 10),
        "own_median": _percentile(own_scores, 50),
        "own_p90": _percentile(own_scores, 90),
        "best_other_p10": _percentile(other_scores, 10),
        "best_other_median": _percentile(other_scores, 50),
        "best_other_p90": _percentile(other_scores, 90),
        "folder_pair_count": len(pair_scores),
        "folder_pair_median": _percentile(pair_scores, 50),
        "folder_pair_p90": _percentile(pair_scores, 90),
        "folder_pair_p95": _percentile(pair_scores, 95),
        "folder_pair_max": max(pair_scores) if pair_scores else None,
        "same_folder_photo_median": _percentile(same_photo_scores, 50),
        "different_folder_photo_p90": _percentile(different_photo_scores, 90),
        "different_folder_photo_p99": _percentile(different_photo_scores, 99),
    }
    return calibration, calibration_photo_rows, folder_rows, photo_rows


def _write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_report(output_dir, calibration, calibration_photo_rows, folder_rows, photo_rows, timings):
    """Write a new run directory; refuse to overwrite prior diagnostic evidence."""
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    summary_path = output_dir / "folder-consistency.csv"
    photos_path = output_dir / "folder-consistency-photos.csv"
    calibration_path = output_dir / "calibration.csv"
    calibration_photos_path = output_dir / "calibration-photos.csv"

    _write_csv(summary_path, folder_rows, list(folder_rows[0]) if folder_rows else [
        "category", "identity", "usable_photos", "eligible", "agree", "borderline",
        "outlier", "agree_rate", "verdict", "odd_threshold", "solid_threshold",
    ])
    _write_csv(photos_path, photo_rows, [
        "category", "identity", "photo", "folder_score", "folder_state",
        "best_other_identity", "best_other_score", "odd_threshold", "solid_threshold",
        "assign_threshold", "margin_threshold",
    ])
    _write_csv(calibration_path, [calibration], list(calibration))
    _write_csv(calibration_photos_path, calibration_photo_rows, [
        "identity", "photo", "own_folder_score", "best_other_identity", "best_other_score",
        "top_rank_correct", "threshold_result", "assign_threshold", "margin_threshold",
    ])

    eligible_folders = [row for row in folder_rows if row["eligible"]]
    excluded_count = len(folder_rows) - len(eligible_folders)
    flagged = sorted(
        (row for row in photo_rows if row["folder_state"] != "agree"),
        key=lambda row: (
            row["folder_score"] if row["folder_score"] is not None else 1,
            row["identity"].casefold(),
            row["photo"].casefold(),
        ),
    )
    lines = [
        "# Likeness diagnostics",
        "",
        "Read-only diagnostics for this source snapshot and effective settings. "
        "Scores are diagnostic evidence, not identity proof or move instructions.",
        "",
        "## Runtime",
        "",
        "| Stage | Seconds |",
        "| --- | ---: |",
        f"| Library load and embedding/cache check | {timings['load_seconds']:.2f} |",
        f"| Calibration and folder scoring | {timings['score_seconds']:.2f} |",
        f"| Total before report writing | {timings['total_seconds']:.2f} |",
        "",
        "## Library calibration",
        "",
        f"- Scope: {calibration['photo_count']} usable photos in "
        f"{calibration['identity_count']} identities.",
        f"- Eligible leave-one-out comparisons: {calibration['eligible_photo_count']}.",
        f"- Correct identity ranked first: {calibration['correct_top_rank']}/"
        f"{calibration['eligible_photo_count']} "
        f"({calibration['correct_top_rank_rate']:.1%})"
        if calibration["correct_top_rank_rate"] is not None
        else "- Correct identity ranked first: no eligible comparisons.",
        f"- Confident under configured assign/margin: {calibration['confident_right']} "
        f"correct and {calibration['confident_wrong']} incorrect "
        f"(assign {calibration['assign_threshold']:.2f}, margin "
        f"{calibration['margin_threshold']:.2f}).",
        f"- Per-photo calibration evidence: "
        f"[{calibration_photos_path.name}]({calibration_photos_path.name}).",
        f"- Own-folder scores: p10 {calibration['own_p10']:.2f}, "
        f"median {calibration['own_median']:.2f}, p90 {calibration['own_p90']:.2f}."
        if calibration["own_p10"] is not None
        else "- Own-folder scores: unavailable.",
        f"- Best-other scores: p10 {calibration['best_other_p10']:.2f}, "
        f"median {calibration['best_other_median']:.2f}, "
        f"p90 {calibration['best_other_p90']:.2f}."
        if calibration["best_other_p10"] is not None
        else "- Best-other scores: unavailable.",
        "",
        "## Per-folder consistency",
        "",
        f"- Active categories checked: {', '.join(ACTIVE_ROOTS)}.",
        f"- Eligible identities: {len(eligible_folders)}; not evaluated "
        f"(<3 usable photos): {excluded_count}.",
        "- Folder scores compare each photo with the remaining usable photos in its folder.",
        f"- Thresholds: below {folder_rows[0]['odd_threshold']:.2f} outlier; "
        f"{folder_rows[0]['odd_threshold']:.2f} to below {SOLID_SCORE:.2f} borderline; "
        f"{SOLID_SCORE:.2f}+ agree."
        if folder_rows else "- No active identity folders found.",
        f"- Folder results: [{summary_path.name}]({summary_path.name}).",
        f"- Per-photo scores: [{photos_path.name}]({photos_path.name}).",
        "",
        f"### Photos to inspect ({len(flagged)})",
        "",
    ]
    if flagged:
        lines.extend([
            "| Identity | Photo | Folder score | State | Closest other identity | Score |",
            "| --- | --- | ---: | --- | --- | ---: |",
        ])
        lines.extend(
            f"| `{row['identity']}` | `{row['photo']}` | "
            f"{row['folder_score']:.3f} | {row['folder_state']} | "
            f"`{row['best_other_identity'] or '-'}` | "
            f"{row['best_other_score']:.3f} |"
            for row in flagged[:100]
        )
        if len(flagged) > 100:
            lines.append(f"| … | {len(flagged) - 100} more; see CSV | - | - | - | - |")
    else:
        lines.append("No borderline or outlier photos.")
    lines += [
        "",
        f"Calibration metrics: [{calibration_path.name}]({calibration_path.name}).",
        "",
    ]
    (output_dir / "diagnostics.md").write_text("\n".join(lines), encoding="utf-8")
    return {
        "markdown": output_dir / "diagnostics.md",
        "folder_csv": summary_path,
        "photo_csv": photos_path,
        "calibration_csv": calibration_path,
        "calibration_photo_csv": calibration_photos_path,
    }
