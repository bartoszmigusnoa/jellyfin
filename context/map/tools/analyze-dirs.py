import json, collections
import os, sys
# Repo root = two levels above this script (context/map/tools/ -> repo root)
ROOT = os.environ.get('JF_REPO') or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')).replace(os.sep, '/')
OUT = os.environ.get('JF_OUT') or os.path.join(ROOT, 'context', 'map', '.cache').replace(os.sep, '/')
os.makedirs(OUT, exist_ok=True)

G = json.load(open(OUT + '/graph.json', encoding='utf-8'))
ns_owner, dir_of, usings = G['ns_owner'], G['dir_of_file'], G['usings']
ns_proj, proj_of = G['ns_proj'], G['proj_of_file']

edges = collections.Counter()          # (srcdir, dstdir) -> files
for f, us in usings.items():
    s = dir_of.get(f)
    if s is None: continue
    for u in us:
        d = ns_owner.get(u)
        if d and d != s: edges[(s, d)] += 1

fanout = collections.Counter(); fanin = collections.Counter()
for (s, d), n in edges.items():
    fanout[s] += 1; fanin[d] += 1

HOT = ['Jellyfin.Server.Implementations/Item','Jellyfin.Api/Controllers',
       'MediaBrowser.Controller/Entities','Emby.Server.Implementations/Library',
       'MediaBrowser.Controller/Persistence','MediaBrowser.Controller/Library',
       'Jellyfin.Server/Migrations/Routines','MediaBrowser.Controller/MediaEncoding',
       'src/Jellyfin.Database/Jellyfin.Database.Providers.Sqlite/Migrations',
       'MediaBrowser.Providers/Plugins/Tmdb/TV']

print("=== HOT DIRS: structural fan-in / fan-out ===")
print(f"{'fan-in':>7} {'fan-out':>8}  dir")
for h in HOT:
    print(f"{fanin[h]:7d} {fanout[h]:8d}  {h}")

print("\n=== GLOBAL TOP FAN-IN (most depended-upon dirs) ===")
for d, n in fanin.most_common(12): print(f"  {n:4d}  {d}")
print("\n=== GLOBAL TOP FAN-OUT (dirs pulling most) ===")
for d, n in fanout.most_common(12): print(f"  {n:4d}  {d}")

print("\n=== KEY QUESTION: does MB.Controller/Persistence depend on JSI/Item? ===")
for a, b in [('MediaBrowser.Controller/Persistence','Jellyfin.Server.Implementations/Item'),
             ('Jellyfin.Server.Implementations/Item','MediaBrowser.Controller/Persistence'),
             ('MediaBrowser.Controller/Library','Jellyfin.Server.Implementations/Item'),
             ('Jellyfin.Server.Implementations/Item','MediaBrowser.Controller/Library'),
             ('Emby.Server.Implementations/Library','Jellyfin.Server.Implementations/Item'),
             ('Jellyfin.Server.Implementations/Item','Emby.Server.Implementations/Library'),
             ('Jellyfin.Api/Controllers','Jellyfin.Server.Implementations/Item'),
             ('MediaBrowser.Controller/Entities','Jellyfin.Server.Implementations/Item')]:
    print(f"  {edges[(a,b)]:4d} files   {a}  ->  {b}")

json.dump({'edges': {f"{a}|{b}": n for (a,b), n in edges.items()}},
          open(OUT + '/edges.json','w',encoding='utf-8'))
