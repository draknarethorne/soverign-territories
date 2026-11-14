"""Replay frozen references through shared membership gates and publish photo comparisons."""
import argparse
import copy
import html
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art import likeness_disposition_trial as source  # noqa: E402
from tools.art.likeness_library import (  # noqa: E402
    appearance_context, candidate_replay, fragment_evidence, fragment_report,
    fragment_review, policy, protection, refinement, rejections, review_packet, shadow,
)
from tools.art.likeness_review_packet import output_path  # noqa: E402


def codes():
    modules = (source, appearance_context, candidate_replay, fragment_evidence, fragment_report,
               fragment_review, policy, protection, refinement, rejections, review_packet, shadow)
    paths = [pathlib.Path(__file__), *(pathlib.Path(module.__file__) for module in modules)]
    return {str(p.resolve()): shadow.digest(p) for p in paths}


def load(root):
    packet, answers, ledger, _, bindings = source.load(root)
    def find(name):
        found = [pathlib.Path(p) for p in bindings if pathlib.Path(p).name == name]
        if len(found) != 1:
            raise ValueError(f"expected exactly one bound {name}")
        return found[0]
    candidate = json.loads(find("realignment.json").read_bytes())
    if fragment_review.digest(candidate) != packet["candidateSHA256"]:
        raise ValueError("candidate no longer matches reviewed reference source")
    if fragment_review.digest(answers) != ledger["answersSHA256"]:
        raise ValueError("candidate answers differ from frozen repair source")
    experiment = find("experiment.json").parent
    run, vectors, _, binding = review_packet.load_experiment(experiment)
    cache_path = pathlib.Path(binding["sourceRun"]) / "likeness-cache.json"
    cache = json.loads(cache_path.read_bytes())
    bindings[str(cache_path)] = shadow.digest(cache_path)
    checkpoints = [pathlib.Path(p) for p in bindings if pathlib.Path(p).suffix == ".safetensors"]
    if len(checkpoints) != 1:
        raise ValueError("expected exactly one already-bound local context checkpoint")
    return packet, ledger, candidate, run, vectors, cache, checkpoints[0], bindings


def check(out, bindings):
    receipt = json.loads((out / "receipt.json").read_bytes())
    if receipt["inputs"] != bindings or receipt["code"] != codes():
        raise ValueError("candidate replay input/code changed; use a new --out")
    if not {"candidate.json", "packet.json", "display.json", "context.json", "index.html"} <= receipt["outputs"].keys():
        raise ValueError("candidate replay receipt incomplete")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, name)) != digest:
            raise ValueError(f"candidate replay output changed: {name}")
    for image in json.loads((out / "display.json").read_bytes()).values():
        if shadow.digest(pathlib.Path(image["path"])) != image["sha256"]:
            raise ValueError("candidate replay displayed source changed")
    packet = json.loads((out / "packet.json").read_bytes())
    if fragment_review.digest({k: v for k, v in packet.items() if k != "packetSHA256"}) != packet["packetSHA256"]:
        raise ValueError("candidate replay packet binding differs")
    return packet


def reuse(out, bindings):
    """Reuse frozen numerical results across publisher changes, never scorer changes."""
    receipt = json.loads((out / "receipt.json").read_bytes())
    if (receipt["kind"] != "connected-candidate-replay-receipt"
            or receipt["inputs"] != bindings or receipt["directPairLabelsInScoring"] != 0
            or receipt["reverseVerified"] is not True or receipt["libraryWrites"] != 0):
        raise ValueError("reusable candidate recipe/input contract differs")
    publisher = str(pathlib.Path(__file__).resolve())
    old_helpers = {str(pathlib.Path(p).resolve()): h for p, h in receipt["code"].items()
                   if str(pathlib.Path(p).resolve()) != publisher}
    if old_helpers != {p: h for p, h in codes().items() if p != publisher}:
        raise ValueError("cannot reuse candidate after analysis/helper code changes")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, name)) != digest:
            raise ValueError(f"reusable candidate output changed: {name}")
    required = {"candidate.json", "packet.json", "display.json", "context.json", "index.html"}
    if not required <= receipt["outputs"].keys():
        raise ValueError("reusable candidate output contract incomplete")
    packet = json.loads((out / "packet.json").read_bytes())
    if fragment_review.digest({k: v for k, v in packet.items() if k != "packetSHA256"}) != packet["packetSHA256"]:
        raise ValueError("reusable candidate packet binding differs")
    for image in json.loads((out / "display.json").read_bytes()).values():
        if shadow.digest(pathlib.Path(image["path"])) != image["sha256"]:
            raise ValueError("reusable candidate source photo changed")
    result = json.loads((out / "candidate.json").read_bytes())
    if packet["evidenceSHA256"] != fragment_review.digest(result):
        raise ValueError("reusable candidate evidence binding differs")
    bound = {**bindings, str(out / "receipt.json"): shadow.digest(out / "receipt.json"),
             **{str(out / name): h for name, h in receipt["outputs"].items()}}
    return result, packet, json.loads((out / "context.json").read_bytes()), bound


def validate_evaluation(packet, result, value):
    if (not isinstance(value, dict)
            or set(value) != {"schemaVersion", "kind", "packetSHA256", "candidateSHA256",
                              "identityAnswers", "recommendations"}
            or type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1
            or value["kind"] != "candidate-recommendation-evaluation"
            or value["packetSHA256"] != packet["packetSHA256"]
            or value["candidateSHA256"] != fragment_review.digest(result)
            or not isinstance(value["recommendations"], list)):
        raise ValueError("recommendation evaluation schema/packet/candidate mismatch")
    labels = fragment_review.validate_answers(packet, value["identityAnswers"])
    cases = {case["id"] for case in packet["cases"]}
    seen = set()
    for row in value["recommendations"]:
        if (not isinstance(row, dict) or set(row) != {"caseId", "judgment", "reason"}
                or not isinstance(row["caseId"], str) or row["caseId"] not in cases
                or row["caseId"] in seen or row["judgment"] not in ("agree", "disagree", "uncertain")
                or not isinstance(row["reason"], str) or len(row["reason"]) > 4000
                or row["judgment"] == "disagree" and not row["reason"].strip()):
            raise ValueError("invalid/duplicate recommendation or missing disagreement reason")
        seen.add(row["caseId"])
    return {"imageAnswers": labels, "recommendations": len(seen), "total": len(cases)}


def split_report(args, out, reused, candidate, run, vectors, cache, ledger):
    from tools.art.likeness_library import split_diagnostics
    if not reused or args.prior_answers or args.answers or args.evaluation:
        raise ValueError("--split-evaluation requires --reuse-result and no other answer options")
    if not args.split_evaluation.is_absolute():
        raise ValueError("--split-evaluation must be absolute")
    result, packet, _, bindings = reused
    evaluation = json.loads(args.split_evaluation.read_bytes())
    counts = validate_evaluation(packet, result, evaluation)
    bindings = {**bindings, str(args.split_evaluation): shadow.digest(args.split_evaluation)}
    split_codes = {**codes(), str(pathlib.Path(split_diagnostics.__file__).resolve()):
                   shadow.digest(pathlib.Path(split_diagnostics.__file__))}
    def verify(directory):
        receipt = json.loads((directory / "receipt.json").read_bytes())
        if (receipt["kind"] != "split-investigation-receipt"
                or receipt["inputs"] != bindings or receipt["code"] != split_codes
                or not {"splits.json", "display.json", "index.html"} <= receipt["outputs"].keys()):
            raise ValueError("split report input/code/output contract changed")
        for path, digest in bindings.items():
            if shadow.digest(pathlib.Path(path)) != digest:
                raise ValueError("split report source changed")
        for name, digest in receipt["outputs"].items():
            if shadow.digest(review_packet.safe_path(directory, name)) != digest:
                raise ValueError(f"split report output changed: {name}")
        for row in json.loads((directory / "display.json").read_bytes()).values():
            if shadow.digest(pathlib.Path(row["path"])) != row["sha256"]:
                raise ValueError("split report displayed source changed")
    if args.check or args.apply and out.exists():
        verify(out)
        print(f"Verified split investigation: {out / 'index.html'}")
        return 0
    repaired = candidate_replay.repaired_references(candidate, ledger)
    investigation = split_diagnostics.build(repaired, run, vectors, packet, evaluation, result, ledger)
    reverse_candidate = copy.deepcopy(repaired)
    for key in ("rows", "identities", "appearances"):
        reverse_candidate[key].reverse()
    reverse_evaluation = copy.deepcopy(evaluation)
    reverse_evaluation["recommendations"].reverse()
    reverse_evaluation["identityAnswers"]["decisions"].reverse()
    reverse_run = copy.deepcopy(run)
    reverse_run["photos"].reverse()
    reversed_result = split_diagnostics.build(
        reverse_candidate, reverse_run, vectors, packet, reverse_evaluation, result, ledger,
    )
    # Serialized feedback provenance is order-sensitive; decisions must not be.
    reversed_result["evaluationSHA256"] = investigation["evaluationSHA256"]
    if reversed_result != investigation:
        raise ValueError("split investigation differs under reversed inputs")
    review_packet.image_assets(investigation, run, cache, out, write=False)
    print("Validated evaluation:", counts)
    print("Split scope:", investigation["summary"])
    if not args.apply:
        print("Preview only: frozen vectors, complete scoped member evidence; no models, output writes or installed changes.")
        return 0
    staging = out.with_name(out.name + ".partial")
    staging.mkdir(parents=True, exist_ok=False)
    images, outputs = review_packet.image_assets(investigation, run, cache, staging, write=True)
    for name, value in (("splits.json", investigation), ("display.json", images)):
        (staging / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        outputs[name] = shadow.digest(staging / name)
    (staging / "index.html").write_text(split_diagnostics.render(investigation, images), encoding="utf-8")
    outputs["index.html"] = shadow.digest(staging / "index.html")
    if any(shadow.digest(pathlib.Path(p)) != h for p, h in {**bindings, **split_codes}.items()):
        raise ValueError("split investigation source/code changed during publication")
    receipt = {"schemaVersion": 1, "kind": "split-investigation-receipt", "inputs": bindings,
               "code": split_codes, "outputs": outputs, "reverseVerified": True,
               "libraryWrites": 0, "modelCalls": 0}
    (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    verify(staging)
    staging.rename(out)
    print(f"Published split investigation: {out / 'index.html'}")
    return 0


def render(packet, images, context, result, prior_answers=None):
    document = fragment_report.render(packet, images, context)
    document = document.replace("</style>", "p,h1,h2,summary{overflow-wrap:anywhere}</style>", 1)
    document = document.replace("<title>Split identities and mixed references</title>",
                                "<title>Candidate replay: where would these photos go?</title>")
    document = document.replace("Suggested identity — may contain exceptions",
                                "Outside identity for comparison — NOT necessarily a move")
    document = document.replace("Current identity — not assumed right", "Current identity — evaluate its examples")
    document = document.replace("Suggested identity <select", "Compared outside identity <select")
    document = document.replace("Suggested only</button>", "Outside identity only</button>")
    document = document.replace("Suggested reference context", "Outside reference context")
    document = document.replace("No new question is prefilled from an earlier group-level answer.",
                                "Previously returned exact photo labels can be restored; action agreement is separate.")
    document = document.replace('<p id="reason"></p>', '<details><summary>Case selection / audit detail</summary>'
                                '<p id="reason"></p></details>')
    document = document.replace('<p id="progress" role="status"></p>', (
        '<p id="progress" role="status"></p>'
        '<section class="panel" id="recommendation"><h2>1. What the automation recommends</h2>'
        '<p id="action-title" class="notice"></p><p id="action-location"></p>'
        '<p id="action-reason"></p><p id="action-scores"></p><p id="rival-purpose"></p>'
        '<p>Scores are face-vector similarities, not probabilities. They compare this photo '
        'against frozen reference subgroups; context is not part of this decision.</p>'
        '<label>Do you agree with this action? <select id="action-agreement">'
        '<option value="unreviewed">Not evaluated</option><option value="agree">Agree</option>'
        '<option value="disagree">Disagree</option><option value="uncertain">Cannot tell</option></select></label>'
        '<label>Why / what should happen instead? (required for disagreement)'
        '<textarea id="action-explanation" maxlength="4000" rows="3"></textarea></label>'
        '<p id="action-feedback-status" role="status"></p>'
        '<p>Agreeing with HOLD means keeping the current placement for now. It does NOT mean '
        'the two identities are different. A split can be real even when no move is recommended. '
        'A move proposal does not choose the final canonical identity or authorize installation.</p></section>'
    ))
    document = document.replace("<h2>Which intended identities fit the query?</h2>",
                                "<h2>2. Which identities and exact photos are the same person?</h2>")
    document = document.replace('<button id="export">Export answers / download JSON</button>',
                                '<button id="export-evaluation">Export evaluation + image answers</button>'
                                '<button id="export">Export image answers only</button>')
    document = document.replace("<h1>Split identities or mixed references?</h1>", (
        "<h1>Candidate replay: where would these photos go?</h1>"
        "<p class=notice><strong>Automation actions and comparison evidence — evaluated separately.</strong> "
        "Each case below states the installed location, proposed destination or hold, and why. "
        "A HOLD keeps the photo in its current place; a matching identity can still be an appearance association. "
        "Nothing has been installed. This is one frozen candidate pass, not a finished rebase.</p>"
        "<p>Use the photo comparisons below to judge whether each identity fits and flag individual exceptions. "
        "Both means an identity split; Neither means neither example represents this photo. "
        "Do not interpret the proposed destination as a correct answer.</p>"
        "<details><summary>Whole-population result and unfinished work</summary><pre>"
        + html.escape(json.dumps(result["summary"], indent=2))
        + "</pre><p>All photos retained. Saved protection/quality/workflow/rejection safeguards remain. "
        "No direct pair labels enter scoring; reference sets still contain human development decisions. "
        "Secondary context is shown, not fused into identity. Series/hair detection, staged reference growth, "
        "converged incremental processing, fictional-family assignment and actual rebase/viewer acceptance remain open. "
        "Local Qwen/InternVL is not installed or selected; no model download or external upload.</p>"
        '<a href="candidate.json">All per-photo current/proposed destinations and reasons</a></details>'
    ))
    data = {"rows": result.get("rows", []), "candidateSHA256": fragment_review.digest(result),
            "priorAnswers": prior_answers}
    payload = json.dumps(data, allow_nan=False).replace("<", "\\u003c")
    return document.replace("</body>", '<script id="recommendation-data" type="application/json">'
                            + payload + "</script><script>" + EVALUATION_SCRIPT + "</script></body>")


EVALUATION_SCRIPT = r"""
"use strict";
const evaluationData=JSON.parse(el("recommendation-data").textContent);
const outcomeRows=new Map(evaluationData.rows.map(r=>[r.photoId,r]));
let actionAnswers=new Map();
const actionLabels=["agree","disagree","uncertain"];
function captureAction(){
 const judgment=el("action-agreement").value,reason=el("action-explanation").value;
 if(judgment==="unreviewed"&&!reason)actionAnswers.delete(p.cases[index].id);
 else actionAnswers.set(p.cases[index].id,{caseId:p.cases[index].id,judgment,reason});
 dirty=true;
 el("action-feedback-status").textContent=judgment==="disagree"&&!reason.trim()
  ?"Add a reason before exporting. Your draft is retained."
  :"Evaluation draft retained in this page; export before stopping.";
}
function actionSummary(){
 const c=p.cases[index],row=outcomeRows.get(c.photoId),d=row.candidateDecision;
 const own=row.own?.subgroupScore,rival=row.topCandidates.find(r=>r.folder===c.targetFolder);
 const score=v=>typeof v==="number"?v.toFixed(3):"unavailable";
 write("action-title",d.decision==="move"?"MOVE PROPOSAL — not installed":"HOLD — KEEP CURRENT LOCATION");
 write("action-location","Current: "+row.currentDestination+
  (d.decision==="move"?" | Proposed: "+d.destination:" | Proposed destination: none."));
 write("action-reason","Decision reason: "+d.reason);
 write("action-scores","Current subgroup score: "+score(own)+" | Outside subgroup score: "+score(rival?.subgroupScore)+
  " | Outside minus current: "+score(typeof own==="number"&&typeof rival?.subgroupScore==="number"
    ?rival.subgroupScore-own:null)+" | Independent outside support: "+(rival?.supportCount??"unavailable"));
 write("rival-purpose",d.decision==="move"
  ?"The outside identity is the policy's proposed destination. Judge the action above, then separately label identity compatibility below."
  :"The outside identity is a diagnostic rival, NOT a recommended move or an established association. "+
   "We need both correct and incorrect rivals to evaluate split identities and mixed references.");
 const saved=actionAnswers.get(c.id);
 el("action-agreement").value=saved?.judgment||"unreviewed";
 el("action-explanation").value=saved?.reason||"";
 write("action-feedback-status",saved?"Evaluation draft restored. Export before stopping.":"Action not evaluated; image labels are separate.");
 write("question","Compare "+c.currentFolder+" with "+c.targetFolder+": same person, different people, or mixed examples?");
}
const originalShow=show;
show=function(){originalShow();actionSummary();};
el("action-agreement").onchange=captureAction;
el("action-explanation").oninput=captureAction;
function validateActions(rows){
 if(!Array.isArray(rows))throw Error("Recommendation evaluations must be a list");
 const seen=new Set();
 for(const a of rows){
  if(!a||Object.keys(a).sort().join(",")!=="caseId,judgment,reason"||!cases.has(a.caseId)||
   seen.has(a.caseId)||!actionLabels.includes(a.judgment)||typeof a.reason!=="string"||
   a.reason.length>4000||(a.judgment==="disagree"&&!a.reason.trim()))
    throw Error("Choose an action judgment; disagreement requires a reason");
  seen.add(a.caseId);
 }
}
el("export-evaluation").onclick=()=>{
 try{
  validateActions([...actionAnswers.values()]);
  if(hasDraft()&&!record(false))return;
  const identityAnswers={schemaVersion:1,kind:"identity-fragment-answers",packetSHA256:p.packetSHA256,
   decisions:[...answers].sort((a,b)=>a.caseId.localeCompare(b.caseId))};
  valid(identityAnswers.decisions);
  const value={schemaVersion:1,kind:"candidate-recommendation-evaluation",packetSHA256:p.packetSHA256,
   candidateSHA256:evaluationData.candidateSHA256,identityAnswers,
   recommendations:[...actionAnswers.values()].sort((a,b)=>a.caseId.localeCompare(b.caseId))};
  const text=JSON.stringify(value,null,2);el("json").value=text;el("transfer").open=true;
  const url=URL.createObjectURL(new Blob([text],{type:"application/json"}));
  const a=document.createElement("a");a.href=url;a.download="candidate_evaluation_"+p.packetSHA256.slice(0,12)+".json";
  document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  write("status","Export contains "+value.recommendations.length+" action evaluations and "+
   identityAnswers.decisions.length+" image-label cases. Verify your download or copy the JSON below.");
 }catch(error){write("status","Evaluation export refused: "+error.message+". Drafts remain; copy/export after correcting.");}
};
const importImages=el("import").onclick;
el("import").onclick=()=>{
 try{
  const value=JSON.parse(el("json").value);
  if(value.kind!=="candidate-recommendation-evaluation"){importImages();return;}
  if(Object.keys(value).sort().join(",")!=="candidateSHA256,identityAnswers,kind,packetSHA256,recommendations,schemaVersion"||
   value.schemaVersion!==1||value.packetSHA256!==p.packetSHA256||
   value.candidateSHA256!==evaluationData.candidateSHA256)throw Error("Evaluation packet/candidate mismatch");
  const identity=value.identityAnswers;
  if(!identity||Object.keys(identity).sort().join(",")!=="decisions,kind,packetSHA256,schemaVersion"||
   identity.schemaVersion!==1||identity.kind!=="identity-fragment-answers"||
   identity.packetSHA256!==p.packetSHA256)throw Error("Image answers schema/packet mismatch");
  valid(identity.decisions);validateActions(value.recommendations);
  actionAnswers=new Map(value.recommendations.map(a=>[a.caseId,a]));
  el("json").value=JSON.stringify(identity);importImages();el("json").value=JSON.stringify(value,null,2);
  dirty=actionAnswers.size>0;
  write("status",value.recommendations.length+" action evaluations and "+identity.decisions.length+" image cases imported.");
 }catch(error){write("status","Evaluation import refused: "+error.message+". Existing answers unchanged.");}
};
if(evaluationData.priorAnswers){
 el("json").value=JSON.stringify(evaluationData.priorAnswers);importImages();
 write("status","Your "+answers.length+" earlier image-label cases are loaded unchanged. "+
  "No need to answer them again. Action agreement is new and starts unevaluated.");
}
actionSummary();
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True, help="Absolute verified reconciliation report")
    parser.add_argument("--out", required=True, help="New absolute reports\\likeness-reassessment\\NAME")
    parser.add_argument("--answers", type=pathlib.Path, help="Validate returned packet answers with --check")
    parser.add_argument("--evaluation", type=pathlib.Path, help="Validate action evaluation + image answers with --check")
    parser.add_argument("--prior-answers", type=pathlib.Path, help="Load previously returned image answers into the review")
    parser.add_argument("--split-evaluation", type=pathlib.Path,
                        help="Investigate complete member groups from returned evaluation; requires --reuse-result")
    parser.add_argument("--reform", action="store_true",
                        help="Construct actual cross-folder shadow membership; requires --reuse-result")
    parser.add_argument("--reform-view", type=pathlib.Path,
                        help="Republish verified reformation state after presentation-only changes; no scoring")
    parser.add_argument("--assess-membership", action="store_true",
                        help="With --reform, assess own/rival cores and regroup released non-core members")
    parser.add_argument("--reuse-result", type=pathlib.Path,
                        help="Republish an absolute frozen candidate after publisher-only changes; no scoring/inference")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if (not args.source.is_absolute()
                or any(path and (not args.check or not path.is_absolute())
                       for path in (args.answers, args.evaluation))
                or args.prior_answers and not args.prior_answers.is_absolute()):
            raise ValueError("absolute paths required; --answers/--evaluation only with --check")
        out = output_path(args.out)
        if args.reform_view and not args.reform:
            raise ValueError("--reform-view requires --reform")
        if args.assess_membership and not args.reform:
            raise ValueError("--assess-membership requires --reform")
        old_packet, ledger, candidate, run, vectors, cache, checkpoint, bindings = load(args.source)
        reuse_path = args.reuse_result
        if not reuse_path and out.exists():
            saved = json.loads((out / "receipt.json").read_bytes())
            if saved.get("reusedResult"):
                reuse_path = pathlib.Path(saved["reusedResult"])
        reused = None
        if reuse_path:
            if not reuse_path.is_absolute() or reuse_path.resolve() == out.resolve():
                raise ValueError("--reuse-result must be absolute and distinct from --out")
            reused = reuse(reuse_path, bindings)
            bindings = reused[3]
        if args.reform:
            from tools.art.likeness_library import reformation_report
            repaired = candidate_replay.repaired_references(candidate, ledger)
            return reformation_report.publish(
                args, out, reused, repaired, run, vectors, cache, ledger, codes, validate_evaluation,
            )
        if args.split_evaluation:
            return split_report(args, out, reused, candidate, run, vectors, cache, ledger)
        prior_answers = None
        prior_path = args.prior_answers
        if not prior_path and out.exists():
            saved = json.loads((out / "receipt.json").read_bytes())
            if saved.get("priorAnswers"):
                prior_path = pathlib.Path(saved["priorAnswers"])
        if prior_path:
            prior_answers = json.loads(prior_path.read_bytes())
            if not reused:
                raise ValueError("--prior-answers requires a verified --reuse-result")
            fragment_review.validate_answers(reused[1], prior_answers)
            bindings[str(prior_path)] = shadow.digest(prior_path)
        if args.check or args.apply and out.exists():
            packet = check(out, bindings)
            if args.answers:
                print("Candidate answers:", fragment_review.validate_answers(packet, json.loads(args.answers.read_bytes())))
            if args.evaluation:
                print("Recommendation evaluation:", validate_evaluation(
                    packet, json.loads((out / "candidate.json").read_bytes()), json.loads(args.evaluation.read_bytes()),
                ))
            print(f"Verified photo candidate replay: {out / 'index.html'}")
            return 0
        repaired = candidate_replay.repaired_references(candidate, ledger)
        removed = sum(len(a["referencePhotoIds"]) - len(b["referencePhotoIds"])
                      for a, b in zip(candidate["identities"], repaired["identities"]))
        print(f"Candidate scope: {len(run['photos'])} photos / {len(candidate['identities'])} identities; "
              f"{removed} explicit development reference repairs; zero direct labels in scoring.", flush=True)
        if not args.apply:
            print("Preview only: " + (
                "would reuse verified candidate/context and republish images/HTML; no scoring or model calls."
                if reused else "would score original/repaired references, probe shared policy, verify reverse order "
                "and publish 30-40-photo review with existing local context."
            ) + " No install or intake.")
            return 0
        initial = codes()
        started = time.perf_counter()
        evidence_hashes = {}
        if reused:
            result, packet, context, _ = reused
            scoring_seconds = context_seconds = 0.
        else:
            baseline = fragment_evidence.evaluate(candidate, run, vectors, {"pairs": []})
            print("Original references scored without pair labels.", flush=True)
            after = fragment_evidence.evaluate(repaired, run, vectors, {"pairs": []})
            print("Repaired references scored without pair labels.", flush=True)
            result = candidate_replay.compare(repaired, baseline, after, run, ledger)
            packet = candidate_replay.packet(result, repaired, run, vectors, ledger, old_packet)
            reverse_run = copy.deepcopy(run)
            reverse_run["photos"].reverse()
            reverse_run["finalMembershipAudit"]["rows"].reverse()
            reverse_candidate = copy.deepcopy(repaired)
            for key in ("rows", "identities", "appearances"):
                reverse_candidate[key].reverse()
            reverse_evidence = fragment_evidence.evaluate(reverse_candidate, reverse_run, vectors, {"pairs": []})
            if after != reverse_evidence:
                raise ValueError("candidate scoring differs under reversed inputs")
            reversed_result = candidate_replay.compare(
                repaired, {**baseline, "rows": list(reversed(baseline["rows"]))}, reverse_evidence, reverse_run, ledger,
            )
            if result != reversed_result or packet != candidate_replay.packet(
                    reversed_result, repaired, reverse_run, vectors, ledger, old_packet):
                raise ValueError("candidate policy/selection differs under reversed inputs")
            scoring_seconds = time.perf_counter() - started
            context_started = time.perf_counter()
            context = appearance_context.measure(packet, run, cache, checkpoint)
            context_seconds = time.perf_counter() - context_started
            evidence_hashes = {"baselineEvidenceSHA256": fragment_review.digest(baseline),
                               "candidateEvidenceSHA256": fragment_review.digest(after)}
        print(f"Connected candidate: {result['summary']}; review: {packet['summary']}", flush=True)
        if initial != codes() or any(shadow.digest(pathlib.Path(p)) != h for p, h in bindings.items()):
            raise ValueError("candidate replay inputs/code changed during computation")
        staging = out.with_name(out.name + ".partial")
        staging.mkdir(parents=True, exist_ok=False)
        images, outputs = review_packet.image_assets(packet, run, cache, staging, write=True)
        from PIL import Image, ImageOps
        for pid, row in context["photos"].items():
            if row["status"] != "measured":
                continue
            image_source = pathlib.Path(images[pid]["path"])
            if shadow.digest(image_source) != row["sourceSHA256"]:
                raise ValueError("context source changed during publication")
            name = f"images/{fragment_review.digest(pid)[:20]}-context.jpg"
            with Image.open(image_source) as image:
                crop = ImageOps.exif_transpose(image).convert("RGB").crop(row["cropPixels"])
                ImageOps.contain(crop, (300, 360)).save(staging / name, format="JPEG", quality=86)
            images[pid]["context"] = name
            outputs[name] = shadow.digest(staging / name)
        for name, value in (("candidate.json", result), ("packet.json", packet),
                            ("context.json", context), ("display.json", images)):
            (staging / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            outputs[name] = shadow.digest(staging / name)
        (staging / "index.html").write_text(render(packet, images, context, result, prior_answers), encoding="utf-8")
        outputs["index.html"] = shadow.digest(staging / "index.html")
        receipt = {
            "schemaVersion": 1, "kind": "connected-candidate-replay-receipt", "inputs": bindings,
            "code": initial, "outputs": outputs, "scoringPasses": 0 if reused else 3, "scoringSeconds": scoring_seconds,
            "contextSeconds": context_seconds, "directPairLabelsInScoring": 0,
            "referenceRepairOrigin": "human-development-fixtures-not-blind-reference-discovery",
            "reverseVerified": True, "libraryWrites": 0, "downloads": 0,
            "reusedResult": str(reuse_path) if reused else None, **evidence_hashes,
            "priorAnswers": str(prior_path) if prior_path else None,
        }
        (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        check(staging, bindings)
        if any(shadow.digest(pathlib.Path(p)) != h for p, h in bindings.items()) or initial != codes():
            raise ValueError("candidate replay inputs/code changed during publication")
        staging.rename(out)
        print(f"Published verified photo candidate: {out / 'index.html'}", flush=True)
        print(f"Scoring/reverse {scoring_seconds:.3f}s; local context {context_seconds:.3f}s; no installed changes.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        print(f"likeness-candidate-replay: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
