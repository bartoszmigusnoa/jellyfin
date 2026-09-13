import os, re, json, collections
import os, sys
# Repo root = two levels above this script (context/map/tools/ -> repo root)
ROOT = os.environ.get('JF_REPO') or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')).replace(os.sep, '/')
OUT = os.environ.get('JF_OUT') or os.path.join(ROOT, 'context', 'map', '.cache').replace(os.sep, '/')
os.makedirs(OUT, exist_ok=True)

BS = chr(92)

def norm(p): return p.replace(BS, '/')

def walk(ext):
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in ('obj','bin','.git','.idea','node_modules')]
        for f in fns:
            if f.endswith(ext):
                yield norm(os.path.join(dp, f))

def rel(p): return p[len(ROOT)+1:]

projrefs = collections.defaultdict(set)
projname = {}
for cs in walk('.csproj'):
    name = os.path.basename(cs)[:-7]
    projname[rel(cs)] = name
    txt = open(cs, encoding='utf-8-sig', errors='replace').read()
    for m in re.finditer(r'ProjectReference\s+Include="([^"]+)"', txt):
        t = os.path.basename(norm(m.group(1)))[:-7]
        projrefs[name].add(t)

ns_of_file, usings_of_file, dir_of_file, proj_of_file = {}, {}, {}, {}
p2n = {os.path.dirname(p): projname[p] for p in projname}
projdirs = sorted(p2n, key=len, reverse=True)

nsre = re.compile(r'^\s*namespace\s+([A-Za-z0-9_.]+)', re.M)
usre = re.compile(r'^\s*using\s+(?:static\s+)?([A-Za-z0-9_.]+)\s*;', re.M)

for cs in walk('.cs'):
    r = rel(cs)
    if r.endswith('.Designer.cs') or 'ModelSnapshot' in r: continue
    try: txt = open(cs, encoding='utf-8-sig', errors='replace').read()
    except OSError: continue
    m = nsre.search(txt)
    if not m: continue
    ns_of_file[r] = m.group(1)
    usings_of_file[r] = set(usre.findall(txt))
    dir_of_file[r] = r.rsplit('/',1)[0] if '/' in r else '(root)'
    for pd in projdirs:
        if pd and r.startswith(pd + '/'):
            proj_of_file[r] = p2n[pd]; break

ns_dirs = collections.defaultdict(collections.Counter)
for f, ns in ns_of_file.items():
    ns_dirs[ns][dir_of_file[f]] += 1
ns_owner = {ns: c.most_common(1)[0][0] for ns, c in ns_dirs.items()}
ns_proj = {}
for f, ns in ns_of_file.items():
    ns_proj.setdefault(ns, proj_of_file.get(f, '?'))

json.dump({'projrefs': {k: sorted(v) for k,v in projrefs.items()},
           'ns_of_file': ns_of_file,
           'usings': {k: sorted(v) for k,v in usings_of_file.items()},
           'dir_of_file': dir_of_file, 'proj_of_file': proj_of_file,
           'ns_owner': ns_owner, 'ns_proj': ns_proj},
          open(OUT + '/graph.json','w',encoding='utf-8'))

print("projects:", len(projname), " files with ns:", len(ns_of_file), " namespaces:", len(ns_owner))
print("project edges:", sum(len(v) for v in projrefs.values()))
