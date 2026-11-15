import re, json, sys
md = open(sys.argv[1], encoding='utf-8').read()
notes = {}
for m in re.finditer(r'dm/games/([0-9A-F]{16})/README\.md">([^<]+)</a></b>(?:<br>([^<]*))?</small>', md):
    notes[m.group(1)] = (m.group(3) or '').strip()
s2 = {}
sec = md.split('## Switch 2 games')[1].split('## Profiles')[0]
for line in sec.splitlines():
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) == 4 and c[1].startswith('`'):
        s2[c[1].strip('`')] = {'upstream': c[2], 'fork': c[3]}
prof = md.split('## Profiles')[1].split('## Verified on')[0]
games = []
for line in prof.splitlines():
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) != 4 or not c[1].startswith('`'): continue
    tid = c[1].strip('`'); name = re.sub(r'\s*\(Switch 2\)$', '', c[0])
    g = {'name': name, 'id': tid, 'update': c[2], 'status': c[3].replace('**',''),
         'note': notes.get(tid, ''), 'switch2': tid.startswith('04')}
    if tid in s2: g.update(s2[tid])
    games.append(g)
print(len(games), len(notes), file=sys.stderr)
json.dump(games, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
