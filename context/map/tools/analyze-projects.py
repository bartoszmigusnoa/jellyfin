import json, collections
import os, sys
# Repo root = two levels above this script (context/map/tools/ -> repo root)
ROOT = os.environ.get('JF_REPO') or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')).replace(os.sep, '/')
OUT = os.environ.get('JF_OUT') or os.path.join(ROOT, 'context', 'map', '.cache').replace(os.sep, '/')
os.makedirs(OUT, exist_ok=True)

G = json.load(open(OUT + '/graph.json', encoding='utf-8'))
pr = {k: set(v) for k, v in G['projrefs'].items()}
known = set(pr) | {t for v in pr.values() for t in v}

# cycles in project graph
def cycles(adj):
    out, color, stack = [], {}, []
    def dfs(u):
        color[u] = 1; stack.append(u)
        for v in sorted(adj.get(u, ())):
            if color.get(v, 0) == 0: dfs(v)
            elif color.get(v) == 1: out.append(stack[stack.index(v):] + [v])
        stack.pop(); color[u] = 2
    for n in sorted(adj):
        if color.get(n, 0) == 0: dfs(n)
    return out

print("=== PROJECT-LEVEL CYCLES ===")
c = cycles(pr)
print("none" if not c else c)

# transitive depth = layer
import functools
@functools.lru_cache(None)
def depth(p):
    d = pr.get(p, set())
    return 0 if not d else 1 + max(depth(x) for x in d)

print("\n=== LAYERS (0 = foundation, higher = depends on more) ===")
rows = sorted(((depth(p), len(pr.get(p,())), p) for p in pr), reverse=True)
for d, n, p in rows:
    if 'Tests' in p or 'Fuzz' in p: continue
    print(f"  L{d}  refs={n:2d}  {p}")

# fan-in at project level
fanin = collections.Counter()
for a, bs in pr.items():
    if 'Tests' in a: continue
    for b in bs: fanin[b] += 1
print("\n=== PROJECT FAN-IN (excl. test projects) ===")
for p, n in fanin.most_common(12): print(f"  {n:3d}  {p}")
