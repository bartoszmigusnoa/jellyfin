import json, collections
import os, sys
# Repo root = two levels above this script (context/map/tools/ -> repo root)
ROOT = os.environ.get('JF_REPO') or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')).replace(os.sep, '/')
OUT = os.environ.get('JF_OUT') or os.path.join(ROOT, 'context', 'map', '.cache').replace(os.sep, '/')
os.makedirs(OUT, exist_ok=True)

E = json.load(open(OUT + '/edges.json', encoding='utf-8'))['edges']
adj = collections.defaultdict(set)
w = {}
for k, n in E.items():
    a, b = k.split('|'); adj[a].add(b); w[(a,b)] = n

HOT = {'Jellyfin.Server.Implementations/Item','Jellyfin.Api/Controllers',
       'MediaBrowser.Controller/Entities','Emby.Server.Implementations/Library',
       'MediaBrowser.Controller/Persistence','MediaBrowser.Controller/Library',
       'Jellyfin.Server/Migrations/Routines','MediaBrowser.Controller/MediaEncoding',
       'MediaBrowser.Providers/Plugins/Tmdb/TV','MediaBrowser.MediaEncoding/Subtitles',
       'Emby.Server.Implementations/Dto'}

print("=== 2-CYCLES (mutual dependency) touching hot dirs ===")
seen = set()
for (a,b) in list(w):
    if (b,a) in w and (b,a) not in seen:
        seen.add((a,b))
        if a in HOT or b in HOT:
            print(f"  {w[(a,b)]:3d}<->{w[(b,a)]:<3d}  {a}  <->  {b}")

print("\n=== ALL 2-CYCLES, top 15 by weight ===")
pairs = sorted({tuple(sorted((a,b))) for (a,b) in w if (b,a) in w},
               key=lambda p: -(w.get(p,0)+w.get(p[::-1],0)))
for a,b in pairs[:15]:
    print(f"  {w.get((a,b),0):3d}<->{w.get((b,a),0):<3d}  {a}  <->  {b}")
print(f"\n  total mutual pairs: {len(pairs)}")

# 3-cycles involving hot dirs
print("\n=== 3-CYCLES touching hot dirs (sample) ===")
found = set()
for a in HOT:
    for b in adj.get(a, ()):
        for c in adj.get(b, ()):
            if c != a and a in adj.get(c, ()):
                key = tuple(sorted((a,b,c)))
                if key not in found:
                    found.add(key)
                    print(f"  {a} -> {b} -> {c} -> {a}")
print(f"  total: {len(found)}")
