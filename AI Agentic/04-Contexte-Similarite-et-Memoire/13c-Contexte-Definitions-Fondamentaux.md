# Étape 13 ter — Contexte — Définitions fondamentales : l'ingénierie du contexte

> Étape 13 ter du parcours · Prérequis : [Évaluation : définitions](<../03-Schemas-Outils-et-Premiere-Evaluation/13b-Evaluation-Definitions-Fondamentaux.md>) · Suite : [Similarité cosinus, RAG et mémoire](<14-Similarite-Cosinus-RAG-et-Memoire.md>)

**Dossier :** 04-Contexte-Similarite-et-Memoire  
**Métiers :** AI Engineers, AI Agent Ops, AI Platform Team

Le modèle ne voit que ce qu'on met dans sa fenêtre de contexte. Un agent qui tourne vingt tours y empile son prompt, ses outils, chaque appel d'outil et chaque résultat : la fenêtre se remplit, la facture grossit comme un carré et la qualité baisse bien avant la limite. L'ingénierie du contexte est le métier qui décide **ce qui entre, dans quel ordre et sous quelle forme**. Ce fichier se lit avant la mémoire et le RAG, parce que ces deux dossiers ne sont que deux façons de remplir ce contexte.

Le mécanisme interne par lequel le modèle lit ce contexte, l'attention, est traité plus loin (étapes 31 à 37). Ici, on reste du côté de l'ingénieur qui construit la requête.

## Définitions

### Fenêtre de contexte

La fenêtre de contexte est le nombre maximal de tokens qu'un appel peut contenir, entrée et sortie comprises selon les fournisseurs. Elle se mesure en tokens, pas en caractères ni en mots. Une grande fenêtre n'est pas une invitation à tout y mettre : chaque token envoyé se paie à chaque appel, et un modèle retrouve moins bien une information noyée dans un long contexte.

### Composition du contexte

Une requête d'agent contient toujours les mêmes blocs, dans le même ordre :

1. **les définitions d'outils** (noms, descriptions, schémas) ;
2. **le prompt système** ;
3. **l'historique** : messages, appels d'outils, résultats d'outils ;
4. **les documents** injectés pour ce tour (RAG, mémoire) ;
5. **la réserve de sortie** : les tokens que le modèle doit pouvoir écrire, fixés par `max_tokens`.

Les deux premiers blocs sont stables ; les trois derniers changent à chaque tour.

### Préfixe stable et cache

Les fournisseurs mettent en cache le **préfixe** d'une requête : tout ce qui précède le premier octet différent. Si les outils et le prompt système sont identiques d'un appel à l'autre, ce préfixe est relu depuis le cache, à un tarif réduit et plus vite. Un seul octet changé au début (une date, un identifiant de requête, un outil ajouté dans un ordre différent) invalide tout le cache qui suit. Règle : le stable devant, le variable derrière.

### Dégradation avec la longueur

Plus le contexte est long, moins le modèle exploite chaque passage. Une information placée au milieu d'un long contexte est moins bien retrouvée qu'au début ou à la fin (phénomène dit *lost in the middle*, Liu et al., 2023). Des résultats d'outils anciens et volumineux diluent l'attention sur ce qui compte pour le tour courant. Moins de contexte, mieux choisi, donne souvent de meilleures réponses.

### Les cinq leviers

| Levier | Ce qu'il fait | Ce qu'il coûte |
|---|---|---|
| **Troncature des résultats d'outils** | Coupe un résultat trop long et le signale (`[… 18 000 caractères tronqués]`) | Une information coupée peut manquer ; l'outil doit renvoyer l'essentiel en premier |
| **Fenêtre glissante** | Garde les M derniers tours en entier | Les tours plus anciens disparaissent |
| **Compaction** | Remplace les tours anciens par un résumé | Le résumé peut effacer une nuance ou une incertitude |
| **Effacement des anciens résultats d'outils** | Retire le contenu des vieux `tool_result`, garde la trace de l'appel | Le modèle doit rappeler l'outil s'il en a besoin |
| **Sous-agent** | Confie une sous-tâche à un agent au contexte vierge, qui ne renvoie qu'un résumé | Un appel de plus ; le sous-agent ne voit pas tout |

À ces cinq leviers s'ajoute la **récupération à la demande** : plutôt que d'injecter dix documents, on donne au modèle un outil de recherche et des identifiants, et il charge ce dont il a besoin.

## Équations

Le budget d'un appel :

$$
n_{\text{outils}} + n_{\text{système}} + n_{\text{historique}} + n_{\text{documents}} + n_{\text{sortie}} \le B
$$

Si le préfixe fixe vaut

$$
n_0 = n_{\text{outils}} + n_{\text{système}}
$$

et que chaque tour ajoute Δ tokens à l'historique, le tour t envoie n₀ + (t−1)Δ tokens d'entrée, et le nombre maximal de tours avant de saturer la fenêtre est :

$$
T_{\max} = \left\lfloor \frac{B - n_0 - n_{\text{sortie}}}{\Delta} \right\rfloor + 1
$$

Sur T tours sans gestion du contexte, l'entrée cumulée vaut

$$
T n_0 + \Delta \dfrac{T(T-1)}{2}
$$

Un terme en T², démontré à l'étape 72. Avec une fenêtre glissante de M tours et un résumé de r tokens pour le reste, chaque tour au-delà du (M+1)-ième coûte au plus n₀ + MΔ + r, une constante : la croissance redevient linéaire.

### Décryptage des symboles

$$
B
$$

**Sens :** taille de la fenêtre, en tokens · **Variable Python :** `budget`

$$
n_0
$$

**Sens :** tokens du préfixe fixe (outils + prompt système) · **Variable Python :** `n_fixe`

$$
n_{\text{sortie}}
$$

**Sens :** réserve de sortie (`max_tokens`) · **Variable Python :** `reserve_sortie`

$$
\Delta
$$

**Sens :** tokens ajoutés par tour (appel + résultat d'outil) · **Variable Python :** `delta`

$$
M
$$

**Sens :** tours récents gardés en entier · **Variable Python :** `tours_recents`

$$
r
$$

**Sens :** tokens du résumé des tours anciens · **Variable Python :** `tokens(resume)`

## Démonstration

**Tₘₐₓ.** Le tour t contient n₀ + (t−1)Δ tokens d'entrée et doit laisser nₛₒᵣₜᵢₑ tokens libres : n₀ + (t−1)Δ + nₛₒᵣₜᵢₑ ≤ B, soit t − 1 ≤ (B − n₀ − nₛₒᵣₜᵢₑ)/Δ. Le plus grand entier t qui vérifie cette inégalité est la partie entière du membre de droite, plus 1.

Exemple : B = 200 000, n₀ = 3 000, nₛₒᵣₜᵢₑ = 16 000, Δ = 1 500.

$$
(200\,000 - 3\,000 - 16\,000)/1\,500 = 181\,000/1\,500 = 120{,}67 ,
$$

donc Tₘₐₓ = 121 tours.

**Fenêtre glissante.** Avec M = 10 et un résumé de r = 500 tokens, sur T = 40 tours :

- tours 1 à 11 : historique complet,

$$
\sum_{t=1}^{11} (3\,000 + (t-1) \times 1\,500) = 11 \times 3\,000 + 1\,500 \times (0 + 1 + \cdots + 10) = 33\,000 + 82\,500 = 115\,500 ;
$$

- tours 12 à 40 (29 tours) : 3 000 + 10 × 1 500 + 500 = 18 500 chacun, soit 536 500 ;
- total : 652 000 tokens d'entrée.

Sans gestion :

$$
40 \times 3\,000 + 1\,500 \times 40 \times 39/2 = 120\,000 + 1\,170\,000 = 1\,290\,000 .
$$

La fenêtre glissante divise ici l'entrée cumulée par 1,98, et l'écart grandit avec T parce qu'on remplace un terme en T² par un terme en T.

## Architecture hexagonale : l'assemblage du contexte est un service

Dans le code, une seule fonction construit la requête : l'**assembleur de contexte**. La boucle d'agent (étape 1) ne fait plus `llm.create(messages=messages)` sur l'historique brut, mais sur ce que l'assembleur lui rend. Les règles (budget, troncature, compaction, ordre) vivent dans ce service, testable sans modèle, comme un `ContextAssembler` injecté dans un service Spring.

## Construire depuis une feuille blanche

On construit l'assembleur de contexte d'un agent de support qui interroge un système de tickets. Ses résultats d'outils sont parfois énormes (un historique de ticket de 20 000 caractères). Le programme tronque ces résultats, garde les tours récents, compacte les anciens en un résumé quand le budget déborde, sélectionne les documents par score dans la place restante, puis vérifie que le préfixe reste identique d'un appel à l'autre pour le cache. Il termine par les nombres de la démonstration.

### Déroulé, ligne par ligne

**`tokens(texte)`** estime `ceil(len(texte) / 4)`, comme à l'étape 4. En production, on utilise le compte exact du fournisseur.

**`tronquer(texte, max_tokens)`** garde le début du texte et ajoute `[… N caractères tronqués]`. La place du marqueur est retirée d'avance (`max_tokens * 4 - 40` caractères gardés) pour que le résultat tienne toujours dans `max_tokens`. Le programme le vérifie sur un résultat de 20 000 caractères.

**`resumer(tours)`** est un faux résumeur déterministe : il garde la première phrase de chaque message. En production, c'est un appel au modèle (souvent un modèle moins cher), avec une consigne : conserver les faits confirmés, les décisions et les **incertitudes**.

**`AssembleurContexte.assembler(system, outils, historique, documents)`** :

1. calcule le préfixe fixe `outils + system` et son coût `n_fixe` ;
2. tronque chaque résultat d'outil (`role == "tool"`) à `max_resultat` tokens ;
3. calcule la place disponible : `budget - reserve_sortie - n_fixe` ;
4. si l'historique ne tient pas, garde les `tours_recents` derniers messages et remplace les autres par **un** message de résumé ; si cela ne tient toujours pas, lève une erreur plutôt que d'envoyer une requête qui serait refusée ;
5. ajoute les documents par score décroissant tant qu'ils tiennent ;
6. renvoie le préfixe, les messages, les documents retenus, le total et un indicateur `compacte`.

**`empreinte_prefixe(ctx)`** calcule le SHA-256 du préfixe. Deux appels successifs, avec un historique qui a grandi, doivent donner la même empreinte : c'est la condition pour que le cache serve.

**`entree_cumulee(T, n0, delta, M=None, r=0)`** additionne l'entrée de chaque tour, avec ou sans fenêtre glissante. Le programme vérifie Tₘₐₓ = 121, 1 290 000 et 652 000.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tokens(texte)`** — Cette fonction est le métreur qui évalue un texte à la toise plutôt qu'au centimètre : elle reçoit une chaîne, divise sa longueur en caractères par 4 et arrondit à l'entier supérieur, puis renvoie ce nombre de tokens estimé, sans lever d'exception. C'est l'unité de compte de tout l'assembleur : le préfixe fixe du programme coûte 504 tokens, un résultat d'outil de 20 000 caractères en coûterait 5 000, et le budget de 8 000 tokens se répartit avec elle. En production, on la remplacerait par le compte exact du fournisseur.

**`tronquer(texte, max_tokens)`** — Celle-ci est le monteur qui coupe une bobine trop longue en laissant un carton « suite coupée » : elle reçoit un texte et une limite en tokens, renvoie le texte tel quel s'il tient dans la limite, et sinon garde ses max_tokens × 4 − 40 premiers caractères, les 40 caractères réservés laissant la place au marqueur, puis ajoute sur une nouvelle ligne le nombre de caractères retirés. Elle renvoie ce texte borné : un résultat de 20 000 caractères limité à 500 tokens tombe à 498 tokens et se termine par « [… 18040 caractères tronqués] », si bien que le modèle sait qu'il ne lit qu'un extrait.

**`resumer(tours)`** — Cette fonction joue le greffier pressé qui ne retient de chaque intervention que la première phrase : elle reçoit une liste de messages, coupe le contenu de chacun au premier point, retire les espaces, écarte les morceaux vides et renvoie une seule chaîne qui commence par « Résumé des tours précédents : », les phrases étant séparées par des points-virgules. Elle est déterministe, donc testable ; dans le programme, le résumé des anciens tours commence par « Je lis le ticket T-1 ; Ticket T-1 : client C-1 ». En production, ce rôle reviendrait à un appel au modèle chargé de garder les faits, les décisions et les incertitudes.

**`AssembleurContexte.__init__(budget, reserve_sortie, max_resultat, tours_recents)`** — Le constructeur de l'assembleur fixe les règles du jeu, comme un intendant qui affiche à l'entrée de la salle la jauge, les places réservées et le temps de parole : il reçoit le budget total en tokens, la réserve laissée à la réponse du modèle, la taille maximale d'un résultat d'outil et le nombre de messages récents à garder intacts, et les range dans l'objet sans rien vérifier ni renvoyer. Dans `main`, l'assembleur reçoit un budget de 8 000 tokens, une réserve de 1 500, des résultats bornés à 500 tokens et les 6 derniers messages protégés.

**`AssembleurContexte.assembler(system, outils, historique, documents)`** — C'est le régisseur qui compose, à chaque tour, ce que le modèle verra, dans un ordre immuable : il reçoit le prompt système, la description des outils, l'historique et une liste de documents notés, place d'abord le préfixe fixe, outils puis prompt, calcule la place restante après la réserve de sortie, tronque chaque résultat d'outil, puis, si l'historique déborde, remplace les anciens messages par un seul résumé en gardant les derniers intacts. Il lève `ValueError` si même la version compactée ne tient pas, ajoute ensuite les documents par score décroissant tant qu'ils tiennent, et renvoie le préfixe, les messages, les documents retenus, le total, l'indicateur de compaction et le coût du préfixe : au tour 12, 7 messages, trois documents et 5 182 tokens sur 6 500.

**`empreinte_prefixe(ctx)`** — Cette fonction est le notaire qui scelle la partie fixe du contexte pour vérifier qu'elle n'a pas bougé d'un iota : elle reçoit le dictionnaire produit par `assembler`, calcule l'empreinte SHA-256 de son préfixe encodé en UTF-8 et renvoie les douze premiers caractères hexadécimaux. Deux tours dont le préfixe est identique ont donc la même empreinte, `6870709a1fdb` aux tours 12 et 13 dans la sortie attendue, condition pour que le cache du fournisseur serve ; une date ajoutée en tête du prompt système suffit à la changer.

**`t_max(B, n0, sortie, delta)`** — Celle-ci est le calculateur qui annonce combien de tours une conversation peut durer avant de saturer la fenêtre : elle reçoit la taille B de la fenêtre, la taille n₀ du premier tour, la réserve de sortie et l'accroissement δ de chaque tour, puis renvoie la division entière de B − n₀ − sortie par δ, augmentée de 1. Elle ne contrôle pas ses entrées. Avec une fenêtre de 200 000 tokens, un premier tour de 3 000, une réserve de 16 000 et 1 500 tokens de plus par tour, elle renvoie 121 tours.

**`entree_cumulee(T, n0, delta, M, r)`** — Cette fonction est le comptable qui additionne tout ce que le modèle relit, tour après tour : elle reçoit le nombre de tours T, la taille n₀ du premier, l'accroissement δ, et facultativement la taille M d'une fenêtre glissante et le coût r du résumé qui la remplace. Pour chaque tour t, elle ajoute n₀ + (t − 1) δ tant que l'historique n'a pas dépassé M tours, ou si aucune fenêtre n'est fixée, puis n₀ + M δ + r au-delà. Elle renvoie ce total : 1 290 000 tokens pour 40 tours sans gestion, contre 652 000 avec une fenêtre de 10 tours et un résumé de 500 tokens, soit une division par 1,98.

**`historique_simule(n_tours)`** — C'est le figurant qui rejoue une conversation de support réaliste : la fonction reçoit un nombre de tours et, pour chacun, ajoute un message de l'assistant, « Je lis le ticket T-i. Appel de lire_ticket. », puis un résultat d'outil qui décrit le ticket du client fictif C-i, suivi de 3 000 caractères de remplissage, ou de 20 000 au troisième tour pour simuler un historique de ticket énorme. Elle renvoie la liste de ces deux messages par tour, soit 24 messages pour 12 tours, que l'assembleur doit tronquer puis compacter.

**`main()`** — C'est le chef d'équipe qui fait passer l'assembleur par quatre épreuves : il tronque d'abord un texte de 20 000 caractères à 500 tokens et vérifie qu'un texte court reste intact, puis assemble le contexte du tour 12, compacté en un résumé plus 6 messages récents, avec le meilleur document `kb-17` en tête et des résultats d'outils tous sous 500 tokens. Il vérifie ensuite que le préfixe garde la même empreinte au tour 13 et qu'une date en tête du prompt système la change, et termine par les formules : 121 tours au plus, 1 290 000 tokens relus sans gestion et 652 000 avec la fenêtre glissante.

```python
"""Étape 13 ter — ingénierie du contexte : budget, troncature, compaction, documents, préfixe stable."""
import hashlib
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def tokens(texte: str) -> int:
    return math.ceil(len(texte) / 4)


def tronquer(texte: str, max_tokens: int) -> str:
    if tokens(texte) <= max_tokens:
        return texte
    garde = max_tokens * 4 - 40                       # place réservée au marqueur
    return texte[:garde] + f"\n[… {len(texte) - garde} caractères tronqués]"


def resumer(tours: list[dict]) -> str:
    """Faux résumeur déterministe : la première phrase de chaque message."""
    phrases = [m["content"].split(".")[0].strip() for m in tours]
    return "Résumé des tours précédents : " + " ; ".join(p for p in phrases if p) + "."


class AssembleurContexte:
    def __init__(self, budget: int, reserve_sortie: int, max_resultat: int, tours_recents: int):
        self.budget, self.reserve_sortie = budget, reserve_sortie
        self.max_resultat, self.tours_recents = max_resultat, tours_recents

    def assembler(self, system: str, outils: str, historique: list[dict], documents: list[tuple]) -> dict:
        prefixe = outils + "\n" + system
        n_fixe = tokens(prefixe)
        place = self.budget - self.reserve_sortie - n_fixe
        hist = [dict(m, content=tronquer(m["content"], self.max_resultat)) if m["role"] == "tool" else m
                for m in historique]
        compacte = False
        if sum(tokens(m["content"]) for m in hist) > place:
            anciens, recents = hist[:-self.tours_recents], hist[-self.tours_recents:]
            hist = [{"role": "user", "content": resumer(anciens)}] + recents
            compacte = True
        n_hist = sum(tokens(m["content"]) for m in hist)
        if n_hist > place:
            raise ValueError("le contexte ne tient pas même après compaction")
        retenus, reste = [], place - n_hist
        for score, doc_id, texte in sorted(documents, reverse=True):
            if tokens(texte) <= reste:
                retenus.append(doc_id)
                reste -= tokens(texte)
        total = self.budget - self.reserve_sortie - reste
        return {"prefixe": prefixe, "messages": hist, "documents": retenus,
                "total": total, "compacte": compacte, "n_fixe": n_fixe}


def empreinte_prefixe(ctx: dict) -> str:
    return hashlib.sha256(ctx["prefixe"].encode("utf-8")).hexdigest()[:12]


def t_max(B: int, n0: int, sortie: int, delta: int) -> int:
    return (B - n0 - sortie) // delta + 1


def entree_cumulee(T: int, n0: int, delta: int, M: int | None = None, r: int = 0) -> int:
    total = 0
    for t in range(1, T + 1):
        if M is None or t - 1 <= M:
            total += n0 + (t - 1) * delta
        else:
            total += n0 + M * delta + r
    return total


SYSTEM = "Tu es l'agent de support d'un éditeur SaaS à Dubaï. " * 20
OUTILS = '{"name": "lire_ticket", "input_schema": {"ticket_id": "string"}} ' * 15


def historique_simule(n_tours: int) -> list[dict]:
    hist = []
    for i in range(1, n_tours + 1):
        hist.append({"role": "assistant", "content": f"Je lis le ticket T-{i}. Appel de lire_ticket."})
        taille = 20_000 if i == 3 else 3_000
        hist.append({"role": "tool", "content": f"Ticket T-{i} : client C-{i}, statut ouvert. " + "x" * taille})
    return hist


def main() -> None:
    print("1. Troncature")
    gros = "y" * 20_000
    court = tronquer(gros, 500)
    print(f"  20 000 caractères -> {tokens(court)} tokens, se termine par {court.splitlines()[-1]!r}")
    assert tokens(court) <= 500 and court.endswith("caractères tronqués]")
    assert tronquer("court", 500) == "court"

    print("2. Assemblage d'un agent au tour 12")
    asm = AssembleurContexte(budget=8_000, reserve_sortie=1_500, max_resultat=500, tours_recents=6)
    docs = [(0.91, "kb-17", "z" * 4_000), (0.84, "kb-02", "z" * 6_000), (0.40, "kb-33", "z" * 2_000)]
    ctx = asm.assembler(SYSTEM, OUTILS, historique_simule(12), docs)
    print(f"  préfixe fixe {ctx['n_fixe']} tokens ; {len(ctx['messages'])} messages ; compacté : {ctx['compacte']}")
    print(f"  documents retenus : {ctx['documents']} ; total {ctx['total']} / {8_000 - 1_500} tokens disponibles")
    print(f"  1er message : {ctx['messages'][0]['content'][:70]}…")
    assert ctx["compacte"] and len(ctx["messages"]) == 7                    # 1 résumé + 6 récents
    assert ctx["total"] <= 8_000 - 1_500
    assert ctx["documents"][0] == "kb-17"                                    # le meilleur score d'abord
    assert all(tokens(m["content"]) <= 500 for m in ctx["messages"] if m["role"] == "tool")

    print("3. Préfixe stable pour le cache")
    ctx13 = asm.assembler(SYSTEM, OUTILS, historique_simule(13), docs)
    print(f"  empreinte tour 12 = {empreinte_prefixe(ctx)}, tour 13 = {empreinte_prefixe(ctx13)}")
    assert empreinte_prefixe(ctx) == empreinte_prefixe(ctx13)
    date = asm.assembler("Date : 2026-11-11. " + SYSTEM, OUTILS, historique_simule(13), docs)
    assert empreinte_prefixe(date) != empreinte_prefixe(ctx)                  # une date au début casse le cache
    print("  une date ajoutée en tête du prompt système change l'empreinte : cache perdu")

    print("4. Formules")
    tm = t_max(200_000, 3_000, 16_000, 1_500)
    naif = entree_cumulee(40, 3_000, 1_500)
    glissant = entree_cumulee(40, 3_000, 1_500, M=10, r=500)
    print(f"  T_max = {tm} tours ; 40 tours : {naif:,} tokens sans gestion, {glissant:,} avec fenêtre M=10 "
          f"(÷{naif / glissant:.2f})")
    assert tm == 121 and naif == 1_290_000 and glissant == 652_000
    assert naif == 40 * 3_000 + 1_500 * 40 * 39 // 2
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Troncature
  20 000 caractères -> 498 tokens, se termine par '[… 18040 caractères tronqués]'
2. Assemblage d'un agent au tour 12
  préfixe fixe 504 tokens ; 7 messages ; compacté : True
  documents retenus : ['kb-17', 'kb-02', 'kb-33'] ; total 5182 / 6500 tokens disponibles
  1er message : Résumé des tours précédents : Je lis le ticket T-1 ; Ticket T-1 : clie…
3. Préfixe stable pour le cache
  empreinte tour 12 = 6870709a1fdb, tour 13 = 6870709a1fdb
  une date ajoutée en tête du prompt système change l'empreinte : cache perdu
4. Formules
  T_max = 121 tours ; 40 tours : 1,290,000 tokens sans gestion, 652,000 avec fenêtre M=10 (÷1.98)
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un contexte se gère avec un budget, comme une mémoire de serveur. Les résultats d'outils sont bornés, l'historique est compacté quand il déborde, les documents se disputent la place restante par score, et le préfixe reste octet pour octet identique pour que le cache serve.

### Mécanisme du programme, en détail

Le programme commence par une mesure volontairement grossière : `tokens` compte un token pour quatre caractères, arrondi vers le haut, ce qui suffit pour raisonner sur un budget sans dépendre d'un tokenizer particulier. `tronquer` utilise cette mesure pour couper un texte trop long : si le texte tient dans la limite, il est rendu tel quel ; sinon, la fonction garde les premiers caractères, en réservant quarante caractères pour un marqueur qui dit combien de caractères ont été retirés, de sorte que le modèle sache qu'il lit un extrait et non le résultat complet d'un outil. `resumer` joue le rôle d'un résumeur : il garde la première phrase de chaque message, ce qui le rend déterministe et donc testable, là où un vrai résumé serait demandé au modèle.

Tout le travail se fait dans `AssembleurContexte.assembler`. La méthode place d'abord le préfixe fixe, les outils puis le prompt système, et calcule la place qui reste une fois ce préfixe et la réserve de sortie retirés du budget. Elle tronque ensuite chaque résultat d'outil de l'historique à `max_resultat` tokens, parce que ce sont presque toujours les résultats d'outils qui font exploser le contexte. Si l'historique dépasse encore la place disponible, elle le compacte : les anciens messages sont remplacés par un seul résumé et seuls les `tours_recents` derniers messages sont gardés intacts. Si même après compaction l'historique ne tient pas, elle lève une erreur plutôt que d'envoyer un contexte tronqué au hasard. Enfin, elle trie les documents par score décroissant et les ajoute un par un tant qu'ils tiennent dans la place restante, ce qui est un remplissage glouton.

`empreinte_prefixe` calcule un SHA-256 du préfixe : deux tours dont le préfixe est identique ont la même empreinte, donc le cache du fournisseur peut servir ce préfixe, alors qu'une date ajoutée en tête du prompt système change l'empreinte et fait perdre le cache, ce que vérifie le programme. `t_max` et `entree_cumulee` traduisent les deux formules du fichier : le nombre maximal de tours avant de dépasser la fenêtre, et le total de tokens d'entrée relus sur T tours, avec ou sans fenêtre glissante de M tours.

## Squelette algorithmique

L'algorithme assemble, à chaque tour, le contexte envoyé au modèle sous une contrainte de budget : d'abord ce qui ne bouge pas, puis l'historique réduit si besoin, puis les meilleurs documents qui tiennent encore.

```text
ALGORITHME AssemblerContexte
ENTRÉES : budget B, réserve de sortie, système, outils, historique, documents (score, id, texte),
          max_résultat, tours_récents
SORTIE  : (préfixe, messages, documents retenus, total)

  préfixe ← outils + système                      (fixe d'un tour à l'autre : il reste en cache)
  place ← B − réserve de sortie − tokens(préfixe)
  POUR CHAQUE message m de l'historique FAIRE
      SI m vient d'un outil ALORS m ← Tronquer(m, max_résultat)
  FIN POUR
  SI tokens(historique) > place ALORS
      historique ← [Résumer(anciens messages)] + les tours_récents derniers messages
  FIN SI
  SI tokens(historique) > place ALORS ERREUR « le contexte ne tient pas »
  reste ← place − tokens(historique)
  trier les documents par score décroissant
  POUR CHAQUE document d FAIRE
      SI tokens(d) ≤ reste ALORS retenir d ; reste ← reste − tokens(d)
  FIN POUR
  RETOURNER préfixe, historique, documents retenus, B − réserve − reste
```

**Complexité.** L'assemblage est linéaire en nombre de messages : une passe pour tronquer, une passe pour compter, une passe éventuelle pour résumer, soit O(m × L) en caractères lus pour m messages de longueur L. Le tri des d documents coûte O(d log d) et leur remplissage glouton O(d). Le calcul d'empreinte est linéaire en la taille du préfixe. La formule du coût cumulé montre l'enjeu : sans gestion, T tours relisent T n₀ + Δ T (T − 1) / 2 tokens, une croissance quadratique que la fenêtre glissante ramène à une croissance linéaire au-delà de M tours.

**Du squelette au code.** `AssemblerContexte` correspond à `AssembleurContexte.assembler`, `Tronquer` à `tronquer`, `Résumer` à `resumer` et `tokens` à `tokens`. La propriété « préfixe stable » se vérifie avec `empreinte_prefixe`, et les deux formules du fichier sont `t_max` et `entree_cumulee`.

## Cas d'usage réels aux Émirats

Les tailles et tarifs sont illustratifs.

### SaaS — agent de support sur un historique de tickets

L'agent de support d'un éditeur de Dubaï lit des tickets dont l'historique complet dépasse parfois 50 000 caractères. L'outil `lire_ticket` renvoie d'abord le statut, le client et les trois derniers échanges, puis le reste : la troncature à 2 000 tokens coupe donc la partie la moins utile. Les tours au-delà des dix derniers sont compactés en un résumé qui garde explicitement les engagements pris auprès du client (« remboursement promis le 3 »), parce qu'un résumé qui les perdrait ferait répéter ou contredire une promesse.

### Banque — conformité d'un dossier KYC volumineux

Un agent de revue KYC doit lire 40 pièces d'un dossier entreprise. Plutôt que d'injecter les 40 pièces, il reçoit leur liste (titre, type, date) et un outil `lire_piece(id)` : il charge les statuts, l'extrait de registre et les pièces d'identité des bénéficiaires effectifs, soit 6 pièces au lieu de 40. Le contexte reste sous 30 000 tokens, et la trace montre exactement quelles pièces ont fondé l'avis transmis à l'analyste.

### BTP — sous-agent de lecture de cahier des charges

Un groupe de construction fait analyser un cahier des charges de 300 pages. L'agent principal confie chaque lot (gros œuvre, MEP, finitions) à un sous-agent au contexte vierge, qui lit son lot et ne renvoie qu'une fiche de 400 tokens : exigences, pénalités, délais. L'agent principal ne voit jamais les 300 pages, seulement trois fiches, et son préfixe stable reste en cache d'un lot à l'autre.

## Pièges et limites

- **Remplir la fenêtre parce qu'elle est grande.** Le coût et la dilution augmentent avec chaque token, même loin de la limite.
- **Résumer sans consigne.** Un résumé libre transforme « le paiement a peut-être échoué » en « le paiement a échoué ». La consigne de compaction exige de garder les incertitudes et les engagements.
- **Tronquer la fin d'un résultat qui met l'essentiel à la fin.** L'outil doit trier son résultat ; sinon on tronque au milieu ou on extrait les champs utiles.
- **Changer l'ordre des outils d'un appel à l'autre.** Un dictionnaire non trié ou un outil ajouté dynamiquement en tête invalide le cache de tout ce qui suit.
- **Ne pas lever d'erreur quand rien ne tient.** Une requête trop longue est refusée par l'API ; mieux vaut un échec explicite, journalisé, qu'une erreur réseau difficile à lire.

### Exercice feuille blanche

1. Calculer Tₘₐₓ pour B = 128 000, n₀ = 5 000, nₛₒᵣₜᵢₑ = 8 000, Δ = 2 500. (Réponse : ⌊ 115 000/2 500 ⌋ + 1 = 47.)
2. Réécrire `assembler` sans regarder, puis ajouter le levier « effacement des anciens résultats d'outils » : au-delà des 4 derniers résultats, remplacer le contenu par `[résultat effacé, rappeler l'outil si besoin]`.
3. Trouver le bug : un collègue place la date du jour au début du prompt système « pour que le modèle la connaisse ». Quel effet sur le coût d'un agent à 30 tours, et où mettre la date ? (Réponse : le préfixe n'est plus jamais en cache, chaque tour paie le préfixe plein tarif ; la date va dans le premier message utilisateur.)

## Pour aller plus loin

- La croissance en T² de l'entrée cumulée et l'effet chiffré du cache sur une facture annuelle sont démontrés à l'[étape 72](<../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>).
- La mémoire longue (étape 15 bis) et le RAG (étapes 18 à 30) décident **quels** souvenirs et documents se disputent la place calculée ici.
- Pourquoi un passage noyé au milieu d'un long contexte pèse moins : l'attention, [étape 31](<../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>).

> Suite : [Similarité cosinus, RAG et mémoire](<14-Similarite-Cosinus-RAG-et-Memoire.md>) — étape 14.
