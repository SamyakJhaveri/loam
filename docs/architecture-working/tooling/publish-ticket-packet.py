"""Publish the explicitly approved planning packet. Never start runtime work."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ARC = Path(__file__).resolve().parents[1]
OUT = ARC / 'publication'
REPO = 'SamyakJhaveri/loam'
BACKLOG = json.loads((ARC / 'ticket-backlog.json').read_text())
DIGEST = hashlib.sha256((ARC / 'ticket-backlog.json').read_bytes()).hexdigest()
LEDGER = OUT / 'ledger.json'
STATE = json.loads(LEDGER.read_text()) if LEDGER.exists() else {
    'backlog_sha256': DIGEST, 'approval': 'User selected Option A: publish parent and all prepared tickets',
    'runtime_authorized': False, 'issues': {}, 'relationships': {}, 'status': 'in-progress'}
assert STATE['backlog_sha256'] == DIGEST and STATE['runtime_authorized'] is False


def save():
    temp = LEDGER.with_suffix('.tmp')
    temp.write_text(json.dumps(STATE, indent=2) + '\n')
    temp.replace(LEDGER)


def gh(*args):
    p = subprocess.run(['gh', *args], text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip())
    return p.stdout.strip()


def api(path, *args):
    return json.loads(gh('api', f'repos/{REPO}/{path}', *args))


def marker(key):
    return f'<!-- loam-native-campaign:{DIGEST}:{key} -->'


def body_for(ticket):
    body = ticket['body'].replace('planned draft; publication approval pending; runtime implementation deferred',
                                  'planned; runtime implementation deferred; not ready-for-agent')
    assert 'publication approval pending' not in body
    blockers = '\n'.join(f"- {STATE['issues'][d]['url']} ({d})" for d in ticket['depends']) or 'None. Implementation authorization and source-packet readiness still required.'
    return (f"{marker(ticket['id'])}\n\nStage: {ticket['stage']}\n\nImplementation lead: {ticket['implementation_lead']}\n\n"
            f"Campaign: {STATE['issues']['parent']['url']}\n\n## Blocked by\n\n{blockers}\n\n{body}\n\n"
            f"Approved draft SHA-256: `{ticket['sha256']}`. Full source access must be verified before execution.\n")


def parent_body(complete=False):
    body = (ARC / 'tickets/campaign-parent.md').read_text().split('\n', 1)[1].lstrip()
    body = body.replace('Draft parent for publication approval.', 'Published with explicit Option A approval. Status: planned; runtime implementation deferred; not ready-for-agent.')
    by_file = {t['file']:t for t in BACKLOG['tickets']}
    def link(match):
        label, target = match.groups()
        if '://' in target:
            return match.group(0)
        if target in by_file:
            t = by_file[target]
            return f"[{label}]({STATE['issues'][t['id']]['url']})" if complete else f"{label} (publication in progress)"
        return f"{label}: `docs/architecture-working/{target.removeprefix('../')}`"
    body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, body)
    body = body.split('## Publication handling')[0]
    body += '## Source availability\n\nThe exact approved source packet is preserved locally at `docs/architecture-working/publication/approved-source-packet/`. It is not yet committed to main. Supply and verify it before a fresh worker starts. Publication does not remove this readiness gate.\n'
    return marker('parent') + '\n\n' + body


def create(key, title, body):
    path = OUT / f'{key}.md'
    if key in STATE['issues']:
        row = STATE['issues'][key]
        data = api(f"issues/{row['number']}")
        saved_body = path.read_text()
        assert hashlib.sha256(saved_body.encode()).hexdigest() == row['body_sha256'], key
        assert data['body'] == saved_body and data['title'] == row['title'], key
        assert not data['labels'] and not data['assignees'], key
        return
    # A prior process may have succeeded remotely before its receipt was saved.
    rows = json.loads(gh('issue', 'list', '--repo', REPO, '--state', 'all', '--limit', '500', '--json', 'number,title,body,url'))
    matches = [r for r in rows if marker(key) in (r['body'] or '')]
    assert len(matches) <= 1, f'Duplicate marker: {key}'
    path.write_text(body)
    if matches:
        number = matches[0]['number']
    else:
        url = gh('issue', 'create', '--repo', REPO, '--title', title, '--body-file', str(path))
        number = int(url.rsplit('/', 1)[1])
    if matches:
        assert matches[0]['body'] == body and matches[0]['title'] == title, key
    # Save the returned identity before the next network operation.
    STATE['issues'][key] = {'number':number, 'url':f'https://github.com/{REPO}/issues/{number}',
                            'body_sha256':hashlib.sha256(body.encode()).hexdigest(), 'title':title}
    save()
    data = api(f'issues/{number}')
    assert data['body'] == body and data['title'] == title, key
    STATE['issues'][key]['id'] = data['id']
    save()
    print(f"Published {key}: {STATE['issues'][key]['url']}", flush=True)


def relation_api(path, *args):
    try:
        return api(path, *args)
    except RuntimeError as exc:
        if not any(f'HTTP {code}' in str(exc) for code in (404, 410, 422)):
            raise
        STATE.setdefault('relationship_fallbacks', {})[path] = str(exc)
        save()
        print(f'Native relationship unavailable; linked-body fallback recorded: {path}', flush=True)
        return None


def verify():
    parent = STATE['issues']['parent']['number']
    children = relation_api(f'issues/{parent}/sub_issues?per_page=100')
    expected_children = {STATE['issues'][t['id']]['id'] for t in BACKLOG['tickets']}
    if children is not None:
        actual = {x['id'] for x in children}
        assert actual.issubset(expected_children)
        assert actual == expected_children or f'issues/{parent}/sub_issues' in STATE.get('relationship_fallbacks', {})
    for key, row in STATE['issues'].items():
        data = api(f"issues/{row['number']}")
        assert data['body'] == (OUT / f'{key}.md').read_text(), f'body: {key}'
        assert hashlib.sha256(data['body'].encode()).hexdigest() == row['body_sha256']
        assert data['title'] == row['title'] and data['state'] == 'open'
        assert not data['assignees'] and not data['labels'], f'assignment/label: {key}'
        if key != 'parent':
            t = next(t for t in BACKLOG['tickets'] if t['id'] == key)
            endpoint = f"issues/{row['number']}/dependencies/blocked_by"
            deps = relation_api(endpoint + '?per_page=100')
            if deps is not None:
                actual = {x['id'] for x in deps}
                expected = {STATE['issues'][d]['id'] for d in t['depends']}
                assert actual.issubset(expected), key
                assert actual == expected or endpoint in STATE.get('relationship_fallbacks', {}), key
            for d in t['depends']:
                assert STATE['issues'][d]['url'] in data['body'], key
    assert all(row['url'] in (OUT / 'parent.md').read_text() for key,row in STATE['issues'].items() if key != 'parent')
    STATE['status'] = 'published-verified-runtime-deferred'
    save()
    print(f"Publication: PASSED; {len(BACKLOG['tickets'])} children; {sum(len(t['depends']) for t in BACKLOG['tickets'])} dependencies; exact bodies; unassigned; no labels; {len(STATE.get('relationship_fallbacks', {}))} recorded endpoint fallbacks", flush=True)


def finish_parent_update():
    pending = STATE.get('pending_parent_update')
    if not pending:
        return
    row = STATE['issues']['parent']
    data = api(f"issues/{row['number']}")
    remote_hash = hashlib.sha256(data['body'].encode()).hexdigest()
    assert remote_hash in (pending['old_sha256'], pending['new_sha256'])
    assert data['title'] == row['title'] and not data['labels'] and not data['assignees']
    body = pending['body']
    assert hashlib.sha256(body.encode()).hexdigest() == pending['new_sha256']
    path = OUT / 'parent.md'
    path.write_text(body)
    if remote_hash != pending['new_sha256']:
        gh('issue', 'edit', str(row['number']), '--repo', REPO, '--body-file', str(path))
    assert api(f"issues/{row['number']}")['body'] == body
    row['body_sha256'] = pending['new_sha256']
    del STATE['pending_parent_update']
    save()


def main():
    mode = sys.argv[1]
    frozen = OUT / 'approved-source-packet'
    for name, digest in json.loads((frozen / 'manifest.json').read_text()).items():
        assert hashlib.sha256((frozen / name).read_bytes()).hexdigest() == digest, name
        if name.endswith(('ticket-backlog.json', 'tickets/campaign-parent.md')):
            assert hashlib.sha256((ARC.parents[1] / name).read_bytes()).hexdigest() == digest, name
    if mode == 'preview':
        print('Repository:', REPO)
        print('Parent: Generated native software factory for every Loam seed')
        print('Children:', len(BACKLOG['tickets']), 'Dependencies:', sum(len(t['depends']) for t in BACKLOG['tickets']))
        print('No labels. No assignees. No runtime commands. Existing issues unchanged. Frozen sources verified.')
        return
    if mode == 'verify':
        verify()
        return
    assert mode == 'publish'
    finish_parent_update()
    create('parent', 'Generated native software factory for every Loam seed', parent_body())
    for t in BACKLOG['tickets']:
        create(t['id'], f"{t['id']}: {t['title']}", body_for(t))
    # Recover IDs after an interrupted creation/readback boundary.
    for row in STATE['issues'].values():
        if 'id' not in row:
            row['id'] = api(f"issues/{row['number']}")['id']
            save()
    body = parent_body(True)
    STATE['pending_parent_update'] = {'body': body,
        'old_sha256': STATE['issues']['parent']['body_sha256'],
        'new_sha256': hashlib.sha256(body.encode()).hexdigest()}
    save()
    finish_parent_update()
    parent = STATE['issues']['parent']['number']
    present = {x['id'] for x in (relation_api(f'issues/{parent}/sub_issues?per_page=100') or [])}
    for t in BACKLOG['tickets']:
        row = STATE['issues'][t['id']]
        if row['id'] not in present:
            relation_api(f'issues/{parent}/sub_issues', '--method', 'POST', '-F', f"sub_issue_id={row['id']}")
        deps = {x['id'] for x in (relation_api(f"issues/{row['number']}/dependencies/blocked_by?per_page=100") or [])}
        for d in t['depends']:
            ident = STATE['issues'][d]['id']
            if ident not in deps:
                result = relation_api(f"issues/{row['number']}/dependencies/blocked_by", '--method', 'POST', '-F', f'issue_id={ident}')
                method = 'native' if result is not None else 'linked-body-fallback'
            else:
                method = 'native'
            STATE['relationships'][f"{t['id']}<-{d}"] = method
            save()
        print(f"Linked {t['id']}", flush=True)
    verify()


if __name__ == '__main__':
    main()
