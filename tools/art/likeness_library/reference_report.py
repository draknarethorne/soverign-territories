"""Read-only before/after evidence for frozen-reference experiments."""
import collections
import html
import json


def evidence_diagnostics(result):
    diagnostics = []
    for character in result["characters"]:
        folder = character["folder"]
        rows = [row for row in result["rows"] if folder in row["choiceByCharacter"]]
        variants = {}
        for variant in ("baseline", "confirmed"):
            pools = collections.defaultdict(list)
            for row in rows:
                choice = row["choiceByCharacter"][folder]
                score = row["characterScores"][folder][variant]
                if score is not None:
                    pools[choice].append(score)
            positives = [*pools["reference"], *pools["same-not-reference"]]
            negatives = pools["different"]
            variants[variant] = {
                "referenceLOO": pools["reference"],
                "sameNonReference": pools["same-not-reference"],
                "different": negatives, "uncertain": pools["uncertain"],
                "positiveMinimum": min(positives) if positives else None,
                "negativeMaximum": max(negatives) if negatives else None,
                "positiveNegativeRangeOverlap": (
                    max(negatives) >= min(positives) if positives and negatives else None
                ),
                "boundary": "Selected, related examples; reference LOO is not held-out or series-independent.",
            }
        profiles = {}
        for method in ("nearestScore", "secondScore", "topTwoMean"):
            pools = collections.defaultdict(list)
            for row in rows:
                score = row["characterScores"][folder].get("confirmedProfile", {}).get(method)
                if score is not None:
                    pools[row["choiceByCharacter"][folder]].append(score)
            positives = [*pools["reference"], *pools["same-not-reference"]]
            negatives = pools["different"]
            profiles[method] = {
                "referenceLOO": pools["reference"],
                "sameNonReference": pools["same-not-reference"],
                "different": negatives, "uncertain": pools["uncertain"],
                "positiveNegativeRangeOverlap": (
                    max(negatives) >= min(positives) if positives and negatives else None
                ),
                "boundary": "Uncalibrated per-reference evidence, not a new routing rule or independent acceptance.",
            }
        diagnostics.append({"folder": folder, "variants": variants, "confirmedProfiles": profiles})
    return diagnostics


def select_photos(result, *, per_character=3, maximum=80):
    rows = {row["photoId"]: row for row in result["rows"]}
    selected = {
        row["photoId"] for row in result["rows"] if row["choiceByCharacter"]
    }
    for character in result["characters"]:
        folder = character["folder"]
        candidates = [
            row for row in result["rows"]
            if row["qualityEligible"] and not row["choiceByCharacter"]
            and folder in row["characterScores"]
            and row["characterScores"][folder]["baseline"] is not None
            and row["characterScores"][folder]["confirmed"] is not None
        ]
        ordered = sorted(candidates, key=lambda row: (
            -abs(row["characterScores"][folder]["confirmed"] - row["characterScores"][folder]["baseline"]),
            row["photoId"],
        ))
        selected.update(row["photoId"] for row in ordered[:per_character])
    if len(selected) > maximum:
        raise ValueError(f"reference result report exceeds {maximum} displayed-photo budget")
    if not selected <= rows.keys():
        raise ValueError("reference report selected unknown photos")
    return sorted(selected)


def render(result, images, *, outcomes=None):
    escape = html.escape

    def score(value):
        return "Unavailable" if value is None else f"{value:.3f}"

    def image(pid):
        record = images[pid]
        return (
            f'<a href="{escape(record["href"], quote=True)}" target="_blank" rel="noopener">'
            f'<img class="full" src="{record["full"]}" alt="Full photo {escape(pid)}">'
            f'<img class="face" src="{record["face"]}" alt="Face {escape(pid)}"></a>'
        )

    rows = {row["photoId"]: row for row in result["rows"]}
    member_rows = {row["photoId"]: row for row in outcomes["rows"]} if outcomes else {}
    sections, options, summaries = [], [], []
    ordered = sorted(result["characters"], key=lambda item: (
        item["folder"] != "Angels/angelica", item["folder"].casefold(),
    ))
    for index, character in enumerate(ordered):
        folder = character["folder"]
        options.append(f'<option value="{index}">{escape(folder)}</option>')
        known = [
            row for row in result["rows"] if folder in row["choiceByCharacter"]
        ]
        choices = collections.Counter(row["choiceByCharacter"][folder] for row in known)
        summaries.append(
            f'<tr><td>{escape(folder)}</td><td>{character["baselineReferenceCount"]}</td>'
            f'<td>{character["confirmedReferenceCount"]}</td>'
            f'<td>{escape(json.dumps(dict(choices), sort_keys=True))}</td></tr>'
        )
        selected = [row for row in known if row["photoId"] in images]
        extra = sorted(
            (rows[pid] for pid in images if not rows[pid]["choiceByCharacter"]
             and folder in rows[pid]["characterScores"]),
            key=lambda row: (
                -abs((row["characterScores"][folder]["confirmed"] or 0)
                     - (row["characterScores"][folder]["baseline"] or 0)),
                row["photoId"],
            ),
        )[:3]
        cards = []
        for row in [*sorted(selected, key=lambda row: row["photoId"]), *extra]:
            pid = row["photoId"]
            scores = row["characterScores"][folder]
            profile = scores.get("confirmedProfile", {})
            choice = row["choiceByCharacter"].get(folder, "Unlabelled score-change example - not a proposed move")
            training = (
                "Reference example: self excluded; training diagnostic, NOT held-out accuracy."
                if choice == "reference" else
                "Non-reference judgment; not guaranteed series-independent from the references."
                if folder in row["choiceByCharacter"] else
                "No human character label. Score change is not evidence that identity changed."
            )
            comparisons = []
            for name in ("baseline", "confirmed"):
                evaluation = row[name]
                rivals = "; ".join(
                    f'{rival["folder"]}: {rival["score"]:.3f}' for rival in evaluation["rivals"]
                )
                comparisons.append(
                    f'<details><summary>{name.title()} full-competition policy probe</summary>'
                    f'<p>Own: {score(evaluation["ownScore"])}; rivals: {escape(rivals)}</p>'
                    f'<pre>{escape(json.dumps(evaluation["policyDecision"], indent=2))}</pre></details>'
                )
            member = member_rows.get(pid)
            proposal = ""
            if member:
                placement = member["placement"]
                proposal = (
                    '<section class="notice"><strong>Placement proposal: '
                    f'{escape(placement["action"])}</strong>'
                    f'<p>Target: {escape(placement["targetFolder"] or "Unresolved")} '
                    f'{escape(placement["targetBucket"] or "")}</p>'
                    f'<p>{escape(placement["reason"])}. Execution: not authorized.</p>'
                    f'<p>Safeguards: {escape(", ".join(placement["blockers"]) or "None flagged")}. '
                    f'Existing probe: {escape(placement["policyAgreement"])}.</p>'
                    f'<p>Reference status: {escape(member["reference"]["status"])}</p>'
                    '<details><summary>Reference changes, direct evidence and safeguards</summary>'
                    f'<pre>{escape(json.dumps(member, indent=2))}</pre></details></section>'
                )
            cards.append(
                f'<article>{image(pid)}<small>{escape(pid)}</small>'
                f'<p><strong>{escape(choice)}</strong></p><p>{escape(training)}</p>'
                f'<p>Installed home: {escape(row["currentFolder"])}</p>'
                f'{proposal}'
                '<table><tr><th>Against this character</th><th>Baseline</th><th>Confirmed refs</th></tr>'
                f'<tr><td>Query-excluded mean score</td><td>{score(scores["baseline"])}</td>'
                f'<td>{score(scores["confirmed"])}</td></tr>'
                f'<tr><td>Independent reference support</td><td>{scores["baselineSupport"]}</td>'
                f'<td>{scores["confirmedSupport"]}</td></tr></table>'
                '<p>Confirmed individual-reference profile (not routing thresholds): '
                f'nearest {score(profile.get("nearestScore"))}; '
                f'second {score(profile.get("secondScore"))}; '
                f'top-two mean {score(profile.get("topTwoMean"))}. '
                'Query and identical-content reference measurements are excluded.</p>'
                f'{"".join(comparisons)}</article>'
            )
        sections.append(
            f'<section data-group="{index}"{" hidden" if index else ""}><h2>{escape(folder)}</h2>'
            '<p>Human-confirmed reference examples remain frozen. Other photos do not join the references during this trial.</p>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )
    notices = "".join(f"<li>{escape(text)}</li>" for text in result["limits"])
    transfers = escape(json.dumps(result["referenceTransfers"], indent=2))
    summary = escape(json.dumps(result["summary"], indent=2))
    evidence = evidence_diagnostics(result)
    diagnostics = escape(json.dumps(evidence, indent=2))
    separation = []
    for group in evidence:
        value = group["variants"]["confirmed"]
        overlap = value["positiveNegativeRangeOverlap"]
        separation.append(
            f'<tr><td>{escape(group["folder"])}</td>'
            f'<td>{score(value["positiveMinimum"])}</td><td>{score(value["negativeMaximum"])}</td>'
            f'<td>{"Overlap remains" if overlap else "No overlap in this sample" if overlap is False else "No negative examples supplied"}</td></tr>'
        )
    statistics = result["summary"]
    headlines = escape(
        f'{statistics["photoCount"]} saved photo rows conserved; '
        f'{statistics.get("eligibleCount", "not recorded")} eligible measurements. '
        f'{statistics.get("changedTopRivalCount", "not recorded")} photos change their strongest rival. '
        f'Existing-policy proposed moves: {statistics.get("policyMoves", {})}.'
    )
    member_summary = ""
    if outcomes:
        counts = outcomes["summary"]
        counts_text = "; ".join(f"{key}: {value}" for key, value in counts["placementActions"].items())
        outcome_rows = []
        for member in outcomes["rows"]:
            placement, reference = member["placement"], member["reference"]
            changed = bool(reference.get("changes")) or placement["action"] in {"recover", "reassess", "policy-proposal"}
            conflict = "human-evidence-conflict" in placement["blockers"]
            change_text = "; ".join(
                f'{"Add" if change["after"] else "Withdraw"} {change["folder"]}: {change["reason"]}'
                for change in reference.get("changes", [])
            ) or "No reference change"
            target = placement["targetFolder"] or "Unresolved"
            outcome_rows.append(
                f'<tr data-outcome-action="{escape(placement["action"], quote=True)}" '
                f'data-reference-change="{str(bool(reference.get("changes"))).lower()}" '
                f'data-proposed-change="{str(changed or conflict).lower()}" '
                f'data-conflict="{str(conflict).lower()}">'
                f'<td>{escape(member["photoId"])}</td>'
                f'<td>{escape(member.get("currentFolder", ""))}</td>'
                f'<td>{escape(placement["action"])}</td><td>{escape(target)}</td>'
                f'<td>{escape(change_text)}</td>'
                f'<td>{escape(placement["reason"])}<br>'
                f'Policy probe: {escape(member["policyProbe"]["reason"])}<br>'
                f'Safeguards: {escape(", ".join(placement["blockers"]) or "None flagged")}</td></tr>'
            )
        member_summary = (
            '<h2>Per-photo proposed outcomes</h2>'
            f'<p><strong>{escape(counts_text)}</strong></p>'
            f'<p>Reference additions: {counts["referenceAdditions"]}; '
            f'withdrawals: {counts["referenceWithdrawals"]}; '
            f'photos with conflicting human evidence: {counts["conflictPhotoCount"]}. '
            'Executable moves: zero. These proposals do not change installed placements.</p>'
            '<p>Recover/retain proposals come from your explicit character answers, not newly inferred identity. '
            'Unreviewed photos remain holds unless the unchanged policy proposes a move. '
            'Reference withdrawals do not mean the photo is necessarily a different person.</p>'
            '<p><a href="member-outcomes.json" target="_blank" rel="noopener">'
            'Full-population member/reference ledger</a> (all photo IDs and reasons).</p>'
            '<details><summary>Browse proposed changes and holds for every photo</summary>'
            '<p><label>Outcome <select id="member-filter">'
            '<option value="changes">Proposed changes / conflicts</option>'
            '<option value="recover">Recover</option><option value="reassess">Reassess</option>'
            '<option value="reference-change">Reference changes</option>'
            '<option value="conflict">Conflicting evidence</option>'
            '<option value="retain">Retain</option><option value="hold">Hold</option>'
            '<option value="all">All photos</option></select></label> '
            '<label>Search <input id="member-search" type="search" placeholder="Photo ID, folder or reason"></label></p>'
            '<p id="member-count" role="status"></p><div class="outcome-scroll">'
            '<table><thead><tr><th>Photo ID</th><th>Current folder</th><th>Placement proposal</th>'
            '<th>Target folder</th><th>Reference proposal</th><th>Reason / safeguards</th></tr></thead>'
            f'<tbody>{"".join(outcome_rows)}</tbody></table></div></details>'
        )
    return TEMPLATE.replace("{{OPTIONS}}", "".join(options)).replace(
        "{{SUMMARY_ROWS}}", "".join(summaries),
    ).replace("{{SECTIONS}}", "".join(sections)).replace(
        "{{SUMMARY}}", summary,
    ).replace("{{LIMITS}}", notices).replace("{{TRANSFERS}}", transfers).replace(
        "{{DIAGNOSTICS}}", diagnostics,
    ).replace("{{SEPARATION}}", "".join(separation)).replace(
        "{{HEADLINES}}", headlines,
    ).replace(
        "{{MEMBER_OUTCOMES}}", member_summary,
    )


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Frozen-reference experiment results</title><style>
body{background:#15191f;color:#e3e8ef;font:16px system-ui;margin:20px;line-height:1.45}
header,main{max-width:1450px;margin:auto}a{color:#8fceff}.notice{border-left:4px solid #e6b458;padding:12px;background:#282c32}
nav{position:sticky;top:0;background:#20262e;padding:12px;z-index:2;display:flex;gap:12px}
button,select{font:inherit;padding:8px;max-width:100%}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
article{background:#20262e;border:1px solid #536071;padding:12px;border-radius:6px;overflow-wrap:anywhere}
article a{display:flex;gap:6px;align-items:start}img{object-fit:contain;max-width:100%}
.full{width:72%;height:360px}.face{width:26%;height:150px}body.faces .full{display:none}
body.faces .face{width:100%;height:300px}small{display:block;color:#b7c8db}
table{border-collapse:collapse;max-width:100%;font-size:14px}td,th{border:1px solid #58616d;padding:7px;text-align:left}
pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin-top:12px}[hidden]{display:none!important}
.outcome-scroll{max-height:650px;overflow:auto}input{font:inherit;padding:8px;max-width:100%}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:550px){.grid{grid-template-columns:1fr}}
</style></head><body><header>
<h1>Frozen-reference experiment: results, not another assessment</h1>
<p class="notice"><strong>No photos, references, protections or workflows were changed in the library.</strong>
This is a full saved-population score comparison with a one-pass shared-policy probe, not a completed routing replay or rebase.</p>
<p>Your confirmed character references replace only the six sampled character reference sets in the experiment.
Those reference photos stop representing any other identity in the experimental reference map.
Everything else stays frozen. Query images never score against themselves, even across folders.</p>
<p>Face score is not identity probability. Changed scores and policy suggestions are not approved destinations.
No new acceptance threshold, appearance classifier or model download has been introduced.</p>
<h2>Measured result</h2><p><strong>{{HEADLINES}}</strong></p>
{{MEMBER_OUTCOMES}}
<p>Reference repair changes the evidence, but is not by itself a cleanup engine.
The existing membership gates remain in force; their hold reasons appear on every card below.
Zero proposed moves does not mean every installed member is correct.</p>
<table><thead><tr><th>Character</th><th>Baseline references</th><th>Confirmed references</th><th>Your sampled choices</th></tr></thead>
<tbody>{{SUMMARY_ROWS}}</tbody></table>
<h2>Can one mean-face threshold separate your known examples?</h2>
<table><thead><tr><th>Character</th><th>Lowest endorsed score</th><th>Highest different-person score</th><th>Diagnostic</th></tr></thead>
<tbody>{{SEPARATION}}</tbody></table>
<p>Endorsed scores include query-excluded reference examples and same/non-reference photos.
Reference examples are training diagnostics, not held-out acceptance.
Where the ranges overlap, no single threshold on this mean score can separate all these labelled examples.
No negatives supplied means unknown discrimination, not a clean result.</p>
<details><summary>Conservation, arithmetic checks, score changes and policy-probe counts</summary><pre>{{SUMMARY}}</pre></details>
<details><summary>Known-example score separation (diagnostic, not acceptance)</summary><pre>{{DIAGNOSTICS}}</pre></details>
<details><summary>Explicit experimental reference withdrawals from other identities</summary><pre>{{TRANSFERS}}</pre></details>
<details><summary>Evidence limits and evaluation boundary</summary><ul>{{LIMITS}}</ul></details>
<h2>What this step builds</h2>
<ol><li>A separately bound reference-selection artifact from your character answers.</li>
<li>A full-population before/after scoring experiment with frozen competitor context and query exclusion.</li>
<li>Existing membership-policy probes that expose protection, support and admission blockers instead of bypassing them.</li>
<li>Concrete regression examples for the next member/reference implementation. These results are not held-out acceptance.</li></ol>
<h2>Build decisions from this increment</h2><ol>
<li>Keep reference eligibility separate from Gallery placement, protection and art selection.</li>
<li>Keep individually confirmed reference vectors and provenance; do not make a single average the only identity representation.</li>
<li>Next test a per-member evidence profile and abstention gate against the known lookalikes, before automatic reference growth.</li>
<li>Then test bounded series/outfit and hairstyle support on unresolved cases, with missing cues explicit.
No physical-proportion classifier or inferred biological family relation is part of this experiment.</li>
<li>Integrate only after full routing/reference reconstruction, leakage-safe evaluation and numeric acceptance;
then perform one approved sandbox install with real viewer checks.</li></ol>
</header><main><nav><label>Character <select id="character">{{OPTIONS}}</select></label>
<button id="next">Next character</button><button id="view">Face crops only / full + face</button></nav>
{{SECTIONS}}</main><script>
"use strict";
const selector=document.getElementById("character"),groups=[...document.querySelectorAll("[data-group]")];
function show(){for(const section of groups)section.hidden=section.dataset.group!==selector.value;
 document.getElementById("next").disabled=Number(selector.value)===groups.length-1;}
selector.onchange=show;document.getElementById("next").onclick=()=>{selector.selectedIndex++;show();};
document.getElementById("view").onclick=()=>document.body.classList.toggle("faces");show();
const memberFilter=document.getElementById("member-filter"),memberSearch=document.getElementById("member-search");
if(memberFilter){
 const memberRows=[...document.querySelectorAll("[data-outcome-action]")];
 function filterMembers(){
  const kind=memberFilter.value,term=memberSearch.value.trim().toLowerCase();let visible=0;
  for(const row of memberRows){
   const matches=kind==="all"||kind==="changes"&&row.dataset.proposedChange==="true"||
    kind==="reference-change"&&row.dataset.referenceChange==="true"||
    kind==="conflict"&&row.dataset.conflict==="true"||kind===row.dataset.outcomeAction;
   row.hidden=!matches||!row.textContent.toLowerCase().includes(term);if(!row.hidden)visible++;
  }
  document.getElementById("member-count").textContent=visible+" / "+memberRows.length+" photos shown. No changes installed.";
 }
 memberFilter.onchange=filterMembers;memberSearch.oninput=filterMembers;filterMembers();
}
</script></body></html>
"""
