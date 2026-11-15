"""Read `git log --format=@%cI --name-only -- dm/games` on stdin; print {title ID: time of its last change} as JSON.

Times are converted to UTC (ISO 8601, ending in Z) so they sort correctly and the page can show them in the
viewer's own time zone; a commit's own date is in its author's time zone, which can be a day ahead or behind.
"""
import json, re, sys
from datetime import datetime, timezone
dates, cur = {}, None
for line in sys.stdin:
    line = line.strip()
    if line.startswith('@'):
        cur = datetime.fromisoformat(line[1:]).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        continue
    m = re.match(r'dm/games/([0-9A-F]{16})/', line)
    if m and m.group(1) not in dates:   # newest commit comes first
        dates[m.group(1)] = cur
json.dump(dates, sys.stdout, indent=0, sort_keys=True)
