#!/usr/bin/env python3
"""Construit le pack packwiz d'Imperium (pack.toml, index.toml, mods/*.pw.toml).

Sources :
  - tools/curseforge.json : mods téléchargés directement depuis CurseForge (nom de fichier, lien, sha1) ;
  - mods/*.jar           : nos mods et les versions modifiées, hébergés ici ;
  - config/, options.txt, servers.dat, journeymap/ : fichiers de départ, installés UNE SEULE FOIS
    (« preserve ») : les réglages, touches et serveurs des joueurs ne sont jamais écrasés.
Usage : python3 tools/build_pack.py <version>
"""
import hashlib, json, os, re, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "0"
MC, NEOFORGE = "1.21.1", "21.1.264"
# fichiers installés une seule fois (puis laissés au joueur)
PRESERVE_DIRS = ("config/", "journeymap/")
PRESERVE_FILES = ("options.txt", "servers.dat")
# fichiers toujours tenus à jour (même s'ils sont dans config/)
FORCE_UPDATE = set()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def q(s):
    return json.dumps(s, ensure_ascii=False)


def slug(name):
    s = re.sub(r"\.jar$", "", name)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:80]


def main():
    os.chdir(ROOT)
    meta_dir = "mods"
    # ancien .pw.toml générés : on repart de zéro
    for f in os.listdir(meta_dir):
        if f.endswith(".pw.toml"):
            os.remove(os.path.join(meta_dir, f))
    cf = json.load(open("tools/curseforge.json", encoding="utf-8"))
    hosted = {f for f in os.listdir(meta_dir) if f.endswith(".jar")}
    files = []
    used = set()
    for m in sorted(cf, key=lambda m: m["filename"].lower()):
        if m["filename"] in hosted:
            continue  # la version hébergée ici gagne (version modifiée)
        s = slug(m["filename"])
        while s in used:
            s += "-x"
        used.add(s)
        url = m["url"]
        p = urllib.parse.urlsplit(url)
        url = urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path)), "", ""))
        body = (f"name = {q(m['name'])}\nfilename = {q(m['filename'])}\nside = \"both\"\n\n"
                f"[download]\nurl = {q(url)}\nhash-format = \"sha1\"\nhash = {q(m['sha1'])}\n")
        path = f"{meta_dir}/{s}.pw.toml"
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        files.append({"file": path, "hash": sha256(path), "metafile": True})
    skip_top = {".git", "tools", "installeur", "README.md", "CHANGELOG.md", "pack.toml", "index.toml", ".gitattributes", "docs"}
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if not (dirpath == "." and d in skip_top)]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), ".").replace(os.sep, "/")
            if rel.split("/")[0] in skip_top or rel.endswith(".pw.toml"):
                continue
            e = {"file": rel, "hash": sha256(rel)}
            if (rel.startswith(PRESERVE_DIRS) or rel in PRESERVE_FILES) and rel not in FORCE_UPDATE:
                e["preserve"] = True
            files.append(e)
    files.sort(key=lambda e: e["file"])
    out = ['hash-format = "sha256"', ""]
    for e in files:
        out.append("[[files]]")
        out.append(f"file = {q(e['file'])}")
        out.append(f"hash = {q(e['hash'])}")
        if e.get("metafile"):
            out.append("metafile = true")
        if e.get("preserve"):
            out.append("preserve = true")
        out.append("")
    with open("index.toml", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))
    pack = (f'name = "Imperium"\nauthor = "Kaszimir01"\nversion = {q(VERSION)}\npack-format = "packwiz:1.1.0"\n\n'
            f'[index]\nfile = "index.toml"\nhash-format = "sha256"\nhash = {q(sha256("index.toml"))}\n\n'
            f'[versions]\nminecraft = {q(MC)}\nneoforge = {q(NEOFORGE)}\n')
    with open("pack.toml", "w", encoding="utf-8", newline="\n") as f:
        f.write(pack)
    n_meta = sum(1 for e in files if e.get("metafile"))
    n_jar = sum(1 for e in files if e["file"].endswith(".jar") and e["file"].startswith("mods/"))
    print(f"Imperium {VERSION} : {n_meta} mods CurseForge, {n_jar} mods hébergés, {len(files) - n_meta - n_jar} autres fichiers")


if __name__ == "__main__":
    main()
