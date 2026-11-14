# Étape 8 — Assemblage et vérification

> Palier 02, étape 8 sur 8 · Précédent : [Étape 7 — Les probabilités de la réparation](<07-Probabilites-de-reparation.md>) · Suivant : [Palier 03 — Outils métier EAU](<../../../03-Outils-Metier-EAU/README.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** relire le module complet dans l'ordre, lancer les 32 tests et la démo, comprendre chaque ligne affichée, puis passer au palier 03.

## Comment raisonner

Le module a été écrit morceau par morceau, et `validate` a même été construite en trois passes. L'assemblage vérifie que les morceaux tiennent ensemble : que le fichier se lit de haut en bas, que les tests du palier 01 passent toujours (le module `modele.py` n'a pas été touché, et `reparer` s'appuie sur lui), et que la démo affiche exactement la sortie attendue.

## Le module dans l'ordre

```python
# [extrait] agent/schemas.py
"""Palier 02 — schémas et validation : refuser des arguments mal formés avant tout effet.

Origine : étape 77, section 3 (validateur minimal : mêmes chemins JSON, mêmes messages, onze mots-clés),
et étape 8 (boucle de réparation, probabilité de succès après relances).

Trois pièces :
- `validate` rend la liste des écarts entre une instance et un schéma, avec leurs chemins JSON ;
- `schema_pour_api_strict` prépare le schéma envoyé à l'API en mode strict, qui refuse les bornes ;
- `reparer` renvoie les erreurs au modèle et lui redemande un JSON, au plus `max_essais` fois.
"""
import json
import math
import re
```

Après la docstring et les imports, le fichier suit l'ordre de la progression :

```text
agent/schemas.py
  imports ; MOTS_CLES, TYPES, NOMS_JSON                           étape 1
  validate        mot-clé inconnu, type                           étape 1
                  nombres, chaînes                                étape 2
                  objets, récursion                               étape 3
  objet                                                           étape 3
  NON_STRICT, schema_pour_api_strict                              étape 4
  MOTIF_EMIRATES_ID, SCHEMA_DEMANDE_CREDIT                        étape 3
  lire_et_valider                                                 étape 5
  reparer                                                         étape 6
  p_succes, essais_moyens                                         étape 7
```

Deux remarques sur l'ordre. `SCHEMA_DEMANDE_CREDIT` utilise `MOTIF_EMIRATES_ID` au moment où le dictionnaire est construit, à l'import du module : le motif doit donc être défini juste au-dessus. `reparer` appelle `lire_et_valider`, qui appelle `validate` : en Python, une fonction peut en appeler une autre définie plus bas, car le nom n'est cherché qu'à l'exécution ; mais l'ordre « du plus simple au plus composé » rend la lecture plus facile.

Le module n'importe rien du palier 01 : `reparer` reçoit le modèle en paramètre (`llm`) et ne connaît que sa méthode `create`. C'est le port de l'architecture hexagonale : `schemas.py` fonctionnera tel quel avec `ClaudeLLM` au palier 12. Seuls les tests et la démo importent `FakeLLM`.

## Lancer toute la suite

Depuis `projet/` :

```powershell
python -m unittest -v
```

Sortie attendue, à la durée près (les 17 lignes du palier 01 viennent d'abord, puis celles du palier 02) :

```text
(17 lignes « ... ok » de tests.test_01_modele)
test_echec_apres_max_essais (tests.test_02_schemas.TestReparation.test_echec_apres_max_essais) ... ok
test_json_dans_un_bloc_de_code (tests.test_02_schemas.TestReparation.test_json_dans_un_bloc_de_code) ... ok
test_probabilites (tests.test_02_schemas.TestReparation.test_probabilites) ... ok
test_refus_traite_avant_le_contenu (tests.test_02_schemas.TestReparation.test_refus_traite_avant_le_contenu) ... ok
test_une_relance_suffit (tests.test_02_schemas.TestReparation.test_une_relance_suffit) ... ok
test_bornes_retirees_et_recopiees (tests.test_02_schemas.TestSchemaStrict.test_bornes_retirees_et_recopiees) ... ok
test_la_validation_locale_reste_necessaire (tests.test_02_schemas.TestSchemaStrict.test_la_validation_locale_reste_necessaire) ... ok
test_objet (tests.test_02_schemas.TestSchemaStrict.test_objet) ... ok
test_bornes_numeriques (tests.test_02_schemas.TestValidateContraintes.test_bornes_numeriques) ... ok
test_chaines (tests.test_02_schemas.TestValidateContraintes.test_chaines) ... ok
test_objet_champs_absents_et_non_prevus (tests.test_02_schemas.TestValidateContraintes.test_objet_champs_absents_et_non_prevus) ... ok
test_booleen_n_est_pas_un_entier (tests.test_02_schemas.TestValidateTypes.test_booleen_n_est_pas_un_entier) ... ok
test_decimal_refuse_comme_entier_et_nan_refuse (tests.test_02_schemas.TestValidateTypes.test_decimal_refuse_comme_entier_et_nan_refuse) ... ok
test_mot_cle_inconnu_refuse (tests.test_02_schemas.TestValidateTypes.test_mot_cle_inconnu_refuse) ... ok
test_type_faux_avec_chemin (tests.test_02_schemas.TestValidateTypes.test_type_faux_avec_chemin) ... ok

----------------------------------------------------------------------
Ran 32 tests in 0.011s

OK
```

Si un test du palier 01 échoue, ce n'est pas ton code : vérifie que tu n'as pas modifié `agent/modele.py`.

## Lancer la démo

```powershell
python demo.py
```

```text
Palier 02 — demande de prêt personnel du client C-2 (150 000 AED sur 36 mois)
1. Demande mal formée, erreurs avec leur chemin JSON :
   $ : champ obligatoire absent « emirates_id »
   $.montant_aed : 0 doit être > 0
   $.duree_mois : type attendu integer, reçu string
   $.revenu_mensuel_aed : type attendu number, reçu boolean
   $ : champ non prévu « commentaire »
   demande correcte : []
2. Schéma strict pour l'API, duree_mois : {'type': 'integer', 'description': 'Contraintes : minimum=12, maximum=300.'}
   6 mois passe le schéma strict : True ; le schéma local le refuse : ['$.duree_mois : 6 < minimum 12']
3. Réparation : essai 1 → ['$.duree_mois : type attendu integer, reçu string']
   statut valide en 2 essais, 2 appels au modèle
4. Trois essais ratés : statut echec → le dossier part en revue humaine
   un refus s'arrête au premier essai : statut refusal, essais 1
5. p = 0.9 par essai, 2 relances : succès 0.999, 1.11 appels en moyenne
OK — palier 02 terminé.
```

**Chaque ligne, d'où elle vient.**

- **Bloc 1.** La demande mal formée est `{"montant_aed": 0, "duree_mois": "36", "revenu_mensuel_aed": True, "commentaire": "urgent"}`. `validate` traite d'abord `required` : seul `emirates_id` manque. Puis les champs dans l'ordre de l'instance : 0 n'est pas strictement positif (`exclusiveMinimum`), `"36"` est une chaîne et non un entier, `True` est un booléen et non un nombre (le piège de l'étape 1), et `commentaire` n'est pas prévu. Cinq erreurs, toutes trouvées en un seul appel : une seule relance pourrait les corriger toutes. La demande correcte donne la liste vide.
- **Bloc 2.** Le schéma strict de `duree_mois` a perdu ses bornes, recopiées dans la description (étape 4). Une demande de 6 mois passe donc le schéma strict, et seule la validation locale la refuse.
- **Bloc 3.** Le scénario de l'étape 6 : le premier essai a une erreur, la durée en chaîne ; le second est valide. Deux essais, deux appels au faux modèle.
- **Bloc 4.** Trois réponses avec un montant nul : trois essais ratés, statut `echec`, et le dossier part chez un humain. Un refus arrête la boucle dès le premier essai, sans lire le contenu.
- **Bloc 5.** Les formules de l'étape 7 : 1 − 0,1³ = 0,999 et 1 + 0,1 + 0,01 = 1,11.

## Ce que tu as appris

- **Valider, c'est lister.** `validate` rend toutes les erreurs d'un coup, chacune avec son chemin JSON, pour que le modèle sache exactement quoi corriger.
- **Les pièges de Python.** Un booléen est un `int`, NaN passe toutes les comparaisons, `json.loads` accepte `NaN`, `$` accepte un saut de ligne final : chacun a sa ligne de défense.
- **La récursion** applique à chaque champ tout ce qui a été écrit pour un nombre ou une chaîne, avec un chemin prolongé.
- **Le mode strict de l'API** garantit la forme, pas les bornes : on prépare une copie sans bornes pour l'API, et la validation locale reste obligatoire.
- **La boucle de réparation** est bornée, lit le `stop_reason` avant le contenu, renvoie au modèle sa réponse fautive et ses erreurs, et rend toujours un résultat de la même forme.
- **Deux relances suffisent** quand un essai réussit 9 fois sur 10 : 99,9 % de succès pour 1,11 appel en moyenne, sous l'hypothèse d'indépendance.

## La suite

L'agent sait maintenant parler au modèle et vérifier la forme de ce qu'il rend. Il ne sait encore rien calculer. Au palier 03, tu écris `agent/metier.py` : les calculs métier des Émirats que le modèle n'a pas le droit de faire de tête (mensualité d'un prêt, ratio d'endettement sous le plafond de 50 % de la CBUAE, indemnité de fin de service, TVA de 5 %, conversion AED et USD à 3,6725, contrôle d'un IBAN et d'un Emirates ID). Au palier 04, chacun deviendra un outil dont la porte appellera `validate` avant toute exécution.

> Suivant : [Palier 03 — Outils métier EAU](<../../../03-Outils-Metier-EAU/README.md>) · [Retour à l'énoncé du palier 02](<../../README.md>)
