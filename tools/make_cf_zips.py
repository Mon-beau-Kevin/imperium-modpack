#!/usr/bin/env python3
"""Fabrique les deux packs à importer dans CurseForge (première installation des joueurs) :
dist/Imperium-JOUEUR-v<version>.zip et dist/Imperium-JOUEUR-LEGER-v<version>.zip.
Chaque pack contient déjà l'outil de mise à jour (Mettre a jour Imperium.bat) : ensuite tout se met à jour tout seul.
À lancer après tools/build_pack.py <version>.
"""
import json, os, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC, NEOFORGE = "1.21.1", "21.1.264"
OUTILS = ["Mettre a jour Imperium.bat", "packwiz-installer-bootstrap.jar"]
LISEZ = ("Bienvenue sur Imperium !\r\n\r\n"
         "Installation : CurseForge > Create Custom Profile > Import > choisis ce fichier .zip.\r\n\r\n"
         "Mises a jour : rien a faire. Quand une nouvelle version sort, un ecran s'affiche au lancement du jeu :\r\n"
         "le jeu se ferme, une fenetre telecharge les nouveautes, puis CurseForge se rouvre : clique sur Jouer.\r\n"
         "Tes touches, tes reglages et tes serveurs sont conserves.\r\n\r\n"
         "En cas de souci : dossier de l'instance (clic droit > Open Folder) > double-clic sur \"Mettre a jour Imperium.bat\".\r\n")


def make(base, name, label, version):
    cf = json.load(open(os.path.join(ROOT, "tools", "curseforge.json"), encoding="utf-8"))
    hosted = {f for f in os.listdir(os.path.join(base, "mods")) if f.endswith(".jar")}
    metas = set()
    for f in os.listdir(os.path.join(base, "mods")):
        if f.endswith(".pw.toml"):
            for line in open(os.path.join(base, "mods", f), encoding="utf-8"):
                if line.startswith("filename"):
                    metas.add(json.loads(line.split("=", 1)[1].strip()))
    files = [{"projectID": m["projectID"], "fileID": m["fileID"], "required": True}
             for m in cf if m["filename"] in metas and m["filename"] not in hosted]
    manifest = {"minecraft": {"version": MC, "modLoaders": [{"id": f"neoforge-{NEOFORGE}", "primary": True}]},
                "manifestType": "minecraftModpack", "manifestVersion": 1, "name": name, "version": version,
                "author": "Kaszimir01", "files": files, "overrides": "overrides"}
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    out = os.path.join(ROOT, "dist", f"Imperium-{label}-v{version}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        for dirpath, dirnames, fns in os.walk(base):
            rel_dir = os.path.relpath(dirpath, base)
            if rel_dir == ".":
                dirnames[:] = [d for d in dirnames if d in ("config", "journeymap", "mods", "shaderpacks", "resourcepacks")]
            for fn in fns:
                rel = os.path.normpath(os.path.join(rel_dir, fn)).replace(os.sep, "/")
                if fn.endswith(".pw.toml") or rel in ("pack.toml", "index.toml"):
                    continue
                if rel_dir == "." and fn not in ("options.txt", "servers.dat", "imperium-version.txt", "imperium-edition.txt", "imperium-mods-retires.txt"):
                    continue
                z.write(os.path.join(dirpath, fn), "overrides/" + rel)
        for f in OUTILS:
            z.write(os.path.join(ROOT, "installeur", "curseforge", f), "overrides/" + f)
        z.writestr("overrides/LISEZ-MOI-Imperium.txt", LISEZ)
    print(out, f"{len(files)} mods CurseForge + {len(hosted)} inclus", os.path.getsize(out) // 1024, "Ko")


if __name__ == "__main__":
    import sys
    v = open(os.path.join(ROOT, "imperium-version.txt")).read().strip() if len(sys.argv) < 2 else sys.argv[1]
    make(ROOT, "Imperium", "JOUEUR", v)
    make(os.path.join(ROOT, "leger"), "Imperium - Leger", "JOUEUR-LEGER", v)
