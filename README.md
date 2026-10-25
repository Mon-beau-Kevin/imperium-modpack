# Modpack Imperium

Modpack du serveur Minecraft **Imperium** (NeoForge 1.21.1) — nations, guerre et Create.

Ce dépôt contient le modpack au format [packwiz](https://packwiz.infra.link/). Une fois installé, le jeu se met à jour
tout seul : seuls les fichiers qui ont changé sont téléchargés. **Tes touches, tes réglages, tes serveurs et tes mondes
ne sont jamais modifiés.**

## Installer Imperium

### Avec Prism Launcher (recommandé : mise à jour automatique)
1. Installe [Prism Launcher](https://prismlauncher.org/) et connecte ton compte Microsoft.
2. Télécharge [Imperium-Prism.zip](https://github.com/Mon-beau-Kevin/imperium-modpack/raw/main/installeur/Imperium-Prism.zip).
3. Dans Prism : **Ajouter une instance** → **Importer** → choisis le fichier.
4. Lance l'instance. La première fois, le modpack se télécharge (environ 800 Mo) ; ensuite, chaque lancement met à jour en quelques secondes.

### Avec CurseForge
1. Si tu as déjà Imperium dans CurseForge, garde-le. Sinon : **Créer un profil personnalisé** → Minecraft **1.21.1**, **NeoForge 21.1.264**.
2. Télécharge [Imperium-mise-a-jour-CurseForge.zip](https://github.com/Mon-beau-Kevin/imperium-modpack/raw/main/installeur/Imperium-mise-a-jour-CurseForge.zip).
3. Clic droit sur l'instance → **Ouvrir le dossier**, et mets-y les fichiers du zip.
4. Double-clique sur **Mettre a jour Imperium.bat**, puis lance le jeu depuis CurseForge.

**Avant chaque partie** : double-clic sur *Mettre a jour Imperium.bat*. Le jeu te prévient aussi sur l'écran titre quand une mise à jour existe.

## Serveur
`91.197.6.73:26162` (déjà ajouté dans ta liste de serveurs à la première installation).

## Nouveautés
Voir [CHANGELOG.md](CHANGELOG.md).

## Pour l'admin
- `tools/curseforge.json` : mods téléchargés depuis CurseForge ; `mods/*.jar` : nos mods et les versions modifiées.
- `config/`, `options.txt`, `servers.dat`, `journeymap/` : installés une seule fois, jamais écrasés ensuite.
- Après une modification : `python3 tools/build_pack.py <version>`, mettre la même version dans `imperium-version.txt`, puis commit et push.


## Version Léger (petits PC)
Le dossier `leger/` est un second pack, construit automatiquement par `tools/build_pack.py` : mêmes fichiers, sans les mods listés dans `tools/leger.json`, avec les réglages de `tools/leger/`. Il se met à jour tout seul comme le pack normal (fichier `imperium-edition.txt`).

Packs à importer dans CurseForge : `python3 tools/make_cf_zips.py` (dans `dist/`).
