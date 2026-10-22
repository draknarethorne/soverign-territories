"""Legacy no-policy reconciliation compatibility adapter."""
import numpy as np
from .scoring import nz
from .reconciliation import _rank, _confident, _average_linkage, _cluster_id

def plan_legacy(prepared, cores, held, candidates, *, assign, margin, cluster, minimum_cluster, cast_merge, names_taken, name_factory):
    """Legacy no-policy API compatibility; ordinary intake and clean rebuilding never call this adapter."""
    assignments = []
    unresolved = []
    for candidate in prepared:
        ranked = _rank(candidate['vector'], cores, candidate['side'])
        match = _confident(ranked, assign, margin)
        if match:
            score, folder = match
            assignments.append({'photoId': candidate['photoId'], 'sourceFolder': candidate['sourceFolder'], 'sourceBucket': candidate['sourceBucket'], 'destination': folder, 'destinationType': 'existing', 'score': round(score, 4), 'reason': 'confident match against frozen identity core'})
        else:
            unresolved.append(candidate)
    provisional_cores = {}
    provisional_rows = []
    pending = []
    groups_by_side = {}
    for candidate in unresolved:
        groups_by_side.setdefault(candidate['side'], []).append(candidate)
    taken = {name.casefold() for name in names_taken}
    for side in sorted(groups_by_side):
        for group in _average_linkage(groups_by_side[side], cluster):
            if len(group) < minimum_cluster:
                pending.extend(group)
                continue
            cluster_vector = nz(np.mean([candidate['vector'] for candidate in group], axis=0))
            ranked = _rank(cluster_vector, cores, side)
            cast_match = _confident(ranked, cast_merge, margin)
            if cast_match and (not (cast_match[1].startswith('Angels/') or cast_match[1].startswith('Sisters/'))):
                cast_match = None
            ordinary_match = _confident(ranked, assign, margin)
            if cast_match:
                score, destination = cast_match
                destination_type = 'existing'
                reason = 'candidate cluster confidently matches a cast identity core'
            elif ordinary_match:
                score, destination = ordinary_match
                if destination.startswith('Angels/') or destination.startswith('Sisters/'):
                    pending.extend(group)
                    continue
                destination_type = 'existing'
                reason = 'candidate cluster confidently matches an existing identity core'
            elif ranked and ranked[0][0] >= assign:
                pending.extend(group)
                continue
            else:
                seed = _cluster_id(group)
                name = name_factory(seed, taken)
                if not name or name.casefold() in taken:
                    raise ValueError(f'name factory returned a missing or duplicate name for cluster {seed}')
                taken.add(name.casefold())
                root = 'Prospects' if len(group) >= 5 else 'Potentials'
                destination = f'{root}/{name}'
                destination_type = 'provisional'
                score = None
                reason = f'new provisional cluster of {len(group)} candidates'
                provisional_cores[destination] = {'vector': cluster_vector, 'side': side}
            cluster_id = _cluster_id(group)
            provisional_rows.append({'clusterId': cluster_id, 'destination': destination, 'destinationType': destination_type, 'photoIds': sorted((candidate['photoId'] for candidate in group)), 'score': round(score, 4) if score is not None else None, 'reason': reason})
            for candidate in group:
                assignments.append({'photoId': candidate['photoId'], 'sourceFolder': candidate['sourceFolder'], 'sourceBucket': candidate['sourceBucket'], 'destination': destination, 'destinationType': destination_type, 'clusterId': cluster_id, 'score': round(score, 4) if score is not None else None, 'reason': reason})
    available_cores = dict(cores)
    available_cores.update(provisional_cores)
    while pending:
        newly_assigned = []
        remaining = []
        for candidate in pending:
            ranked = _rank(candidate['vector'], available_cores, candidate['side'])
            match = _confident(ranked, assign, margin)
            if match:
                score, folder = match
                is_provisional = folder in provisional_cores
                newly_assigned.append({'photoId': candidate['photoId'], 'sourceFolder': candidate['sourceFolder'], 'sourceBucket': candidate['sourceBucket'], 'destination': folder, 'destinationType': 'provisional' if is_provisional else 'existing', 'score': round(score, 4), 'reason': 'confident match against frozen provisional cluster' if is_provisional else 'confident match against frozen identity core'})
            else:
                remaining.append(candidate)
        if not newly_assigned:
            pending = remaining
            break
        assignments.extend(newly_assigned)
        pending = remaining
    assignment_ids = [row['photoId'] for row in assignments]
    if len(assignment_ids) != len(set(assignment_ids)):
        raise AssertionError('a candidate was assigned more than once')
    for candidate in pending:
        ranked = _rank(candidate['vector'], available_cores, candidate['side'])
        match = _confident(ranked, assign, margin)
        reason = 'ambiguous destination; remains staged' if ranked and ranked[0][0] >= assign else 'no destination or qualifying cluster; remains staged'
        if match:
            reason = 'unstable destination; remains staged'
        held.append({'photoId': candidate['photoId'], 'sourceFolder': candidate['sourceFolder'], 'sourceBucket': candidate['sourceBucket'], 'reason': reason, 'bestMatch': ranked[0][1] if ranked else None, 'bestScore': round(ranked[0][0], 4) if ranked else None})
    assignments.sort(key=lambda row: row['photoId'])
    held.sort(key=lambda row: (row.get('photoId') or '', row.get('sourceFolder') or ''))
    provisional_rows.sort(key=lambda row: row['clusterId'])
    return {'assignments': assignments, 'held': held, 'clusters': provisional_rows, 'candidateCount': len(candidates), 'assignedCount': len(assignments), 'heldCount': len(held), 'coreFolders': len(cores)}
