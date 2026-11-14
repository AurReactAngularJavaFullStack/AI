# Étape 8 — L'outil de virement

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 7 — La porte protégée](<07-Porte-protegee.md>) · Suivant : [Étape 9 — Assembler, tester, lancer la démo](<09-Assembler-tester-lancer.md>)

## Comment raisonner

Toutes les pièces existent : contrôle d'IBAN (palier 03), registre (palier 04), score, veto et décision (étapes 4 et 5), approbateur (étape 6), journal (étape 3). Il reste à écrire **le seul outil qui modifie le monde** : un virement, irréversible. Une règle commande tout le reste : **la ligne qui produit l'effet est la dernière**. Avant elle, chaque contrôle qui échoue lève une exception ; après elle, plus rien ne peut échouer. Si cette ligne venait plus tôt, une exception levée ensuite ne défairait rien : on ne rappelle pas un virement parti.

Deuxième décision : l'approbation se demande **dans l'outil**, à chaque appel, et non dans la boucle ou dans le prompt. Ainsi, aucun ordre d'appel, aucune répétition, aucun texte injecté ne peut la contourner : le chemin vers `virements.append` passe forcément par elle.

## Le contrat de l'outil

```python
# [extrait] agent/garde_fous.py
SCHEMA_VIREMENT = objet({
    "iban": {"type": "string", "pattern": "^AE[0-9]{2}( ?[0-9]){19}$"},
    "montant_aed": {"type": "number", "exclusiveMinimum": 0},
    "motif": {"type": "string", "minLength": 1, "maxLength": 140}})
```

`objet` (palier 02) fabrique un schéma où les trois champs sont obligatoires et où tout champ non prévu est refusé. Le motif d'IBAN vérifie le **format** (AE, deux chiffres, dix-neuf chiffres avec espaces facultatives), pas la clé : la clé mod 97 est un calcul que le validateur ne sait pas faire, il est donc dans l'outil. Le montant doit être strictement positif, le motif tenir en 140 caractères.

## Un brouillon où l'effet vient trop tôt

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`outil_virement(iban, montant_aed, motif)`** — Ce brouillon se conduit comme un caissier qui remet d'abord les billets au client et ne consulte qu'ensuite la liste des chèques volés. Il reçoit l'IBAN, le montant et le motif, ajoute aussitôt le virement à la liste globale `virements`, puis seulement calcule R avec la sensibilité personnelle, la gravité de l'irréversible et la constante `INCERTITUDE_MODELE`, et lève `ErreurOutil("bloqué")` si la décision vaut « bloquer ». Dans tous les autres cas il rend `{"statut": "exécuté", …}` : la revue humaine et le contrôle mod 97 manquent, et même quand il lève l'exception, le virement est déjà inscrit et ne peut plus être rappelé.

```python
# [extrait] brouillon
def outil_virement(iban, montant_aed, motif):
    virements.append({"iban": iban, "montant_aed": montant_aed, "motif": motif})     # l'effet d'abord : erreur
    r = score_risque(SENSIBILITE["personnelle"], gravite("irreversible", montant_aed), INCERTITUDE_MODELE)
    if decider(r, veto("irreversible", montant_aed)) == "bloquer":
        raise ErreurOutil("bloqué")
    return {"statut": "exécuté", "montant_aed": montant_aed}
```

Le virement est ajouté avant tout contrôle : même « bloqué », il est parti. Ce brouillon oublie aussi le contrôle mod 97 et la revue humaine, et il lit l'incertitude dans une constante globale au lieu du paramètre, si bien qu'un test ne pourrait pas simuler un signal d'injection.

## L'outil, garde-fou compris

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`enregistrer_virement(registre, approbateur, journal, virements, incertitude)`** — Cette fonction est l'artisan qui fabrique un coffre-fort sur mesure pour un monde donné, puis le scelle dans le mur du registre. Elle reçoit le registre du palier 04, l'approbateur, le journal, la liste des virements de ce monde et l'incertitude du modèle, 0,1 par défaut ; elle définit l'outil interne et le range, grâce au décorateur `@registre.outil`, sous le nom `"initier_virement"` avec sa description « Action IRRÉVERSIBLE » et `SCHEMA_VIREMENT`. Elle rend le registre lui-même, pour qu'on puisse enchaîner les enregistrements, et chaque monde de test obtient ainsi son propre outil branché sur ses propres objets, sans aucune variable globale.

**`outil_virement(iban, montant_aed, motif)`** — Cette fonction interne, qui vit dans `enregistrer_virement` et en capture les objets, est le coffre lui-même, avec ses serrures franchies l'une après l'autre. Elle reçoit l'IBAN, le montant et le motif déjà validés par le schéma, lève `ValueError` si la clé mod 97 est fausse, calcule R avec la sensibilité 0,7, la gravité de l'irréversible et l'incertitude du monde, en déduit la décision, puis journalise la ligne de risque où l'IBAN sera masqué. Si la décision est « bloquer », elle lève `ErreurOutil` sans déranger l'humain ; si elle est « revue », elle interroge l'approbateur et lève `ErreurOutil` s'il n'approuve pas ; ce n'est qu'en tout dernier qu'elle ajoute le virement à `virements` et rend `{"statut": "exécuté", "montant_aed": …}`. Pour l'acompte de 180 000 AED, R = 0,70, la revue reste sans réponse et rien ne part.

```python
# [extrait] agent/garde_fous.py
def enregistrer_virement(registre: Registre, approbateur: Approbateur, journal: JournalAudit, virements: list,
                         incertitude: float = INCERTITUDE_MODELE) -> Registre:
    ...
    @registre.outil("initier_virement", "Virement sortant en AED vers un IBAN émirien. Action IRRÉVERSIBLE.",
                    SCHEMA_VIREMENT)
    def outil_virement(iban: str, montant_aed: float, motif: str) -> dict:
        if not iban_ae_valide(iban):
            raise ValueError("IBAN AE invalide (contrôle mod 97)")
        r = score_risque(SENSIBILITE["personnelle"], gravite("irreversible", montant_aed), incertitude)
        decision = decider(r, veto("irreversible", montant_aed))
        journal.journaliser(f"risque virement {iban} de {montant_aed} AED : R = {r:.2f}, veto, décision {decision}")
        if decision == "bloquer":
            raise ErreurOutil(f"bloqué par le garde-fou : R = {r:.2f} >= {TAU_BLOCAGE}")
        if decision == "revue":                # l'approbation est DANS l'outil, à chaque appel
            ok, motif_humain = approbateur.demander(f"virement de {montant_aed} AED vers {iban}")
            if not ok:
                raise ErreurOutil(f"refusé par l'humain : {motif_humain}")
        virements.append({"iban": iban, "montant_aed": montant_aed, "motif": motif})
        return {"statut": "exécuté", "montant_aed": montant_aed}

    return registre
```

**L'enregistrement.** `@registre.outil(nom, description, schéma)` est le décorateur du palier 04 : appliqué à `outil_virement`, il range la fonction dans le registre sous le nom `"initier_virement"`, avec son contrat. Comme `outil_virement` est définie **dans** `enregistrer_virement`, elle capture `approbateur`, `journal`, `virements` et `incertitude` : chaque monde a son propre outil, branché sur ses propres objets, là où l'étape 77 utilisait les globales `APPROBATEUR` et `VIREMENTS`. La description dit au modèle que l'action est irréversible, mais la sécurité ne repose pas sur cette phrase.

**Le corps, ligne par ligne.**

- Le contrôle mod 97 d'abord : un IBAN mal formé ne mérite même pas un calcul de risque. C'est une `ValueError`, une erreur d'argument, que la boucle renverra au modèle pour qu'il corrige.
- R se calcule avec la sensibilité « personnelle » (0,7 : un compte bancaire), la gravité de l'irréversible et l'incertitude passée en paramètre. Pour 180 000 AED : 0,28 + 0,40 + 0,02 = 0,70.
- La décision combine R et le veto. Pour un virement, le veto est toujours vrai, d'où le mot « veto » écrit en dur dans la ligne de journal.
- Le journal reçoit le risque **avant** l'action, avec l'IBAN en clair dans la chaîne passée, que `journaliser` masque : on lit « [IBAN ••••3456] » dans le journal.
- « bloquer » lève `ErreurOutil` sans solliciter l'humain : inutile de déranger un conseiller pour une action déjà interdite. `{TAU_BLOCAGE}` s'affiche « 0.75 ».
- « revue » demande l'humain ; s'il n'approuve pas, ou ne répond pas à temps, `ErreurOutil` avec son motif.
- La dernière ligne qui touche au monde, `virements.append(…)`, n'est atteinte que si la décision était « autoriser », ou « revue » suivie d'une approbation explicite.
- `return registre` permet d'enchaîner, comme `enregistrer_outils_metier` au palier 04.

**Analogie Java.** On enregistre un bean fonctionnel dans un registre : `registre.put("initier_virement", new Outil(description, schema, args -> service.virer(args)))`, où le service reçoit ses dépendances par injection. La règle « l'effet en dernier » est celle de toute méthode qui appelle un système externe non transactionnel : `@Transactional` ne rattrape pas un virement SWIFT déjà émis.

**Le piège classique.** Mettre l'approbation dans la boucle d'agent, par exemple « si le modèle demande `initier_virement`, demander à l'humain avant d'exécuter ». Un autre outil, ajouté plus tard, qui appellerait le virement en interne, ou un chemin de code qui n'utilise pas cette boucle, passerait sans approbation. Dans l'outil, le contrôle est sur le seul chemin qui mène à l'effet.

## Ce que fait la boucle d'une erreur

L'outil lève des exceptions, mais la boucle ne plante pas. `executer_appel` (palier 04) les attrape, rend un `tool_result` marqué `is_error` et une ligne de trace « ERREUR … », que le modèle lit à l'étape suivante. C'est ce que vérifie le dernier test : le faux modèle demande un virement vers l'IBAN à clé 08, le schéma l'accepte, l'outil le refuse, et la trace contient « ERREUR IBAN AE invalide (contrôle mod 97) » ; le modèle répond ensuite, la boucle finit avec le statut `fini`, et `virements` reste vide.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_09_garde_fous.TestPorteProtegeeEtVirement
```

Les quatre tests passent, y compris celui de l'étape 7 :

- `test_politique_avant_le_schema` : le rôle `assistant_public` est refusé avant tout examen des arguments, et le journal n'a qu'une ligne ;
- `test_virement_de_180000_refuse_sans_humain` : R = 0,70, revue, pas de réponse, `ErreurOutil("refusé par l'humain : pas de réponse en 120 s : refus par défaut")`, aucun virement, et la ligne de risque masquée dans le journal ;
- `test_virement_approuve_puis_injection_bloquee` : un loyer de 2 500 AED approuvé en 45 s est exécuté ; avec `incertitude=1.0`, R monte à 0,88 et l'outil bloque, l'horloge restant au jour 90 parce que l'humain n'a pas été sollicité ;
- `test_dans_la_boucle_l_erreur_repart_vers_le_modele` : l'erreur d'IBAN repart vers le modèle par la boucle du palier 05.
