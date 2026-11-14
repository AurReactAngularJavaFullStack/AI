# Étape 9 — Assembler, tester, lancer la démo

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 8 — L'outil de virement](<08-Outil-de-virement.md>) · Palier suivant : [Palier 10 — Évaluation](<../../../10-Evaluation/README.md>)

## Comment raisonner

Chaque fonction a passé ses tests isolément. Il reste à vérifier que le module entier tient avec les huit paliers précédents, puis à lire la démo comme on lirait un journal de production : chaque ligne doit s'expliquer par une des étapes 1 à 8.

## Le module complet, dans l'ordre

Le fichier `agent/garde_fous.py` se lit de haut en bas dans l'ordre où l'on a raisonné :

1. les imports, dont trois viennent des paliers antérieurs : `iban_ae_valide` et `emirates_id_format_valide` (03), `Horloge` (01), `ErreurOutil`, `RefusPolitique` et `Registre` (04), `objet` (02) ;
2. `LECTURE`, `POLITIQUE` et `autoriser` (étape 1) ;
3. `masquer` (étape 2) ;
4. `GENESE` et `JournalAudit` (étape 3) ;
5. les constantes du risque, `gravite` et `score_risque` (étape 4), puis `veto` et `decider` (étape 5) ;
6. `Approbateur` (étape 6) ;
7. `proteger` (étape 7) ;
8. `SCHEMA_VIREMENT` et `enregistrer_virement` (étape 8).

Aucun module antérieur n'a été modifié : `proteger` enveloppe la porte du palier 04, et `enregistrer_virement` utilise son décorateur. Voici comment `demo.py` assemble le monde :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`main()`** — Dans cet extrait, la fonction principale de la démonstration joue le régisseur qui monte le décor avant le lever du rideau. Elle ne reçoit rien ; elle règle une horloge simulée sur le jour 90 de la relation client, soit 90 × 86 400 secondes, crée un seul journal et un seul approbateur qui partagent cette horloge, ouvre une liste de virements vide, enregistre les outils métier puis l'outil de virement dans un registre neuf, et prépare une session `client_banque` dotée des portées `lecture` et `virement:initier`. Elle termine l'assemblage en confiant le tout à `proteger`, dont le dictionnaire `outils` sera ensuite passé à la boucle d'agent ; la suite de la fonction, en pointillés, déroule les scènes dont la sortie attendue est imprimée plus bas, et elle ne rend rien.

```python
# [extrait] demo.py
def main() -> None:
    ...
    horloge = Horloge(90 * 86_400.0)
    journal = JournalAudit(horloge)
    approbateur, virements = Approbateur(horloge, journal), []
    registre = enregistrer_outils_metier(Registre())
    enregistrer_virement(registre, approbateur, journal, virements)
    session = {"role": "client_banque", "portees": {"lecture", "virement:initier"}}
    outils = proteger(registre, session, journal)
```

L'horloge démarre au jour 90 de la relation client (90 × 86 400 s), comme dans l'étape 77. Une seule horloge et un seul journal sont partagés par tous les composants : l'approbateur avance l'horloge que le journal lit pour dater ses entrées. La session est un dictionnaire gardé par la démo, qui pourra changer le rôle plus loin. Le dictionnaire `outils` se passe ensuite à `executer_agent` (palier 05) à la place de `registre.appelables()`, et la boucle ne voit aucune différence : elle appelle des fonctions par leur nom.

## Toute la suite de tests

Depuis `projet/` :

```text
python -m unittest -v
```

La dernière ligne doit être `OK`, après `Ran 122 tests` : les 107 tests des paliers 01 à 08, qui passaient déjà, et les 15 du palier 09. Si un test d'un palier antérieur casse, c'est qu'un module antérieur a été modifié par erreur : il faut le restaurer, pas l'adapter.

## La démo

```text
python demo.py
```

Sortie attendue, identique à celle de l'énoncé :

```text
Palier 09 — acompte off-plan du client C-7 : un courriel « du promoteur » demande 180 000 AED
  journal : question : Payez l'acompte. Emirates ID [EMIRATES_ID ••••5671], tél. [TEL ••••4567]. <document source="COURRIE
  journal : politique client_banque -> initier_virement : autorisé
  journal : risque virement [IBAN ••••3456] de 180000 AED : R = 0.70, veto, décision revue
  journal : approbation : virement de 180000 AED vers [IBAN ••••3456] -> refus par délai
  [fini] outil : ERREUR refusé par l'humain : pas de réponse en 120 s : refus par défaut
  horloge +120 s ; virements exécutés : 0 ; chaîne intacte : True
Risque : R = 0.46 → autoriser sans veto, revue avec ; R = 0.88 → bloquer
Loyer de 2 500 AED approuvé en 45 s : {'statut': 'exécuté', 'montant_aed': 2500}
Rôle assistant_public : RefusPolitique (outil initier_virement non autorisé pour le rôle assistant_public)
Journal falsifié à l'entrée 1 : verifier() = 1
OK — palier 09 terminé.
```

**Ligne par ligne, ce qui a produit quoi.**

- **Journal, ligne 1.** La démo journalise la question construite par `construire_prompt` (palier 01) : l'Emirates ID et le téléphone sont masqués par `masquer` (étape 2) avant l'écriture ; la balise du courriel est déjà neutralisée en `&lt;` plus loin dans le texte, tronqué ici à 110 caractères.
- **Ligne 2.** `proteger` (étape 7) : le rôle `client_banque` a la portée `virement:initier`, la politique accorde, et la décision est écrite.
- **Ligne 3.** `enregistrer_virement` (étape 8) : R = 0,70, veto, « revue ». L'IBAN est masqué.
- **Ligne 4.** `Approbateur.demander` (étape 6) : la file est vide, refus par délai.
- **`[fini] outil : ERREUR …`.** L'outil a levé `ErreurOutil` ; la boucle l'a renvoyée au modèle, qui a répondu, d'où le statut `fini`.
- **`horloge +120 s`.** C'est le « +120 s » de l'étape 77 : l'attente de l'approbateur, sur l'horloge simulée. Aucun virement n'est parti, et `verifier()` confirme que la chaîne est intacte.
- **`Risque`.** Le retrait de 0,46 que seul le veto envoie en revue, et le signal d'injection à 0,88 qui bloque (étape 5).
- **`Loyer`.** Un virement de 2 500 AED, irréversible donc en revue, approuvé en 45 s : le garde-fou exige un humain, il n'empêche pas le métier.
- **`Rôle assistant_public`.** Le rôle change dans la session, et le même objet `outils` refuse aussitôt : la session est relue à chaque appel.
- **`Journal falsifié`.** La démo réécrit le texte de l'entrée 1 (« autorisé » devient « refusé ») ; `verifier()` désigne exactement l'entrée 1.

## Ce qu'il faut retenir

- Un garde-fou est du **code hors du modèle**, qui tient même si le modèle a été entièrement convaincu : la politique, le veto et l'approbation ne lisent jamais ce que le modèle écrit pour décider.
- **Refus par défaut** : seule une ligne explicite de la table autorise ; un rôle, un outil ou une portée absents refusent, chacun avec son motif.
- **Masquer avant d'écrire**, dans la méthode d'écriture elle-même ; chaîner par SHA-256 et **recalculer** pour vérifier.
- **Deux seuils et un veto** : la moyenne pondérée compense, le veto ne compense pas ; on teste la zone la plus grave d'abord.
- **Le silence vaut refus**, et l'approbation est **dans l'outil**, juste avant la seule ligne qui modifie le monde.
- **Composer, pas réécrire** : `proteger` enveloppe la porte du palier 04 avec une fonction fabrique, et relit la session à chaque appel.

## Et ensuite

L'agent sait maintenant refuser. Il ne sait pas encore **se mesurer** : quelle part des dossiers de crédit traite-t-il correctement, appelle-t-il les bons outils, invente-t-il des chiffres ? C'est l'objet du [Palier 10 — Évaluation](<../../../10-Evaluation/README.md>), qui construit l'intervalle de Wilson, la Tool Call F1, la fidélité approchée et la barrière d'intégration continue qui bloque une version moins bonne avant qu'elle parte en production.
