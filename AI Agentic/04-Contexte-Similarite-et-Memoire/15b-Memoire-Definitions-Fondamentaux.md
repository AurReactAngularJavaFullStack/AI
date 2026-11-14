# Étape 15 bis — Mémoire — Définitions fondamentales : ce qu'un agent retient

> Étape 15 bis du parcours · Prérequis : [Fondements du RAG et de la mémoire](<15-Fondements-RAG-et-Memoire.md>) · Suite : [Décroissance d'un souvenir](<16-Memoire-Formule-Decroissance-Temporelle.md>)

**Dossier :** 04-Contexte-Similarite-et-Memoire  
**Métiers :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers

Le modèle n'a pas de mémoire : chaque appel repart de ce qu'on lui envoie. Ce que l'on appelle « mémoire d'un agent » est un ensemble de mécanismes **extérieurs au modèle** qui décident quoi garder d'une conversation, comment le ranger et quand le ressortir. Ce fichier pose le vocabulaire avant les deux formules du dossier : la décroissance d'un souvenir (étape 16) et le score qui choisit les souvenirs à injecter (étape 17). Il construit ensuite un magasin de mémoire minimal, avec déduplication, mise à jour des faits, isolation par client et effacement.

## Définitions

### Mémoire de travail

La mémoire de travail est le contexte de l'appel en cours : prompt système, historique, documents. Elle est bornée par la fenêtre et coûte des tokens à chaque tour (étape 13 ter). Tout ce qui n'y est pas, le modèle l'ignore.

### Mémoire courte

La mémoire courte est l'historique de la session : la liste `messages` de l'étape 1. Elle disparaît à la fin de la conversation, ou plus tôt si l'on compacte l'historique.

### Mémoire longue

La mémoire longue survit aux sessions. Elle est stockée hors du modèle (base de données, index vectoriel) et on en injecte quelques éléments dans le contexte quand ils sont utiles. On en distingue trois sortes, reprises des sciences cognitives :

| Type | Ce qu'elle contient | Exemple | Comment on la met à jour |
|---|---|---|---|
| **Épisodique** | des événements datés | « Le 3 mars, le client a contesté la facture FAC-1182. » | on ajoute ; on ne réécrit pas un événement passé |
| **Sémantique** | des faits stables sur le monde ou l'utilisateur | « Le client préfère être contacté en arabe. » | le fait le plus récent remplace l'ancien, qui reste dans l'historique |
| **Procédurale** | des savoir-faire | « Pour ce client, toujours vérifier le bon de commande avant la TVA. » | relue et validée par un humain avant d'entrer en service |

### Les quatre opérations

1. **Écrire.** Une politique d'écriture décide ce qui mérite d'être retenu. Tout retenir remplit la mémoire de bruit ; ne rien retenir fait reposer les mêmes questions. Les candidats typiques : préférences déclarées, décisions, engagements, corrections faites par l'utilisateur.
2. **Consolider.** Un même fait dit deux fois ne doit pas exister en deux exemplaires : on détecte les doublons (par similarité, étape 14) et on fusionne. Un fait qui change (nouvelle adresse) remplace l'ancien.
3. **Récupérer.** Au moment de répondre, on choisit les souvenirs à injecter par un score qui combine pertinence, récence et importance (étapes 16 et 17).
4. **Oublier.** Deux sens très différents. *Oublier dans le classement* : un vieux souvenir pèse moins (décroissance, étape 16), mais il existe toujours. *Effacer* : la donnée est supprimée, par exemple à la demande de la personne concernée. Seul le second satisfait une demande d'effacement de données personnelles.

### Provenance

Chaque souvenir garde sa source (quelle conversation, quel outil), sa date et son niveau de confiance. Un souvenir sans provenance ne peut ni être justifié, ni corrigé, ni effacé proprement.

### Isolation

Une mémoire appartient à un utilisateur ou à un client (*tenant*). La récupération filtre **d'abord** par propriétaire, **ensuite** par pertinence. Un filtre oublié et l'agent répond à un client avec les préférences d'un autre : c'est une fuite de données, pas un bug de pertinence.

### Mémoire comme outil

Deux architectures coexistent. Dans la mémoire **automatique**, le programme écrit et récupère à chaque tour, sans que le modèle le demande. Dans la mémoire **comme outil**, l'agent dispose d'outils `memoriser(...)` et `rappeler(...)` et décide lui-même quand s'en servir. La seconde est plus économe et plus lisible dans la trace ; la première ne dépend pas du jugement du modèle. Beaucoup d'agents combinent les deux : faits du profil injectés automatiquement, souvenirs épisodiques à la demande.

## Architecture hexagonale : la mémoire est un port sortant

Pour le domaine, la mémoire est un port : `memoriser`, `rappeler`, `effacer`. L'adaptateur peut être une table SQL, un index vectoriel ou les deux. Le domaine ne sait pas comment la similarité est calculée ; il sait seulement que `rappeler(client, question, k)` renvoie au plus `k` souvenirs **de ce client**. En Java, c'est un `MemoryRepository` injecté dans le service d'agent, avec l'identifiant du tenant obligatoire dans chaque signature.

## Construire depuis une feuille blanche

On construit la mémoire longue de l'agent de relation client d'une agence immobilière. Le programme écrit des souvenirs pour deux clients, détecte un doublon et le fusionne, remplace un fait sémantique qui change en gardant l'ancien dans l'historique, récupère les souvenirs utiles par un score simple, vérifie qu'un client ne voit jamais les souvenirs d'un autre, puis efface toute la mémoire d'un client à sa demande.

### Déroulé, ligne par ligne

**`vecteur(texte)`** transforme un texte en sac de mots : un `Counter` des mots en minuscules, sans ponctuation. C'est un plongement (*embedding*) de démonstration ; en production, on utilise un modèle d'embeddings, mais le cosinus se calcule de la même façon.

**`cosinus(a, b)`** applique la formule de l'étape 14 : produit scalaire divisé par le produit des normes, avec 0 si l'un des vecteurs est vide.

**`Souvenir`** porte le propriétaire, le type (`episodique`, `semantique`, `procedurale`), le texte, une `cle` facultative pour les faits sémantiques (`langue_contact`), l'importance entre 0 et 1, la source et l'heure.

**`Memoire.memoriser(...)`** :

- pour un fait sémantique avec une `cle`, cherche un fait actif de même clé pour ce client ; s'il existe, il passe dans `historique` et le nouveau le remplace ;
- sinon, cherche un souvenir du même client dont le cosinus avec le nouveau texte dépasse `seuil_doublon` (0,9) : c'est un doublon, on met à jour son heure et on garde la plus forte importance au lieu de créer un second exemplaire ;
- sinon, ajoute le souvenir.

**`Memoire.rappeler(client, question, heure, k)`** filtre d'abord par client, puis calcule `cosinus + 0.995 ** heures_ecoulees + importance` et renvoie les `k` meilleurs. Les poids sont égaux et la décroissance horaire est celle de l'étape 16 ; l'étape 17 explique comment les régler.

**`Memoire.effacer(client)`** supprime les souvenirs actifs **et** l'historique du client, puis renvoie le nombre d'éléments supprimés.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`vecteur(texte)`** — Cette fonction est le documentaliste qui réduit un texte à la liste des mots qu'il contient, avec leur nombre d'apparitions : elle reçoit une chaîne, la passe en minuscules, en extrait les mots avec l'expression régulière `\w+`, ce qui fait tomber toute la ponctuation, et renvoie un `Counter` qui associe à chaque mot son nombre d'occurrences. Elle ne lève rien et renvoie un sac vide pour un texte vide. C'est un plongement de démonstration : grâce à lui, « … à Dubai Marina. » et « … à Dubai Marina ! » donnent exactement le même sac, donc un cosinus de 1 et une fusion.

**`cosinus(a, b)`** — Celle-ci est le juge qui compare deux sacs de mots en ne retenant que leur orientation : elle reçoit deux `Counter`, calcule le produit scalaire sur les seuls mots qu'ils ont en commun, puis les deux normes, et renvoie 0 si l'un des sacs est vide, ou sinon le produit divisé par le produit des normes. Elle ne lève jamais d'exception, ce qui la distingue du cosinus de l'étape 14, qui refuse le vecteur nul. Le programme vérifie qu'elle vaut 1 pour deux textes identiques et 0 face à un texte vide ; `memoriser` s'en sert pour repérer les doublons, `rappeler` pour noter la pertinence.

**`Memoire.__init__(seuil_doublon, decroissance)`** — Le constructeur ouvre deux registres vides, comme un archiviste qui installe un classeur des dossiers en cours et une armoire des pièces remplacées : il reçoit le seuil de cosinus au-delà duquel deux souvenirs sont jugés identiques, 0,9 par défaut, et le facteur de décroissance horaire, 0,995 par défaut, crée la liste `actifs` et la liste `historique`, puis garde les deux réglages. Il ne renvoie rien ; `main` crée une seule mémoire avec ces valeurs par défaut, partagée entre les clients C-17 et C-42.

**`Memoire.memoriser(s)`** — C'est l'archiviste qui décide, pour chaque nouvelle pièce, s'il faut remplacer, fusionner ou classer : la méthode reçoit un `Souvenir` et, s'il s'agit d'un fait sémantique muni d'une clé, cherche un fait actif du même client et de même clé, le déplace dans l'historique, met le nouveau à sa place et renvoie « remplace ». Sinon, elle cherche un souvenir du même client dont le cosinus atteint le seuil de doublon, rafraîchit son heure et garde la plus forte importance, et renvoie « fusionne » ; à défaut, elle ajoute le souvenir et renvoie « ajoute ». Les six écritures de `main` donnent ajoute, ajoute, fusionne, ajoute, ajoute, remplace, et le souvenir de Dubai Marina passe à l'heure 30 en gardant l'importance 0,8.

**`Memoire.rappeler(client, question, heure, k)`** — Cette méthode est la bibliothécaire qui ne sort jamais les dossiers d'un autre client : elle reçoit l'identifiant du client, la question, l'heure courante et un nombre k de souvenirs, 3 par défaut, filtre d'abord les souvenirs actifs de ce seul client, puis note chacun par la somme de trois termes, le cosinus avec la question, la décroissance élevée à la puissance des heures écoulées et l'importance. Elle renvoie les k meilleurs couples (score, texte), du plus fort au plus faible : pour C-17 à l'heure 72, 2,143 pour l'appartement à Dubai Marina, 1,724 pour la préférence pour l'arabe et 1,572 pour la visite à JLT ; pour C-42, seule sa villa remonte.

**`Memoire.effacer(client)`** — C'est le broyeur qui exécute une demande d'effacement sans rien laisser derrière lui : la méthode reçoit l'identifiant d'un client, compte les éléments présents dans les deux registres, retire de la liste `actifs` comme de la liste `historique` tout ce qui appartient à ce client, puis renvoie la différence, c'est-à-dire le nombre d'éléments supprimés. Elle ne lève rien, même pour un client inconnu, qui donne 0. Pour C-17, elle supprime 4 éléments, trois souvenirs actifs et l'ancienne préférence pour l'anglais, après quoi `rappeler` ne renvoie plus rien pour ce client.

**`main()`** — C'est le chef de projet qui fait vivre la mémoire de l'agence en quatre temps : il écrit six souvenirs pour les clients C-17 et C-42, vérifie la suite des opérations, les 4 souvenirs actifs, l'ancien fait gardé dans l'historique et le doublon qui a rafraîchi l'original, puis interroge la mémoire pour C-17 à l'heure 72 et contrôle que l'appartement à Dubai Marina arrive en tête sans qu'aucun souvenir de C-42 ne fuite. Il vérifie ensuite l'isolation dans l'autre sens, C-42 n'obtenant que sa villa, et efface enfin toute la mémoire de C-17, 4 éléments, avant de constater qu'il ne reste que le souvenir de C-42.

```python
"""Étape 15 bis — mémoire longue : écrire, consolider, mettre à jour un fait, rappeler, isoler, effacer."""
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def vecteur(texte: str) -> Counter:
    return Counter(re.findall(r"\w+", texte.lower()))


def cosinus(a: Counter, b: Counter) -> float:
    produit = sum(a[m] * b[m] for m in a.keys() & b.keys())
    na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    return 0.0 if na == 0 or nb == 0 else produit / (na * nb)


@dataclass
class Souvenir:
    client: str
    type: str                 # "episodique", "semantique" ou "procedurale"
    texte: str
    importance: float
    source: str
    heure: float              # heures depuis le début de la relation client
    cle: str | None = None    # pour un fait sémantique qui peut changer


class Memoire:
    def __init__(self, seuil_doublon: float = 0.9, decroissance: float = 0.995):
        self.actifs: list[Souvenir] = []
        self.historique: list[Souvenir] = []
        self.seuil_doublon, self.decroissance = seuil_doublon, decroissance

    def memoriser(self, s: Souvenir) -> str:
        if s.type == "semantique" and s.cle:
            for ancien in self.actifs:
                if ancien.client == s.client and ancien.cle == s.cle:
                    self.actifs.remove(ancien)
                    self.historique.append(ancien)
                    self.actifs.append(s)
                    return "remplace"
        v = vecteur(s.texte)
        for existant in self.actifs:
            if existant.client == s.client and cosinus(v, vecteur(existant.texte)) >= self.seuil_doublon:
                existant.heure = max(existant.heure, s.heure)
                existant.importance = max(existant.importance, s.importance)
                return "fusionne"
        self.actifs.append(s)
        return "ajoute"

    def rappeler(self, client: str, question: str, heure: float, k: int = 3) -> list[tuple[float, str]]:
        q = vecteur(question)
        candidats = [s for s in self.actifs if s.client == client]          # isolation d'abord
        notes = [(cosinus(q, vecteur(s.texte)) + self.decroissance ** (heure - s.heure) + s.importance, s.texte)
                 for s in candidats]
        return sorted(notes, reverse=True)[:k]

    def effacer(self, client: str) -> int:
        avant = len(self.actifs) + len(self.historique)
        self.actifs = [s for s in self.actifs if s.client != client]
        self.historique = [s for s in self.historique if s.client != client]
        return avant - len(self.actifs) - len(self.historique)


def main() -> None:
    m = Memoire()
    print("1. Écrire et consolider")
    etats = [
        m.memoriser(Souvenir("C-17", "semantique", "Le client préfère être contacté en anglais.", 0.6, "chat-01", 0, "langue_contact")),
        m.memoriser(Souvenir("C-17", "episodique", "Le client cherche un appartement de 2 chambres à Dubai Marina.", 0.8, "chat-01", 1)),
        m.memoriser(Souvenir("C-17", "episodique", "Le client cherche un appartement de 2 chambres à Dubai Marina !", 0.7, "chat-02", 30)),
        m.memoriser(Souvenir("C-17", "episodique", "Le client a visité un studio à JLT et l'a refusé, trop bruyant.", 0.5, "visite-03", 50)),
        m.memoriser(Souvenir("C-42", "episodique", "Le client cherche une villa de 4 chambres à Arabian Ranches.", 0.8, "chat-09", 5)),
        m.memoriser(Souvenir("C-17", "semantique", "Le client préfère être contacté en arabe.", 0.6, "chat-04", 70, "langue_contact")),
    ]
    print(f"  opérations : {etats}")
    print(f"  {len(m.actifs)} souvenirs actifs, {len(m.historique)} dans l'historique")
    assert etats == ["ajoute", "ajoute", "fusionne", "ajoute", "ajoute", "remplace"]
    assert len(m.actifs) == 4 and len(m.historique) == 1
    assert m.historique[0].texte.endswith("en anglais.")                  # l'ancien fait est gardé, inactif
    marina = next(s for s in m.actifs if "Marina" in s.texte)
    assert (marina.heure, marina.importance) == (30, 0.8)                 # le doublon a rafraîchi l'original

    print("2. Rappeler, pour C-17, à l'heure 72")
    resultats = m.rappeler("C-17", "Quel appartement à Dubai Marina proposer au client ?", heure=72)
    for score, texte in resultats:
        print(f"  {score:.3f}  {texte}")
    assert "Marina" in resultats[0][1]
    assert all("Arabian Ranches" not in t for _, t in resultats)          # aucune fuite entre clients
    assert round(cosinus(vecteur("a b"), vecteur("a b")), 9) == 1.0 and cosinus(vecteur(""), vecteur("a")) == 0.0

    print("3. Isolation")
    autre = m.rappeler("C-42", "Dubai Marina appartement 2 chambres", heure=72)
    print(f"  C-42 obtient : {[t for _, t in autre]}")
    assert len(autre) == 1 and "villa" in autre[0][1]

    print("4. Effacement à la demande de C-17")
    n = m.effacer("C-17")
    print(f"  {n} éléments supprimés (actifs et historique) ; reste {len(m.actifs)} souvenir(s), tous de C-42")
    assert n == 4 and all(s.client == "C-42" for s in m.actifs + m.historique)
    assert m.rappeler("C-17", "Dubai Marina", heure=80) == []
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Écrire et consolider
  opérations : ['ajoute', 'ajoute', 'fusionne', 'ajoute', 'ajoute', 'remplace']
  4 souvenirs actifs, 1 dans l'historique
2. Rappeler, pour C-17, à l'heure 72
  2.143  Le client cherche un appartement de 2 chambres à Dubai Marina.
  1.724  Le client préfère être contacté en arabe.
  1.572  Le client a visité un studio à JLT et l'a refusé, trop bruyant.
3. Isolation
  C-42 obtient : ['Le client cherche une villa de 4 chambres à Arabian Ranches.']
4. Effacement à la demande de C-17
  4 éléments supprimés (actifs et historique) ; reste 1 souvenir(s), tous de C-42
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : une mémoire d'agent est un petit système de données avec ses règles propres. On écrit avec une politique, on fusionne les doublons, on remplace un fait qui change sans perdre la trace de l'ancien, on filtre par client avant toute recherche, et on sait supprimer réellement.

### Mécanisme du programme, en détail

La mémoire du programme repose sur une représentation très simple des textes : `vecteur` découpe un texte en mots, en minuscules, et compte chaque mot dans un `Counter`, ce qui donne un sac de mots. `cosinus` calcule ensuite le cosinus de deux sacs de mots en ne parcourant que les mots qu'ils ont en commun pour le produit scalaire, et renvoie 0 si l'un des deux textes est vide, pour éviter une division par zéro. Ce n'est pas un embedding sémantique, mais le mécanisme est le même que celui des étapes 14 et 15, et il reste vérifiable à la main.

Chaque `Souvenir` porte son client, son type (épisodique, sémantique ou procédural), son texte, son importance, sa source, l'heure à laquelle il a été écrit et, pour un fait sémantique qui peut changer, une clé. `Memoire.memoriser` applique trois règles dans l'ordre. D'abord, un fait sémantique muni d'une clé remplace l'ancien fait du même client et de même clé : l'ancien n'est pas effacé, il passe dans `historique`, ce qui garde la trace d'une préférence qui a changé. Ensuite, un texte dont le cosinus avec un souvenir existant du même client atteint le seuil de doublon (0,9) n'est pas ajouté : il est fusionné, en rafraîchissant l'heure et l'importance de l'original. Sinon, le souvenir est ajouté.

`rappeler` filtre d'abord les souvenirs du seul client concerné, avant tout calcul : c'est l'isolation, qui garantit qu'une question d'un client ne peut pas faire remonter le souvenir d'un autre. Elle note ensuite chaque candidat par la somme de trois termes, le cosinus avec la question, un facteur de récence 0,995 puissance l'âge en heures et l'importance, puis trie et garde les k meilleurs. `effacer` retire d'un coup tous les souvenirs actifs et tout l'historique d'un client, et renvoie le nombre d'éléments supprimés : c'est la réponse à une demande d'effacement, que le simple oubli par décroissance ne satisfait pas.

## Squelette algorithmique

Les quatre opérations de la mémoire longue (écrire, consolider, rappeler, effacer) se résument en deux algorithmes, l'écriture et le rappel, plus un effacement par filtre.

```text
ALGORITHME Mémoriser
ENTRÉES : souvenir s (client, type, texte, importance, heure, clé éventuelle)
SORTIE  : « remplace », « fusionne » ou « ajoute »

  SI s est sémantique ET s a une clé ALORS
      SI un souvenir actif a le même client et la même clé ALORS
          déplacer l'ancien vers l'historique ; ajouter s aux actifs ; RETOURNER « remplace »
  FIN SI
  v ← SacDeMots(s.texte)
  POUR CHAQUE souvenir actif e du même client FAIRE
      SI Cosinus(v, SacDeMots(e.texte)) ≥ seuil ALORS
          e.heure ← max(e.heure, s.heure) ; e.importance ← max(e.importance, s.importance)
          RETOURNER « fusionne »
  FIN POUR
  ajouter s aux actifs ; RETOURNER « ajoute »

ALGORITHME Rappeler
ENTRÉES : client, question, heure, k
  candidats ← souvenirs actifs de ce client SEULEMENT          (isolation avant tout calcul)
  POUR CHAQUE candidat c FAIRE
      note ← Cosinus(question, c.texte) + δ^(heure − c.heure) + c.importance
  FIN POUR
  RETOURNER les k meilleures notes

ALGORITHME Effacer(client)
  retirer de l'actif et de l'historique tout souvenir de ce client ; RETOURNER le nombre retiré
```

**Complexité.** Écrire coûte O(a × L) pour a souvenirs actifs de longueur L, à cause de la recherche de doublon qui compare le nouveau texte à chaque souvenir du client. Rappeler coûte O(a × L) pour les notes et O(a log a) pour le tri. Effacer est une passe O(a + h) sur les actifs et l'historique. En production, la recherche de doublon et le rappel passent par un index vectoriel pour éviter ce parcours linéaire.

**Du squelette au code.** `SacDeMots` correspond à `vecteur`, `Cosinus` à `cosinus`, `Mémoriser` à `Memoire.memoriser`, `Rappeler` à `Memoire.rappeler` (avec `decroissance` = δ = 0,995) et `Effacer` à `Memoire.effacer`. Le programme vérifie les trois issues de l'écriture, l'absence de fuite entre clients et l'effacement complet.

## Cas d'usage réels aux Émirats

Les règles citées sont à confirmer avec le texte en vigueur avant mise en production.

### Immobilier — suivi d'un acheteur sur plusieurs mois

L'agent d'une agence de Dubaï suit un acheteur pendant six mois : budget, quartiers visités, refus motivés. Les visites sont des souvenirs épisodiques ; le budget et la langue de contact sont des faits sémantiques avec une clé, que chaque nouvelle déclaration remplace. Quand l'acheteur relève son budget, l'ancien reste dans l'historique : le conseiller voit l'évolution, mais l'agent ne propose plus de biens au-dessous du nouveau budget.

### Banque — données personnelles et effacement

Une banque soumet la mémoire de son agent client aux règles de protection des données (loi fédérale sur la protection des données personnelles, décret-loi 45/2021, et pour une entité du DIFC la loi de protection des données du DIFC). Chaque souvenir garde sa source, et l'opération `effacer(client)` supprime aussi l'historique et les index : une décroissance du score n'est pas un effacement. Les souvenirs de type procédural (« ce client exige un rappel avant tout virement ») sont validés par un conseiller avant d'entrer en service.

### Assurance — isolation entre assurés d'une même famille

Un assureur santé gère des polices familiales : le titulaire et ses ayants droit discutent avec le même agent. La mémoire est isolée par **assuré**, pas par police : l'agent ne rappelle jamais à un enfant majeur un souvenir médical de son parent. Le filtre de propriétaire est appliqué dans la requête de base de données, avant la recherche par similarité, et un test automatique vérifie qu'aucune requête ne renvoie de souvenir d'un autre assuré.

## Pièges et limites

- **Tout mémoriser.** La mémoire se remplit de bruit et la récupération devient mauvaise. Une politique d'écriture explicite vaut mieux qu'un stockage systématique.
- **Filtrer par pertinence avant le propriétaire.** Un seuil de similarité ne protège pas une donnée ; un filtre de propriétaire, si.
- **Confondre décroissance et suppression.** Un souvenir qui pèse presque zéro existe encore, dans la base et dans les sauvegardes.
- **Laisser le modèle écrire des procédures sans relecture.** Une instruction mal retenue (« ne pas vérifier le bon de commande pour ce client ») devient une faille permanente.
- **Résumer un souvenir en effaçant son incertitude.** « Le client a peut-être déménagé » ne doit pas devenir « le client a déménagé ».

### Exercice feuille blanche

1. Réécrire `memoriser` avec ses trois issues (`remplace`, `fusionne`, `ajoute`) et la tester sur deux déclarations successives de budget.
2. Ajouter un champ `expire_a` aux souvenirs et faire ignorer par `rappeler` les souvenirs expirés.
3. Trouver le bug : dans une variante, `rappeler` trie tous les souvenirs par score puis filtre par client après le `[:k]`. Que se passe-t-il quand un autre client a des souvenirs plus pertinents ? (Réponse : le client reçoit moins de `k` souvenirs, voire aucun, alors qu'il en a de pertinents ; et si le filtre est oublié, il reçoit ceux d'un autre client.)

## Pour aller plus loin

- La décroissance

$$
\delta^{\Delta t}
$$

et sa demi-vie : [étape 16](<16-Memoire-Formule-Decroissance-Temporelle.md>).
- Le score qui pondère pertinence, récence et importance : [étape 17](<17-Memoire-Formule-Score-de-Pertinence.md>).
- La place que ces souvenirs peuvent occuper dans le contexte : [étape 13 ter](<13c-Contexte-Definitions-Fondamentaux.md>).

> Suite : [Décroissance d'un souvenir](<16-Memoire-Formule-Decroissance-Temporelle.md>) — étape 16.
