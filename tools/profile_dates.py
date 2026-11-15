"""Read `git log --format=@%cs --name-only -- dm/games` on stdin; print {title ID: date of its last change} as JSON."""
import json, re, sys
dates, cur = {}, None
for line in sys.stdin:
    line = line.strip()
    if line.startswith('@'):
        cur = line[1:]
        continue
    m = re.match(r'dm/games/([0-9A-F]{16})/', line)
    if m and m.group(1) not in dates:   # newest commit comes first
        dates[m.group(1)] = cur
json.dump(dates, sys.stdout, indent=0, sort_keys=True)
