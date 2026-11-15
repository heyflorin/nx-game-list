import re, json, sys
md = open(sys.argv[1], encoding='utf-8').read()
games = json.load(open(sys.argv[2]))
have = {g['id'] for g in games}
for m in re.finditer(r'dm/games/([0-9A-F]{16})/README\.md">([^<]+)</a></b>(?:<br>([^<]*))?</small>', md):
    if m.group(1) not in have:
        games.append({'name': m.group(2), 'id': m.group(1), 'update': '—',
                      'status': 'Screenshot in the gallery; no row in the profile table',
                      'note': (m.group(3) or '').strip(), 'switch2': m.group(1).startswith('04'), 'galleryOnly': True})
for g in games:
    s, up = g['status'], g.get('upstream', '')
    if s.startswith('Verified') and 'iPhone' in s: tier = 'Verified'
    elif s.startswith('Verified'): tier = 'Plays on Mac'   # verified, but on a Mac only
    elif s.startswith('Playable'): tier = 'Playable'
    elif g['switch2'] and up.startswith('Reaches'): tier = 'Partial'
    elif g['switch2'] and up.startswith('Plays'): tier = 'Plays on Mac'
    elif g.get('galleryOnly'): tier = 'Shown running'
    else: tier = 'Profile only'
    g['tier'] = tier
    if g['switch2']:
        g['platforms'] = ['Mac', 'iPhone', 'iPad'] if g['id'] == '040074A01BF12000' else (['Mac', 'iPhone'] if tier == 'Verified' else ['Mac'])
    else:
        g['platforms'] = ['Mac', 'iPhone', 'iPad']
    fps = re.search(r'(up to \d+|\d+) fps', g['note'] + ' ' + up)
    g['fps'] = fps.group(0) if fps else ''
    extra = []
    if 'by touch' in s and 'touch' not in g['note']: extra.append('playable by touch')
    if 'with a controller' in s and 'controller' not in g['note']: extra.append('needs a controller')
    if up and 'No IPA built' in up: extra.append(up.split('. ', 1)[1] if '. ' in up else 'No IPA built')
    if g.get('fork') and g['fork'] != 'Not tried': extra.append({'040074A01BF12000': 'Tested by the fork: no problems on Mac and iPhone, almost none on iPad', '04007EF01F8AE000': 'Verified by the fork on an iPhone 18 Pro Max: 60 fps, no dropped frames'}.get(g['id'], g['fork'][:120]))
    n = re.sub(r'^Switch 2, Mac (only|& iPhone \(\d+ fps\)),? ?', '', g['note'])
    n = re.sub(r'(up to \d+|\d+) fps( target)?', lambda m: '', n).strip(' ,·')
    n = re.sub(r'^with ', 'with update ', n)
    g['notes'] = ([n] if n else []) + extra
    g['owned'] = ''

import curation as C
byn = {('nx', x['number']): x for x in json.load(open('new1/matched.json'))}
byn.update({('app', x['number']): x for x in json.load(open('new2/matched.json'))})
def key(n): return ('app', int(n[1:])) if isinstance(n, str) else ('nx', n)
def short(t): return re.sub(r'\s+', ' ', t).strip()
def ent(k): x = byn[k]; return {'r': k[0], 'n': k[1], 'open': x['state'] == 'open', 't': short(x['title'])}
for g in games:
    keys = {k for k, x in byn.items() if any(h == g['id'] or h[:13]+'000' == g['id'] for h in x['games'])}
    keys |= {key(n) for n in C.EXTRA_LINKS.get(g['id'], [])} | {key(r[0]) for r in C.REPORTS.get(g['id'], [])}; keys -= {key(n) for n in C.EXCLUDE.get(g['id'], [])}
    g['issues'] = [ent(k) for k in sorted(keys, key=lambda k: (k[0] != 'nx', k[1]))]
    g['reports'] = [{'r': key(n)[0], 'n': key(n)[1], 'k': k, 't': t} for n, k, t in C.REPORTS.get(g['id'], [])]
    if g['id'] in C.REPORTED_WORKING and g['tier'] == 'Profile only': g['tier'] = 'Reported working'
    if g['id'] in C.TIER_OVERRIDE: g['tier'] = C.TIER_OVERRIDE[g['id']]
_profiled = set(json.load(open('readmes/index.json')))
for gid, name, s2, tier, plats, n, note in C.EXTRA_GAMES:
    if gid in _profiled: continue   # a profile now exists: its own row replaces this issue-only one
    links = {key(n)} | {key(m) for m in C.EXTRA_LINKS.get(gid, [])}
    games.append({'name': name, 'id': gid, 'update': '—', 'status': 'Not in GAMES.md; reported in an issue',
      'note': '', 'switch2': s2, 'tier': tier, 'platforms': plats, 'fps': '', 'notes': [], 'community': True,
      'owned': '',
      'issues': [ent(k) for k in sorted(links)],
      'reports': [{'r': key(n)[0], 'n': key(n)[1], 'k': 'good' if tier == 'Reported working' else 'bad', 't': note}]})

# ---- nxnative engine index (dm/games/README.md) and per-game notes ----
IDX = json.load(open('readmes/index.json')); CL = json.load(open('readmes/classify.json'))
try: PDATES = json.load(open('readmes/profile-dates.json'))
except OSError: PDATES = {}
def enote(i):
    try: t = open(f'readmes/all/{i}.md').read()
    except OSError: return ''
    intro = re.sub(r'\s+', ' ', re.split(r'\n## ', t)[0])
    st = re.search(r'## Status\s*\n(.*?)(\n## |\Z)', t, re.S)
    if st: intro += ' ' + re.sub(r'\s+', ' ', st.group(1))
    intro = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', intro).replace('**', '').replace('`', '')
    for s in re.split(r'(?<=[.;])\s', intro):
        if re.search(r'\b(plays|playable|played|brought up)\b|\bruns (on|at)\b|\bon the Mac\b', s, re.I) and not s.startswith('#') and s[:1].isupper() and not re.search(r'same .?sdk|builds? (used|Tears)|first game of this repository', s):
            s = re.sub(r'^Status:\s*', '', s.strip()); s = re.sub(r';$', '.', s)
            return s if len(s) <= 220 else s[:217].rsplit(' ', 1)[0] + '…'
    return ''
def upgrade(g):
    c = CL.get(g['id'], {})
    if c.get('phone') and not g['switch2']: return 'Playable'
    if c.get('mac'): return 'Plays on Mac'
    return g['tier']
have = {g['id'] for g in games}
for g in games:
    i = g['id']
    if i not in IDX: continue
    b = IDX[i]['build']
    if g['update'] == '—': g['update'] = b
    elif not g['update'].startswith('None') and b.split(' ')[0].rstrip(',') not in g['update']:
        g['notes'].append("NX2Apple's list says " + g['update']); g['update'] = b
    if g['tier'] in ('Profile only', 'Shown running'): g['tier'] = upgrade(g)
    g['engine'] = enote(i)
    g['profileDate'] = PDATES.get(i, '')
for i, v in IDX.items():
    if i in have: continue
    ng = {'name': v['name'], 'id': i, 'update': v['build'], 'status': 'nxnative profile, not yet in NX2Apple GAMES.md',
          'note': '', 'switch2': i.startswith('04'), 'tier': 'Profile only', 'fps': '', 'notes': [], 'engineOnly': True,
          'owned': '', 'reports': [], 'engine': enote(i), 'profileDate': PDATES.get(i, '')}
    ng['tier'] = upgrade(ng)
    ng['platforms'] = ['Mac'] if ng['switch2'] else ['Mac', 'iPhone', 'iPad']
    keys = {k for k, x in byn.items() if i.lower() in x['title'].lower()}
    ng['issues'] = [ent(k) for k in sorted(keys, key=lambda k: (k[0] != 'nx', k[1]))]
    games.append(ng)
# A problem whose issue has since closed becomes fixed (completed) or closed (not planned).
for g in games:
    for r in g['reports']:
        x = byn.get((r['r'], r['n']))
        if x and r['k'] == 'bad' and x['state'] == 'closed':
            r['k'] = 'fixed' if x.get('state_reason') == 'completed' else 'closed'

missing = []
games.sort(key=lambda g: g['name'].lower())
for g in games: g.pop('owned', None); g.pop('mine', None)
json.dump({'games': games}, open(sys.argv[3], 'w'), ensure_ascii=False)
from collections import Counter
print(len(games), 'games;', Counter(g['tier'] for g in games), sum(len(g['issues']) for g in games), 'issue links')

import glob, os
try: META = json.load(open('meta.json'))
except OSError: META = {}
META.update({
    'profiles': len(json.load(open('readmes/index.json'))),
    'issues_nx': sum(1 for _ in open('new1/all.jsonl')),
    'issues_app': sum(1 for _ in open('new2/all.jsonl')),
})
html = open(sys.argv[4]).read().replace('__DATA__', json.dumps({'games': games, 'aliases': C.ALIASES, 'notes': C.MISSING_NOTES, 'meta': META}, ensure_ascii=False).replace('</', '<\\/'))
open(sys.argv[5], 'w').write(html)
open(sys.argv[6], 'w').write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + html.replace('<div class="wrap">', '</head>\n<body>\n<div class="wrap">', 1) + '\n</body>\n</html>\n')
