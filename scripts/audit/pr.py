#!/usr/bin/env python3
"""用 GitHub REST API 檢視／更新 openclaw 的 PR（token 來自 ~/.git-credentials）。"""
import json, os, sys, urllib.parse, urllib.request

REPO = 'b101108063-ops/core_radiology'


def token():
    for line in open(os.path.expanduser('~/.git-credentials')):
        line = line.strip()
        if line:
            u = urllib.parse.urlparse(line)
            if u.username:
                return u.username
    raise SystemExit('no token')


def api(path, method='GET', data=None):
    req = urllib.request.Request(
        f'https://api.github.com/repos/{REPO}{path}',
        method=method,
        data=json.dumps(data).encode() if data else None,
        headers={'Authorization': f'token {token()}',
                 'Accept': 'application/vnd.github+json',
                 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'list':
        for p in api('/pulls?state=open'):
            print(f"#{p['number']} [{p['head']['ref']}] {p['title']}")
            print('  mergeable_state:', p.get('mergeable_state'))
            print('  body:', (p.get('body') or '')[:800])
            print('---')
    elif cmd == 'get':
        p = api(f"/pulls/{sys.argv[2]}")
        print('title:', p['title'])
        print('state:', p['state'], '| mergeable:', p.get('mergeable_state'))
        print('commits:', p['commits'], '| changed_files:', p['changed_files'])
        print('body:')
        print(p.get('body') or '(empty)')
    elif cmd == 'body':
        num, path = sys.argv[2], sys.argv[3]
        body = open(path, encoding='utf-8').read()
        api(f'/pulls/{num}', 'PATCH', {'body': body})
        print(f'PR #{num} body updated ({len(body)} chars)')
