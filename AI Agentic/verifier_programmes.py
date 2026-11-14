#!/usr/bin/env python3
"""Vérifie les blocs ```python des fichiers Markdown du parcours « AI Agentic ».

Usage :
    python verifier_programmes.py <fichier.md | dossier> [...] [--status] [--no-run]

Un bloc dont la première ligne non vide commence par « # [extrait] » n'est pas
exécuté : on vérifie seulement qu'il est syntaxiquement valide.

Un bloc exécutable PASSE si :
  - il compile en syntaxe Python 3.10 (ast, feature_version) sans f-string 3.12+ ;
  - il n'importe que la bibliothèque standard ;
  - il contient au moins un assert, définit main() et l'appelle ;
  - il sort avec le code 0 en moins de 30 s, SANS -X utf8 (console cp1252 simulée) ;
  - sa dernière ligne non vide est exactement la sentinelle ci-dessous ;
  - deux exécutions donnent la même sortie (déterminisme) ;
  - la section « Sortie attendue » qui le suit, si elle existe, se retrouve
    ligne à ligne, dans l'ordre, dans la sortie réelle.

ERREUR = fait échouer (code retour 1). ALERTE = à corriger ou à justifier.
"""
from __future__ import annotations

import argparse
import ast
import io
import os
import re
import subprocess
import sys
import tempfile
import tokenize
import urllib.parse
from pathlib import Path

SENTINELLE = "OK — toutes les vérifications sont passées."
PY = sys.executable
RUN_ROOT = Path(tempfile.gettempdir()) / "verifier_programmes_md"  # hors du dossier de cours
TIMEOUT = 30
EXTRAIT = "# [extrait]"

FENCE_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
LINK_RE = re.compile(r"\[([^\]]*)\]\((<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\)")
TYPING_GENERICS = {"List", "Dict", "Set", "Tuple", "Optional", "Union", "FrozenSet", "Type"}


# --------------------------------------------------------------------------- lecture
def lire(path: Path) -> tuple[list[str], list[str]]:
    """Renvoie (lignes, alertes de fichier) avec des fins de ligne universelles."""
    alertes = []
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        alertes.append("BOM UTF-8 en tête de fichier")
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    if crlf and lf:
        alertes.append(f"fins de ligne mélangées (CRLF={crlf}, LF={lf})")
    texte = data.decode("utf-8-sig", errors="replace")
    if "�" in texte:
        alertes.append("caractères non UTF-8 (remplacés par �)")
    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    return texte.split("\n"), alertes


def blocs_de_code(lignes: list[str]):
    """Repère les blocs clôturés. Renvoie (blocs, ligne d'un bloc non fermé ou None)."""
    blocs = []
    dans = False
    car = long = indent = debut = None
    info = ""
    tampon: list[str] = []
    for i, ligne in enumerate(lignes, start=1):
        brut = ligne.strip()
        m = FENCE_RE.match(brut)
        if not dans:
            if m:
                fence, reste = m.group(1), m.group(2).strip()
                if fence[0] == "`" and "`" in reste:
                    continue
                dans, car, long = True, fence[0], len(fence)
                indent = len(ligne) - len(ligne.lstrip(" "))
                info, debut, tampon = reste, i, []
        else:
            if m and m.group(1)[0] == car and len(m.group(1)) >= long and m.group(2).strip() == "":
                lang = info.split()[0].lower() if info else ""
                code = "\n".join(_retirer_indent(l, indent) for l in tampon) + "\n"
                blocs.append({"info": info, "lang": lang, "debut": debut, "fin": i, "code": code})
                dans = False
            else:
                tampon.append(ligne)
    return blocs, (debut if dans else None)


def _retirer_indent(ligne: str, n: int) -> str:
    k = 0
    while k < n and k < len(ligne) and ligne[k] == " ":
        k += 1
    return ligne[k:]


def est_extrait(code: str) -> bool:
    for l in code.splitlines():
        if l.strip():
            return l.strip().startswith(EXTRAIT)
    return True


# --------------------------------------------------------------------------- analyse statique
def _guillemet(s: str) -> str:
    s2 = s.lstrip("rRbBfFuUtT")
    return s2[:3] if s2[:3] in ('"""', "'''") else s2[:1]


def fstrings_312(code: str) -> list[str]:
    FSTART = getattr(tokenize, "FSTRING_START", None)
    FEND = getattr(tokenize, "FSTRING_END", None)
    if FSTART is None:
        return []
    pb, pile = [], []
    try:
        jetons = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, SyntaxError) as e:
        return [f"tokenize impossible : {e}"]
    for t in jetons:
        if t.type == FSTART:
            q = _guillemet(t.string)
            if pile and q == pile[-1]:
                pb.append(f"l.{t.start[0]} : f-string imbriquée avec les mêmes guillemets (Python 3.12+)")
            pile.append(q)
        elif t.type == FEND:
            if pile:
                pile.pop()
        elif pile and t.type == tokenize.STRING:
            if _guillemet(t.string) == pile[-1]:
                pb.append(f"l.{t.start[0]} : mêmes guillemets dans une f-string (Python 3.12+)")
            if "\\" in t.string:
                pb.append(f"l.{t.start[0]} : antislash dans l'expression d'une f-string (Python 3.12+)")
        elif pile and t.type == tokenize.COMMENT:
            pb.append(f"l.{t.start[0]} : commentaire dans une f-string (Python 3.12+)")
    return pb


def analyse_statique(code: str) -> tuple[list[str], list[str]]:
    """Renvoie (erreurs, alertes) pour un bloc exécutable."""
    erreurs, alertes = [], []
    try:
        arbre = ast.parse(code, feature_version=(3, 10))
    except SyntaxError as e:
        return [f"syntaxe incompatible Python 3.10 : {e.msg} (l.{e.lineno})"], []
    erreurs += fstrings_312(code)
    stdlib = set(sys.stdlib_module_names) | {"__future__"}
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] not in stdlib:
                    erreurs.append(f"import hors bibliothèque standard : {a.name}")
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            if n.module.split(".")[0] not in stdlib:
                erreurs.append(f"import hors bibliothèque standard : {n.module}")
    if not any(isinstance(n, ast.Assert) for n in ast.walk(arbre)):
        erreurs.append("aucun assert : le bloc ne vérifie rien")
    defini = any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in arbre.body)
    appele = False
    for n in arbre.body:
        cibles = [n] + (list(ast.walk(n)) if isinstance(n, ast.If) else [])
        for c in cibles:
            if isinstance(c, ast.Expr) and isinstance(c.value, ast.Call) and isinstance(c.value.func, ast.Name) and c.value.func.id == "main":
                appele = True
    if not (defini and appele):
        erreurs.append("main() doit être défini au niveau module et appelé (if __name__ == '__main__': main())")
    noms_typing = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.ImportFrom) and n.module == "typing":
            noms_typing |= {a.name for a in n.names}
    if noms_typing & TYPING_GENERICS:
        alertes.append("typing." + "/".join(sorted(noms_typing & TYPING_GENERICS)) + " : préférer list[int], dict[str, float], X | None")
    for n in ast.walk(arbre):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            nom = n.func.attr
            if nom in {"perf_counter", "time", "now", "monotonic"} and isinstance(n.func.value, ast.Name) and n.func.value.id in {"time", "datetime"}:
                alertes.append(f"l.{n.lineno} : {n.func.value.id}.{nom}() rend la sortie non déterministe (utiliser une horloge simulée)")
            if nom == "sleep" and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, (int, float)) and n.args[0].value > 0.05:
                alertes.append(f"l.{n.lineno} : time.sleep({n.args[0].value}) réel, préférer une horloge simulée")
    return erreurs, alertes


# --------------------------------------------------------------------------- exécution
def _tuer_arbre(p: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
    else:
        p.kill()


def _decoder(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


def executer(code: str) -> tuple[int | None, str, str]:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix="bloc_", dir=RUN_ROOT))
    f = d / "bloc.py"
    f.write_text(code, encoding="utf-8")
    drapeaux = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    p = subprocess.Popen([PY, "-I", str(f)], cwd=d, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=drapeaux)
    try:
        out, err = p.communicate(timeout=TIMEOUT)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        _tuer_arbre(p)
        try:
            out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            out, err = b"", b""
        rc = None
    return rc, _decoder(out).replace("\r\n", "\n"), _decoder(err).replace("\r\n", "\n")


def sous_sequence(attendu: list[str], reel: list[str]) -> str | None:
    """None si chaque ligne attendue apparaît dans l'ordre ; sinon la première ligne introuvable."""
    j = 0
    for a in attendu:
        while j < len(reel) and reel[j] != a:
            j += 1
        if j == len(reel):
            return a
        j += 1
    return None


def _norm(l: str) -> str:
    return l.replace(" ", " ").replace(" ", " ").rstrip()


# --------------------------------------------------------------------------- lint de la prose
def lint_prose(lignes: list[str], blocs, chemin: Path) -> tuple[list[str], list[str]]:
    erreurs, alertes = [], []
    dans_code = set()
    for b in blocs:
        dans_code.update(range(b["debut"], b["fin"] + 1))
        if b["lang"].startswith("markdown"):
            erreurs.append(f"l.{b['debut']} : bloc ```{b['info']} — le contenu s'affiche comme du code brut")
    affichage = False
    paragraphe: list[tuple[int, str]] = []

    def fermer_paragraphe():
        txt = " ".join(t for _, t in paragraphe)
        if txt.count("**") % 2 == 1:
            alertes.append(f"l.{paragraphe[0][0]} : nombre impair de ** dans le paragraphe (gras non fermé)")
        paragraphe.clear()

    debut_maths = 0
    for i, brute in enumerate(lignes, start=1):
        if i in dans_code:
            if paragraphe:
                fermer_paragraphe()
            continue
        # --- règles Typora : toute formule dans un bloc $$ seul sur sa ligne, en colonne 0
        if "$$" in brute:
            if brute.strip() != "$$":
                alertes.append(f"l.{i} : « $$ » doit être seul sur sa ligne (bloc maths Typora)")
            elif brute != brute.lstrip() or brute.lstrip()[:1] in (">", "-", "*", "+", "|"):
                alertes.append(f"l.{i} : bloc $$ indenté, dans une puce, une citation ou un tableau")
            if brute.count("$$") % 2 == 1:
                if not affichage:
                    if i > 1 and lignes[i - 2].strip() != "":
                        alertes.append(f"l.{i} : ligne vide manquante avant le bloc $$")
                    affichage, debut_maths = True, i
                else:
                    if i < len(lignes) and lignes[i].strip() != "":
                        alertes.append(f"l.{i} : ligne vide manquante après le bloc $$")
                    affichage = False
            if paragraphe:
                fermer_paragraphe()
            continue
        if affichage:
            continue
        ligne = INLINE_CODE_RE.sub("", brute)
        for m in INLINE_CODE_RE.finditer(brute):
            if re.search(r"\d,\d", m.group(2)) and not re.search(r"[a-zA-Z_]\(", m.group(2)):
                alertes.append(f"l.{i} : virgule décimale dans du code inline « {m.group(2)[:40]} » (le code utilise le point)")
        if not ligne.strip():
            if paragraphe:
                fermer_paragraphe()
            continue
        paragraphe.append((i, ligne))
        if "$" in ligne.replace("\\$", ""):
            alertes.append(f"l.{i} : maths en ligne $…$ (non rendues dans Typora) — symboles en Unicode dans le texte, formules en bloc $$")
        if re.search(r"\\\(|\\\)|\\\[|\\\]", ligne):
            alertes.append(f"l.{i} : délimiteur \\( \\) \\[ \\] — jamais rendu dans Typora")
        else:
            cmd = re.search(r"\\[A-Za-z]+", ligne)
            if cmd:
                alertes.append(f"l.{i} : commande LaTeX hors d'un bloc $$ (« {cmd.group(0)} »)")
        indice = re.search(r"\S*[_^]\{[^}]*\}", ligne)
        if indice:
            alertes.append(f"l.{i} : indice ou exposant LaTeX hors d'un bloc $$ (« {indice.group(0)[:30]} ») — Unicode (kᵢ, x²) ou bloc $$")
        for m in LINK_RE.finditer(ligne):
            cible = m.group(2).strip("<>").strip()
            if re.match(r"^[a-z]+:", cible) or cible.startswith("#"):
                continue
            cible = urllib.parse.unquote(cible.split("#", 1)[0])
            if cible and not (chemin.parent / cible).exists():
                alertes.append(f"l.{i} : lien relatif cassé → {cible}")
    if paragraphe:
        fermer_paragraphe()
    if affichage:
        erreurs.append(f"l.{debut_maths} : bloc $$ jamais fermé")
    return erreurs, alertes


# --------------------------------------------------------------------------- statut
def statut(lignes: list[str]) -> dict[str, bool]:
    texte = "\n".join(lignes)
    tete = "\n".join(lignes[:8])
    return {
        "nav": ("Étape" in tete and "Suite" in tete),
        "demo": re.search(r"^## Démonstration\s*$", texte, re.M) is not None,
        "deroule": re.search(r"^### Déroulé, ligne par ligne\s*$", texte, re.M) is not None,
        "cas": re.search(r"^## Cas d[’']usage réels", texte, re.M) is not None,
        "sortie": re.search(r"^#{2,6} Sortie attendue", texte, re.M) is not None,
        "exo": re.search(r"^#{2,6} Exercice", texte, re.M) is not None,
        "squelette": re.search(r"^## Squelette algorithmique", texte, re.M) is not None,
    }


# --------------------------------------------------------------------------- fichier
def verifier(chemin: Path, executer_blocs: bool) -> dict:
    lignes, alertes_fichier = lire(chemin)
    blocs, non_ferme = blocs_de_code(lignes)
    res = {"chemin": chemin, "erreurs": [], "alertes": list(alertes_fichier), "blocs": [], "statut": statut(lignes)}
    if non_ferme:
        res["erreurs"].append(f"l.{non_ferme} : bloc de code jamais fermé")
    e, a = lint_prose(lignes, blocs, chemin)
    res["erreurs"] += e
    res["alertes"] += a
    titres_sortie = [i for i, l in enumerate(lignes, start=1) if re.match(r"^#{2,6} Sortie attendue", l)]
    executables = [b for b in blocs if b["lang"] == "python" and not est_extrait(b["code"])]
    if len(executables) > 1:
        res["alertes"].append(f"{len(executables)} blocs exécutables (règle : un seul bloc autonome par fichier)")
    for b in blocs:
        if b["lang"] != "python":
            continue
        if est_extrait(b["code"]):
            try:
                ast.parse(b["code"])
                res["blocs"].append((b["debut"], "EXTRAIT", ""))
            except SyntaxError as ex:
                res["blocs"].append((b["debut"], "FAIL", f"extrait non valide : {ex.msg} (l.{ex.lineno})"))
            continue
        erreurs, alertes = analyse_statique(b["code"])
        res["alertes"] += [f"bloc l.{b['debut']} : {x}" for x in alertes]
        if erreurs:
            res["blocs"].append((b["debut"], "FAIL", " ; ".join(erreurs)))
            continue
        if not executer_blocs:
            res["blocs"].append((b["debut"], "STATIQUE-OK", ""))
            continue
        rc, out, err = executer(b["code"])
        if rc != 0:
            raison = "timeout (30 s)" if rc is None else f"code retour {rc}"
            queue = "\n".join(err.strip().splitlines()[-12:])
            res["blocs"].append((b["debut"], "FAIL", f"{raison}\n{queue}"))
            continue
        lignes_out = [_norm(l) for l in out.splitlines()]
        non_vides = [l for l in lignes_out if l.strip()]
        if not non_vides or non_vides[-1].strip() != SENTINELLE:
            res["blocs"].append((b["debut"], "FAIL", f"dernière ligne attendue : « {SENTINELLE} »"))
            continue
        rc2, out2, _ = executer(b["code"])
        if rc2 != 0 or out2 != out:
            diff = next((f"« {x} » ≠ « {y} »" for x, y in zip(out.splitlines(), out2.splitlines()) if x != y), "longueurs différentes")
            res["blocs"].append((b["debut"], "FAIL", f"sortie non déterministe entre deux exécutions : {diff}"))
            continue
        titre = next((t for t in titres_sortie if t > b["fin"]), None)
        suivant = next((x["debut"] for x in executables if x["debut"] > b["fin"]), None)
        if titre and (suivant is None or titre < suivant):
            attendu_bloc = next((x for x in blocs if x["debut"] > titre), None)
            if attendu_bloc:
                attendu = [_norm(l) for l in attendu_bloc["code"].splitlines()]
                attendu = [l for l in attendu if l.strip() and l.strip() not in {"…", "...", "[…]", "[...]"}]
                manque = sous_sequence(attendu, lignes_out)
                if manque is not None:
                    res["blocs"].append((b["debut"], "FAIL", f"« Sortie attendue » ne correspond pas à la sortie réelle ; ligne introuvable (ou hors ordre) : « {manque} »"))
                    continue
        res["blocs"].append((b["debut"], "PASS", ""))
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chemins", nargs="+")
    ap.add_argument("--status", action="store_true", help="tableau de statut au format Markdown")
    ap.add_argument("--no-run", action="store_true", help="analyse statique et lint seulement")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    fichiers: list[Path] = []
    for c in args.chemins:
        p = Path(c)
        fichiers += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    total_fail = total_err = total_alertes = total_pass = 0
    resultats = []
    for f in fichiers:
        r = verifier(f, not args.no_run)
        resultats.append(r)
        fails = [x for x in r["blocs"] if x[1] == "FAIL"]
        total_fail += len(fails)
        total_pass += sum(1 for x in r["blocs"] if x[1] == "PASS")
        total_err += len(r["erreurs"])
        total_alertes += len(r["alertes"])
        if args.status:
            continue
        print(f"FICHIER {f}")
        for debut, etat, msg in r["blocs"]:
            print(f"  bloc l.{debut} : {etat}" + (f" — {msg}" if msg else ""))
        for e in r["erreurs"]:
            print(f"  ERREUR {e}")
        for a in r["alertes"]:
            print(f"  ALERTE {a}")
    if args.status:
        print("| Fichier | Nav | Démo | Déroulé | Squelette | Cas réels | Sortie | Exercice | Blocs PASS/FAIL |")
        print("|---|---|---|---|---|---|---|---|---|")
        for r in resultats:
            s = r["statut"]
            ok = sum(1 for x in r["blocs"] if x[1] == "PASS")
            ko = sum(1 for x in r["blocs"] if x[1] == "FAIL")
            m = lambda b: "oui" if b else "—"
            print(f"| {r['chemin'].as_posix()} | {m(s['nav'])} | {m(s['demo'])} | {m(s["deroule"])} | {m(s["squelette"])} | {m(s["cas"])} | {m(s['sortie'])} | {m(s['exo'])} | {ok}/{ko} |")
    print(f"RÉSUMÉ : {len(fichiers)} fichier(s), {total_pass} PASS, {total_fail} FAIL, {total_err} ERREUR(S), {total_alertes} ALERTE(S)")
    return 1 if (total_fail or total_err) else 0


if __name__ == "__main__":
    sys.exit(main())
