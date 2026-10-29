#!/usr/bin/env python3
"""Construit le pack packwiz d'Imperium (pack.toml, index.toml, mods/*.pw.toml).

Sources :
  - tools/curseforge.json : mods téléchargés directement depuis CurseForge (nom de fichier, lien, sha1) ;
  - mods/*.jar           : nos mods et les versions modifiées, hébergés ici ;
  - config/, options.txt, servers.dat, journeymap/ : fichiers de départ, installés UNE SEULE FOIS
    (« preserve ») : les réglages, touches et serveurs des joueurs ne sont jamais écrasés.
Construit aussi la version « Léger » (dossier leger/) pour les petits PC : mêmes fichiers, moins de mods
(tools/leger.json) et des réglages graphiques plus légers (tools/leger/).
Anciens mods : tools/mods-historique.txt garde le nom de tous les fichiers de mods que le pack a contenus un jour ;
chaque édition reçoit imperium-mods-retires.txt = ceux qui n'y sont plus. Le mod outils-serveur (au lancement) et les
scripts de mise à jour les suppriment chez le joueur (packwiz, lui, ne supprime pas les mods installés par CurseForge).
Usage : python3 tools/build_pack.py <version>
"""
import hashlib, json, os, re, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "0"
MC, NEOFORGE = "1.21.1", "21.1.264"
# fichiers installés une seule fois (puis laissés au joueur)
PRESERVE_DIRS = ("config/", "journeymap/")
PRESERVE_FILES = ("options.txt", "servers.dat")
# fichiers toujours tenus à jour (même s'ils sont dans config/) : réglages identiques chez tous les joueurs
FORCE_UPDATE = {"config/DistantHorizons.toml", "config/iris.properties", "shaderpacks/ComplementaryReimagined_r5.9.3.zip.txt"}
FORCE_UPDATE_LEGER = {"config/DistantHorizons.toml", "config/iris.properties", "shaderpacks/ComplementaryReimagined_r5.9.3.zip.txt"}   # Léger : shader et DH en faible rendu


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


LEGER = "leger"


def make_leger():
    """Recopie le pack principal dans leger/, sans les mods lourds, avec les réglages légers."""
    import shutil
    spec = json.load(open(os.path.join(ROOT, "tools", "leger.json"), encoding="utf-8"))
    dst = os.path.join(ROOT, LEGER)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.join(dst, "mods"))
    for d in ("config", "journeymap", "shaderpacks"):      # Léger : shader et DH en faible rendu, pas de Fresh Animations (EMF/ETF absents)
        shutil.copytree(os.path.join(ROOT, d), os.path.join(dst, d))
    for f in ("options.txt", "servers.dat", "imperium-version.txt"):
        shutil.copy2(os.path.join(ROOT, f), os.path.join(dst, f))
    for f in os.listdir(os.path.join(ROOT, "mods")):
        if f.endswith(".jar") and f not in spec["sans_mods"]:
            shutil.copy2(os.path.join(ROOT, "mods", f), os.path.join(dst, "mods", f))
    for f in spec.get("sans_fichiers", []):
        p = os.path.join(dst, f)
        if os.path.exists(p):
            os.remove(p)
    over = os.path.join(ROOT, "tools", "leger")
    for dirpath, _, fns in os.walk(over):
        for fn in fns:
            src = os.path.join(dirpath, fn)
            out = os.path.join(dst, os.path.relpath(src, over))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(src, out)
    with open(os.path.join(dst, "imperium-edition.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("leger\n")
    return set(spec["sans_mods"])


HIST = os.path.join(ROOT, "tools", "mods-historique.txt")
RETIRES = "imperium-mods-retires.txt"


def history():
    """Noms de tous les mods que le pack a contenus un jour, complétés avec ceux d'aujourd'hui."""
    names = set()
    if os.path.exists(HIST):
        names = {l.strip() for l in open(HIST, encoding="utf-8") if l.strip() and not l.startswith("#")}
    names |= {m["filename"] for m in json.load(open(os.path.join(ROOT, "tools", "curseforge.json"), encoding="utf-8"))}
    names |= {f for f in os.listdir(os.path.join(ROOT, "mods")) if f.endswith(".jar")}
    head = [l for l in open(HIST, encoding="utf-8") if l.startswith("#")] if os.path.exists(HIST) else []
    with open(HIST, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(head) + "\n".join(sorted(names, key=str.lower)) + "\n")
    return names


def main():
    global ALL_MODS
    ALL_MODS = history()
    build(ROOT, "Imperium", set(), FORCE_UPDATE)
    sans = make_leger()
    build(os.path.join(ROOT, LEGER), "Imperium - Leger", sans, FORCE_UPDATE_LEGER)


def build(base, packname, sans, force):
    os.chdir(base)
    meta_dir = "mods"
    # ancien .pw.toml générés : on repart de zéro
    for f in os.listdir(meta_dir):
        if f.endswith(".pw.toml"):
            os.remove(os.path.join(meta_dir, f))
    cf = [m for m in json.load(open(os.path.join(ROOT, "tools", "curseforge.json"), encoding="utf-8")) if m["filename"] not in sans]
    hosted = {f for f in os.listdir(meta_dir) if f.endswith(".jar")}
    # anciens mods : tout ce que le pack a contenu un jour et que cette édition n'a plus
    retired = sorted(ALL_MODS - {m["filename"] for m in cf} - hosted, key=str.lower)
    with open(RETIRES, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(retired) + ("\n" if retired else ""))
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
    skip_top = {".git", "tools", "installeur", "README.md", "CHANGELOG.md", "pack.toml", "index.toml", ".gitattributes", "docs", LEGER, "dist", ".gitignore"}
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if not (dirpath == "." and d in skip_top)]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), ".").replace(os.sep, "/")
            if rel.split("/")[0] in skip_top or rel.endswith(".pw.toml"):
                continue
            e = {"file": rel, "hash": sha256(rel)}
            if (rel.startswith(PRESERVE_DIRS) or rel in PRESERVE_FILES) and rel not in force:
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
    pack = (f'name = {q(packname)}\nauthor = "Kaszimir01"\nversion = {q(VERSION)}\npack-format = "packwiz:1.1.0"\n\n'
            f'[index]\nfile = "index.toml"\nhash-format = "sha256"\nhash = {q(sha256("index.toml"))}\n\n'
            f'[versions]\nminecraft = {q(MC)}\nneoforge = {q(NEOFORGE)}\n')
    with open("pack.toml", "w", encoding="utf-8", newline="\n") as f:
        f.write(pack)
    n_meta = sum(1 for e in files if e.get("metafile"))
    n_jar = sum(1 for e in files if e["file"].endswith(".jar") and e["file"].startswith("mods/"))
    print(f"{packname} {VERSION} : {n_meta} mods CurseForge, {n_jar} mods hébergés, {len(files) - n_meta - n_jar} autres fichiers, {len(retired)} anciens mods à supprimer")


if __name__ == "__main__":
    main()
