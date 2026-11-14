# Étape 16 — Mémoire — Décroissance temporelle (Memory Decay)

> Étape 16 du parcours · Prérequis : [La mémoire d'un agent : définitions](<15b-Memoire-Definitions-Fondamentaux.md>) · Suite : [Score de pertinence d'un souvenir](<17-Memoire-Formule-Score-de-Pertinence.md>)

**Dossier :** 04-Contexte-Similarite-et-Memoire  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 16-Memoire-Formule-Decroissance-Temporelle.md

## Définition

Une fonction de décroissance réduit le poids d'un souvenir à mesure que le temps passe depuis sa dernière utilisation. Elle ne supprime rien : elle attribue à chaque souvenir un **score de récence** que l'agent utilise ensuite pour classer, filtrer ou archiver sa mémoire. Deux formes sont courantes. La forme **exponentielle** fait perdre au souvenir la même *fraction* de sa valeur à chaque unité de temps : la perte est donc rapide au début, puis de plus en plus lente, et le score n'atteint jamais zéro. La forme **linéaire** fait perdre la même *quantité* à chaque unité de temps et atteint zéro à une date fixe, ce qui en fait un mécanisme d'expiration.

## Rôle dans un agent

À chaque tour, l'agent perçoit une question, puis va chercher dans sa mémoire à long terme les souvenirs qui pourraient l'aider. Avant de décider quoi injecter dans le prompt, il note chaque souvenir candidat : la similarité avec la question (étape 14), l'importance du souvenir, et sa récence, calculée par cette formule. L'étape 17 combine ces trois signaux en un seul score. La récence sert aussi en dehors du classement : un souvenir dont le score passe sous un seuil peut être résumé, archivé ou supprimé, ce qui garde la mémoire petite et le prompt bon marché.

## Équation complète

Décroissance exponentielle :

$$
S(t) = S_0 \, e^{-\lambda t}
$$

Décroissance linéaire :

$$
S(t) = S_0 \, \max(0,\; 1 - \kappa t)
$$

Forme discrète (le temps compte des pas : heures, échanges) :

$$
S(t) = S_0 \, q^{t} \qquad \text{avec} \qquad q = e^{-\lambda}
$$

Demi-vie de la forme exponentielle :

$$
t_{1/2} = \frac{\ln 2}{\lambda}
$$

## Décryptage des symboles

$$
S_0
$$

**Sens :** importance initiale du souvenir, au moment où il est écrit ou relu · **Type / plage :** réel ≥ 0, souvent dans [0, 1] · **Variable Python :** `score0`

$$
t
$$

**Sens :** temps écoulé depuis le dernier accès (jours, heures ou nombre d'échanges) · **Type / plage :** réel ≥ 0 · **Variable Python :** `t`

$$
S(t)
$$

**Sens :** score de récence au temps t · **Type / plage :** réel entre 0 et S₀ · **Variable Python :** valeur renvoyée

$$
\lambda
$$

**Sens :** taux de décroissance exponentielle, dans l'unité inverse de t · **Type / plage :** réel > 0 · **Variable Python :** `lam`

$$
\kappa
$$

**Sens :** pente de la décroissance linéaire (fraction de S₀ perdue par unité de temps) · **Type / plage :** réel > 0 · **Variable Python :** `kappa`

$$
q
$$

**Sens :** fraction conservée à chaque pas, forme discrète · **Type / plage :** réel dans ]0 ; 1[ · **Variable Python :** `q`

$$
t_{1/2}
$$

**Sens :** demi-vie : temps au bout duquel il ne reste que la moitié de S₀ · **Type / plage :** réel > 0 · **Variable Python :** `demi_vie(lam)`

L'ancienne version de ce fichier notait la pente linéaire α. Elle s'écrit désormais κ, parce que α désigne un poids dans les formules suivantes (score de pertinence à l'étape 17, score hybride à l'étape 23) et qu'un même symbole ne doit pas avoir deux sens dans un même calcul.

## Démonstration

### 1. La fraction perdue par unité de temps est constante

On compare le score à deux instants séparés d'une durée Δ :

$$
\frac{S(t+\Delta)}{S(t)} = \frac{S_0\, e^{-\lambda (t+\Delta)}}{S_0\, e^{-\lambda t}} = e^{-\lambda \Delta}
$$

Le résultat ne dépend pas de t, parce que eᵃ⁺ᵇ = eᵃ eᵇ et que le facteur

$$
e^{-\lambda t}
$$

se simplifie. Sur chaque jour, le souvenir garde donc la même fraction de ce qu'il avait la veille : avec λ = 0,1 par jour, il garde e⁻⁰,¹ ≈ 0,9048, soit 90,48 %, quel que soit son âge.

### 2. La perte est rapide au début, puis de plus en plus lente

La dérivée vaut

$$
S'(t) = -\lambda S_0 e^{-\lambda t} = -\lambda S(t)
$$

La vitesse de perte est proportionnelle à ce qui reste. Elle est donc maximale à t = 0, où elle vaut λ S₀, puis diminue à mesure que S(t) diminue. L'ancienne phrase « douce au début, plus rapide ensuite » décrivait l'inverse : c'est le profil d'une gaussienne ou d'une sigmoïde, pas d'une exponentielle. En chiffres, avec S₀ = 1 et λ = 0,1, la perte vaut 0,0952 entre les jours 0 et 1, 0,0350 entre les jours 10 et 11, et 0,0129 entre les jours 20 et 21.

### 3. La demi-vie

On cherche le temps

$$
t_{1/2}
$$

tel que

$$
S(t_{1/2}) = S_0/2
$$

$$
e^{-\lambda t_{1/2}} = \frac{1}{2}
\;\Longleftrightarrow\;
-\lambda t_{1/2} = \ln\frac{1}{2} = -\ln 2
\;\Longleftrightarrow\;
t_{1/2} = \frac{\ln 2}{\lambda}
$$

On passe à la deuxième égalité en prenant le logarithme naturel des deux côtés, parce que ln(eˣ) = x. Avec λ = 0,1 par jour,

$$
t_{1/2} = 0{,}6931 / 0{,}1 = 6{,}931
$$

jours. Après k demi-vies, il reste S₀ / 2ᵏ : un huitième après trois demi-vies. C'est la façon la plus parlante de régler λ en production : on choisit d'abord une demi-vie qui a un sens métier (« une préférence vaut moitié moins au bout d'un mois »), puis on en déduit

$$
\lambda = \ln 2 / t_{1/2} .
$$

### 4. L'exponentielle garde toujours plus que la linéaire

On compare les deux formes quand elles partent avec la même pente, c'est-à-dire κ = λ. Il suffit de montrer que e⁻ˣ ≥ 1 − x pour tout x. Posons f(x) = e⁻ˣ − (1 − x). On a f(0) = 0 et f'(x) = 1 − e⁻ˣ, qui est négative pour x < 0 et positive pour x > 0 : f descend jusqu'à x = 0 puis remonte, donc son minimum vaut f(0) = 0 et f(x) ≥ 0 partout. Géométriquement, 1 − x est la tangente de e⁻ˣ en 0, et une fonction convexe reste au-dessus de ses tangentes. Comme de plus e⁻ˣ > 0, on obtient

$$
S_0 e^{-\lambda t} \ge S_0 \max(0, 1 - \lambda t) ,
$$

avec égalité seulement en t = 0. La forme linéaire atteint 0 en t = 1/κ (10 jours pour κ = 0,1) ; la forme exponentielle ne l'atteint jamais, elle s'en approche seulement.

### 5. La forme discrète est la même courbe

Multiplier par q à chaque pas donne S₀ qᵗ. Comme

$$
q = e^{\ln q} ,
$$

on a

$$
q^t = e^{t \ln q} ,
$$

donc la forme discrète est une exponentielle de taux λ = −ln q. L'article « Generative Agents » (Park et al., 2023) utilise un facteur de 0,995 par heure : λ = −ln 0,995 = 0,0050125 par heure, soit une demi-vie de 0,6931 / 0,0050125 ≈ 138,3 heures, environ 5,8 jours.

### 6. Relire un souvenir le remet à neuf

Le temps t se mesure depuis le **dernier accès**, pas depuis la création. Quand l'agent relit un souvenir et s'en sert, il remet son horloge à zéro et le score retrouve S₀. Un souvenir utile, consulté souvent, reste donc en tête de classement ; un souvenir que personne ne consulte s'efface de lui-même.

### 7. Exemple fait à la main (le code reprend ces nombres)

Avec S₀ = 0,8 et λ = κ = 0,1 par jour :

| t (jours) | Exponentielle 0,8 e⁻⁰,¹ᵗ | Linéaire 0,8max(0, 1 − 0,1t) |
|---|---|---|
| 0 | 0,8 | 0,8 |
| 5 | 0,8 × 0,60653 = 0,48522 | 0,8 × 0,5 = 0,4 |
| 10 | 0,8 × 0,36788 = 0,29430 | 0 |
| 20 | 0,8 × 0,13534 = 0,10827 | 0 |

## Effets et comportement

- **Plus λ est grand, plus l'oubli est rapide.** Doubler λ divise la demi-vie par deux.
- **L'unité de temps fait partie du paramètre.** Un λ « par heure » appliqué à des jours se trompe d'un facteur 24 : λⱼₒᵤᵣ = 24 λₕₑᵤᵣₑ.
- **Le classement par récence seule ne dépend pas de λ.** Si deux souvenirs ont le même S₀, le plus récent gagne quel que soit λ. Le choix de λ compte dès qu'on mélange la récence avec d'autres signaux (étape 17) ou qu'on applique un seuil.
- **Exponentielle ou linéaire ?** L'exponentielle sert à classer en douceur ; il faut lui ajouter un seuil pour archiver. La linéaire sert à faire expirer à date fixe, par exemple pour aligner la mémoire sur une durée de conservation.

## Du symbole au code Python

$$
S_0
$$

**Variable ou fonction :** `score0`, ou `Souvenir.score0`

$$
t
$$

**Variable ou fonction :** `t`, ou `maintenant - dernier_acces`

$$
\lambda,\quad \kappa,\quad q
$$

**Variable ou fonction :** `lam`, `kappa`, `q`

$$
S_0 e^{-\lambda t}
$$

**Variable ou fonction :** `decroissance_exponentielle(score0, t, lam)`

$$
S_0 \max(0, 1 - \kappa t)
$$

**Variable ou fonction :** `decroissance_lineaire(score0, t, kappa)`

$$
\ln 2 / \lambda
$$

**Variable ou fonction :** `demi_vie(lam)`

$$
-\ln q
$$

**Variable ou fonction :** `lam_depuis_facteur(q)`

### Déroulé, ligne par ligne

**`decroissance_exponentielle(score0, t, lam)`**. C'est

$$
S_0 e^{-\lambda t} .
$$

- `if score0 < 0 or t < 0 or lam <= 0` : un temps négatif ou un taux nul n'ont pas de sens. On lève `ValueError` au lieu de renvoyer un nombre faux en silence.
- `return score0 * math.exp(-lam * t)` : `math.exp(x)` calcule eˣ. Avec `score0 = 0.8`, `t = 5`, `lam = 0.1`, l'exposant vaut `-0.5`, `math.exp(-0.5)` vaut 0,60653 et le résultat 0,48522.

**`decroissance_lineaire(score0, t, kappa)`**. C'est S₀ max(0, 1 − κ t).

- `max(0.0, 1.0 - kappa * t)` : pour `t = 5`, `1 - 0.5 = 0.5` ; pour `t = 10`, `1 - 1.0 = 0` ; pour `t = 20`, `1 - 2.0 = -1`, que `max` ramène à 0. Sans ce `max`, le score deviendrait négatif, ce qui n'a pas de sens pour un poids.

**`demi_vie(lam)`** renvoie `math.log(2) / lam`. En Python, `math.log` est le logarithme naturel ln. Pour `lam = 0.1`, cela donne 6,931.

**`lam_depuis_facteur(q)`** renvoie `-math.log(q)`. La garde `0 < q < 1` refuse un facteur qui ferait grandir le souvenir (`q > 1`) ou l'annulerait d'un coup (`q = 0`).

**`Souvenir`** est une `dataclass` à trois champs : le texte, `score0` et `dernier_acces`, mesuré en jours sur une horloge simulée.

- `recence(maintenant, lam)` calcule `t = maintenant - dernier_acces`, puis appelle `decroissance_exponentielle`.
- `relire(maintenant)` met `dernier_acces` à `maintenant`. Au prochain calcul, `t = 0` et le score revaut `score0`.

**`main()`**, bloc par bloc.

1. La boucle parcourt le dictionnaire `attendus`, qui contient les valeurs du tableau de la démonstration. Pour chaque `t`, elle calcule les deux formes. Elle vérifie les valeurs calculées à la main, à `5e-6` près pour l'exponentielle et exactement pour la linéaire, puis l'inégalité `e >= l` démontrée au point 4.
2. Pour chaque intervalle `[debut ; debut + 1]`, on calcule la perte `avant - apres` et le rapport `apres / avant`. Le rapport vaut toujours `math.exp(-0.1)`, soit 0,9048 (point 1). La perte décroît : 0,0952, puis 0,0350, puis 0,0129 (point 2).
3. `t12 = demi_vie(0.1)` vaut 6,931. On vérifie que le score à cet instant vaut exactement `s0 / 2`, soit 0,4.
4. `lam_depuis_facteur(0.995)` donne 0,0050125. La demi-vie vaut 138,3 heures. On vérifie aussi que `0.995 ** 48` (multiplier 48 fois par 0,995) donne la même valeur que `math.exp(-lam_h * 48)` : c'est la même courbe (point 5).
5. Un souvenir écrit au jour 0 vaut 0,2943 au jour 10. Après `relire(10.0)`, il revaut 0,8 (point 6).
6. Deux appels invalides, l'un avec un temps négatif, l'autre avec un taux nul, doivent lever `ValueError`. Si aucune exception n'est levée, `raise AssertionError` arrête le programme.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`decroissance_exponentielle(score0, t, lam)`** — On peut se figurer un archiviste qui ressort une fiche de souvenir et regarde depuis combien de jours elle dort dans son tiroir : la fonction reçoit le poids initial S₀ du souvenir, le temps écoulé t et le taux d'oubli λ, et commence par refuser tout dossier absurde en levant `ValueError` si le score est négatif, si le temps est négatif ou si le taux n'est pas strictement positif. Ce contrôle passé, elle multiplie S₀ par exp(−λ t) grâce à `math.exp` et renvoie ce poids pâli ; avec S₀ = 0,8 et λ = 0,1 par jour, la fiche vaut encore 0,48522 au cinquième jour, 0,29430 au dixième et 0,10827 au vingtième. C'est la brique sur laquelle reposent la méthode `Souvenir.recence` et presque toutes les vérifications de `main`.

**`decroissance_lineaire(score0, t, kappa)`** — Celle-ci ressemble plutôt à une bougie qui fond à vitesse constante : elle reçoit le même score initial, le temps écoulé et une pente κ, refuse elle aussi par `ValueError` un score ou un temps négatif et une pente nulle ou négative, puis retire chaque jour la même fraction κ du poids d'origine. Le facteur 1 − κ t passe par `max(0.0, …)` pour que la bougie, une fois consumée, reste à zéro au lieu de devenir négative ; elle renvoie donc 0,4 au cinquième jour avec S₀ = 0,8 et κ = 0,1, puis 0 dès le dixième. Le programme s'en sert comme point de comparaison, pour montrer que l'exponentielle reste toujours au-dessus de cette droite.

**`demi_vie(lam)`** — Cette petite fonction répond à la question que poserait un bibliothécaire pressé : au bout de combien de temps un souvenir a-t-il perdu la moitié de son éclat ? Elle reçoit le taux λ, divise ln 2, obtenu par `math.log(2)`, par ce taux, et renvoie la durée correspondante, exprimée dans la même unité de temps que λ ; pour λ = 0,1 par jour, elle rend 6,931 jours, et `main` vérifie qu'à cet instant précis le score de 0,8 est tombé à exactement 0,4. Elle ne contrôle rien elle-même, si bien qu'un λ nul y provoquerait une division par zéro.

**`lam_depuis_facteur(q)`** — Elle traduit le langage d'un horloger, qui dit « à chaque tic, le souvenir garde telle part de son poids », dans celui du physicien, qui parle d'un taux continu : elle reçoit le facteur q appliqué à chaque unité de temps, vérifie qu'il est strictement compris entre 0 et 1, sans quoi elle lève `ValueError`, puis renvoie λ = −ln q. Avec q = 0,995 par heure, elle donne λ ≈ 0,0050125 par heure, soit une demi-vie de 138,3 heures, et `main` s'en sert pour constater que multiplier 48 fois par 0,995 revient exactement à appliquer l'exponentielle exp(−48 λ).

**`Souvenir.recence(maintenant, lam)`** — Cette méthode de la petite fiche `Souvenir` agit comme un greffier qui consulte la date inscrite en marge : elle reçoit l'instant présent et le taux λ, calcule le temps écoulé en retranchant `dernier_acces` de `maintenant`, puis confie le calcul à `decroissance_exponentielle` avec le score initial du souvenir. Elle renvoie le poids actuel du souvenir, et laisse remonter la `ValueError` de la fonction appelée si l'horloge est incohérente, c'est-à-dire si le dernier accès semble venir du futur ; dans `main`, le souvenir écrit au jour 0 vaut ainsi 0,2943 au jour 10.

**`Souvenir.relire(maintenant)`** — C'est le geste du lecteur qui rouvre une vieille lettre et lui rend aussitôt sa fraîcheur : la méthode reçoit l'instant présent et l'inscrit dans le champ `dernier_acces` du souvenir, sans rien calculer ni rien renvoyer. Au prochain appel de `recence`, le temps écoulé repart de zéro et le souvenir retrouve tout son poids initial ; c'est ce que `main` vérifie en montrant qu'au jour 10, juste après la relecture, le score remonte de 0,2943 à exactement 0,8.

**`main()`** — Le chef d'orchestre déroule six scènes à la suite, avec S₀ = 0,8 et λ = κ = 0,1 par jour : il compare d'abord l'exponentielle et la droite aux jours 0, 5, 10 et 20 en confrontant chaque valeur au tableau attendu, puis mesure la perte sur trois intervalles d'un jour, 0,0952, 0,0350 et 0,0129, en vérifiant que le rapport d'un jour au suivant reste toujours exp(−0,1). Il contrôle ensuite la demi-vie de 6,931 jours, convertit le facteur horaire 0,995 en un taux et une demi-vie de 138,3 heures, fait vieillir puis relire un souvenir, et termine en s'assurant que deux appels absurdes lèvent bien `ValueError`, faute de quoi il lève lui-même `AssertionError`. Chaque nombre est gardé par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

```python
"""Étape 16 — décroissance temporelle d'un souvenir : exponentielle, linéaire, demi-vie, relecture."""
import math
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def decroissance_exponentielle(score0: float, t: float, lam: float) -> float:
    """S(t) = S0 · e^(−λt)."""
    if score0 < 0 or t < 0 or lam <= 0:
        raise ValueError("il faut score0 >= 0, t >= 0 et lam > 0")
    return score0 * math.exp(-lam * t)


def decroissance_lineaire(score0: float, t: float, kappa: float) -> float:
    """S(t) = S0 · max(0, 1 − κt)."""
    if score0 < 0 or t < 0 or kappa <= 0:
        raise ValueError("il faut score0 >= 0, t >= 0 et kappa > 0")
    return score0 * max(0.0, 1.0 - kappa * t)


def demi_vie(lam: float) -> float:
    """t½ = ln 2 / λ."""
    return math.log(2) / lam


def lam_depuis_facteur(q: float) -> float:
    """Forme discrète S0 · q^t : q = e^(−λ), donc λ = −ln q."""
    if not 0 < q < 1:
        raise ValueError("il faut 0 < q < 1")
    return -math.log(q)


@dataclass
class Souvenir:
    texte: str
    score0: float
    dernier_acces: float  # en jours, sur une horloge simulée (pas l'heure réelle)

    def recence(self, maintenant: float, lam: float) -> float:
        return decroissance_exponentielle(self.score0, maintenant - self.dernier_acces, lam)

    def relire(self, maintenant: float) -> None:
        self.dernier_acces = maintenant  # t repart de 0 : le souvenir retrouve son poids S0


def main() -> None:
    lam = kappa = 0.1  # par jour
    s0 = 0.8

    print("1. Exponentielle contre linéaire (S0 = 0.8, λ = κ = 0.1 par jour)")
    attendus = {0: (0.8, 0.8), 5: (0.48522, 0.4), 10: (0.29430, 0.0), 20: (0.10827, 0.0)}
    for t, (e_att, l_att) in attendus.items():
        e = decroissance_exponentielle(s0, t, lam)
        l = decroissance_lineaire(s0, t, kappa)
        print(f"  t = {t:>2} j   exponentielle = {e:.5f}   linéaire = {l:.5f}")
        assert abs(e - e_att) < 5e-6 and abs(l - l_att) < 1e-12
        assert e >= l  # parce que e^(−x) >= 1 − x

    print("2. Perte sur un jour : grande au début, puis de plus en plus petite")
    pertes = []
    for debut in (0, 10, 20):
        avant = decroissance_exponentielle(1.0, debut, lam)
        apres = decroissance_exponentielle(1.0, debut + 1, lam)
        pertes.append(avant - apres)
        print(f"  [{debut:>2} ; {debut + 1:>2}]   perte = {avant - apres:.4f}   S(t+1)/S(t) = {apres / avant:.4f}")
        assert abs(apres / avant - math.exp(-lam)) < 1e-12
    assert pertes[0] > pertes[1] > pertes[2]
    assert [round(p, 4) for p in pertes] == [0.0952, 0.0350, 0.0129]

    print("3. Demi-vie")
    t12 = demi_vie(lam)
    print(f"  t½ = ln 2 / 0.1 = {t12:.3f} jours ; S(t½) = {decroissance_exponentielle(s0, t12, lam):.4f}")
    assert abs(t12 - 6.931) < 1e-3
    assert abs(decroissance_exponentielle(s0, t12, lam) - s0 / 2) < 1e-12

    print("4. Forme discrète : facteur 0.995 par heure")
    lam_h = lam_depuis_facteur(0.995)
    print(f"  λ = −ln 0.995 = {lam_h:.7f} par heure ; demi-vie = {demi_vie(lam_h):.1f} h = {demi_vie(lam_h) / 24:.2f} jours")
    assert abs(demi_vie(lam_h) - 138.3) < 0.05
    assert abs(0.995 ** 48 - math.exp(-lam_h * 48)) < 1e-12

    print("5. Relire un souvenir remet son horloge à zéro")
    souvenir = Souvenir("Le client cherche un deux-pièces à Dubai Marina", 0.8, dernier_acces=0.0)
    avant = souvenir.recence(10.0, lam)
    souvenir.relire(10.0)
    apres = souvenir.recence(10.0, lam)
    print(f"  jour 10 avant relecture = {avant:.4f} ; juste après = {apres:.4f}")
    assert abs(avant - 0.29430) < 5e-6 and apres == 0.8

    print("6. Entrées invalides refusées")
    for args in ((0.8, -1.0, 0.1), (0.8, 1.0, 0.0)):
        try:
            decroissance_exponentielle(*args)
        except ValueError:
            print(f"  {args} → ValueError")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exponentielle contre linéaire (S0 = 0.8, λ = κ = 0.1 par jour)
  t =  0 j   exponentielle = 0.80000   linéaire = 0.80000
  t =  5 j   exponentielle = 0.48522   linéaire = 0.40000
  t = 10 j   exponentielle = 0.29430   linéaire = 0.00000
  t = 20 j   exponentielle = 0.10827   linéaire = 0.00000
2. Perte sur un jour : grande au début, puis de plus en plus petite
  [ 0 ;  1]   perte = 0.0952   S(t+1)/S(t) = 0.9048
  [10 ; 11]   perte = 0.0350   S(t+1)/S(t) = 0.9048
  [20 ; 21]   perte = 0.0129   S(t+1)/S(t) = 0.9048
3. Demi-vie
  t½ = ln 2 / 0.1 = 6.931 jours ; S(t½) = 0.4000
4. Forme discrète : facteur 0.995 par heure
  λ = −ln 0.995 = 0.0050125 par heure ; demi-vie = 138.3 h = 5.76 jours
5. Relire un souvenir remet son horloge à zéro
  jour 10 avant relecture = 0.2943 ; juste après = 0.8000
6. Entrées invalides refusées
  (0.8, -1.0, 0.1) → ValueError
  (0.8, 1.0, 0.0) → ValueError
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la récence n'est pas une notion floue. C'est une exponentielle dont on choisit la demi-vie, dont on vérifie les valeurs à la main, et dont on remet l'horloge à zéro quand le souvenir sert.

## Squelette algorithmique

L'algorithme note un souvenir par sa récence, puis décide de le garder, de le résumer ou de l'archiver. La demi-vie est le réglage métier, et le taux λ s'en déduit.

```text
ALGORITHME RécenceEtArchivage
ENTRÉES : souvenirs (score initial S₀, dernier accès), maintenant, demi-vie t½, seuil d'archivage s
SORTIE  : pour chaque souvenir : score de récence et décision

  λ ← ln 2 / t½
  POUR CHAQUE souvenir m FAIRE
      t ← maintenant − m.dernier_accès
      SI t < 0 ALORS ERREUR « horloge incohérente »
      m.récence ← m.S₀ × exp(−λ × t)
      SI m.récence < s ALORS décision ← « archiver ou résumer »
      SINON décision ← « garder »
  FIN POUR

ALGORITHME Relire(m, maintenant)
  m.dernier_accès ← maintenant              (le score revient à S₀)

VARIANTE Expiration linéaire
  m.récence ← m.S₀ × max(0, 1 − κ × t)      (atteint 0 en t = 1/κ : expiration à date fixe)
```

**Complexité.** Chaque souvenir coûte O(1) : une soustraction, une exponentielle et une comparaison. Une passe d'archivage sur n souvenirs coûte donc O(n). Comme la récence se calcule à la demande à partir de la date du dernier accès, il n'y a rien à mettre à jour quand le temps passe : seule la relecture modifie une donnée.

**Du squelette au code.** La conversion de la demi-vie correspond à `demi_vie` (dans l'autre sens, λ = ln 2 / t½), le calcul de la récence à `decroissance_exponentielle` et sa variante à `decroissance_lineaire`, la forme discrète à `lam_depuis_facteur`, et la relecture à `Souvenir.relire`. Les gardes qui lèvent `ValueError` pour un temps négatif ou un taux nul sont la ligne « horloge incohérente ».

## Cas d'usage réels aux Émirats

Les valeurs de demi-vie et de seuil ci-dessous sont illustratives : en production, on les règle sur l'historique réel de chaque métier.

### Immobilier — des critères de recherche qui changent

Une agence immobilière de Dubaï déploie un agent qui accompagne les acheteurs pendant plusieurs mois. Il retient chaque critère exprimé comme un souvenir, avec son importance. Trois mois plus tôt, un client cherchait un deux-pièces à Dubai Marina sous 2,2 millions d'AED. Depuis deux jours, il ne parle plus que de villas avec jardin. L'agence a fixé la demi-vie des préférences à 30 jours, soit λ = ln 2 / 30 ≈ 0,0231 par jour. Le critère « Marina », vieux de 90 jours, ne pèse plus que

$$
e^{-0{,}0231 \times 90} \approx 0{,}125
$$

fois son importance initiale, soit trois demi-vies. Le critère « villa », vieux de deux jours, en garde 0,955. L'agent propose donc d'abord des villas et ne mentionne l'appartement qu'en option. Sans décroissance, il continuerait à pousser des biens qui ne correspondent plus au projet, et le client cesserait de répondre. Pour respecter la minimisation des données de la PDPL, l'agence ajoute une décroissance linéaire de pente κ = 1/180 par jour, qui fait expirer à 180 jours tout critère non réactivé. L'indicateur suivi est le taux de visites programmées après une proposition de l'agent.

### Banque — un profil de risque qui vieillit

L'assistant d'investissement d'une banque de détail de Dubaï garde en mémoire l'appétit pour le risque que le client a déclaré lors du dernier entretien. La politique interne de la banque veut qu'un profil ancien ne serve plus à recommander un produit sans nouvelle vérification. L'équipe traduit cette règle par une demi-vie de 180 jours (λ ≈ 0,00385 par jour) et un seuil de 0,3. Au bout d'un an, le souvenir vaut

$$
e^{-0{,}00385 \times 365} \approx 0{,}245 ,
$$

sous le seuil. Le score passe sous 0,3 vers le 313e jour : l'agent repose alors les questions d'adéquation au lieu de supposer que rien n'a changé. Sans ce mécanisme, il recommanderait un fonds risqué sur la base d'une déclaration périmée, ce qui exposerait la banque à une plainte et à une remarque de conformité. L'indicateur suivi est la part des recommandations émises avec un profil de moins de douze mois.

### Crypto — des alertes de liquidité qui perdent leur urgence

Une plateforme d'actifs virtuels agréée par la VARA utilise un agent de surveillance qui mémorise chaque alerte de liquidité sur ses pools. Le temps se compte en heures. Chaque heure, une alerte garde 98 % de son poids (q = 0,98, soit λ ≈ 0,0202 par heure et une demi-vie d'environ 34 heures). Une alerte d'il y a trois jours pèse 0,98⁷² ≈ 0,23 fois sa gravité initiale ; une alerte d'il y a une heure en pèse 0,98. L'agent multiplie la gravité par la récence avant de classer : l'astreinte voit d'abord les incidents en cours, pas l'historique de la semaine. Sans décroissance, la file d'alertes se remplit d'événements résolus et les opérateurs finissent par ignorer les notifications, ce qui est exactement le risque que la surveillance devait réduire. On suit le délai moyen de prise en charge d'une alerte critique.

### RH — un statut de dossier qui doit être revérifié

Un cabinet RH présent dans plusieurs émirats fait suivre par un agent le dossier de chaque nouvel employé : contrat enregistré auprès du MOHRE, visite médicale, demande d'Emirates ID. Un statut administratif périmé est dangereux. L'agent applique donc une décroissance **linéaire** de pente κ = 1/30 par jour à chaque statut mémorisé. Le statut « visite médicale faite », d'importance 0,9, vaut 0,9 × (1 − 12/30) = 0,54 après 12 jours et tombe à 0 au 30e jour. À zéro, l'agent n'a plus le droit de répondre de mémoire : il doit rappeler l'outil qui interroge le système officiel avant de confirmer quoi que ce soit au candidat. On suit le nombre de réponses données à partir d'un statut de plus de 30 jours, avec un objectif de zéro.

### Assurance — les dossiers actifs restent en tête

Un assureur auto et santé confie à un agent l'historique des échanges avec chaque assuré : réclamations, garages contestés, pièces manquantes. La demi-vie est de 60 jours. Une réclamation vieille de 120 jours ne pèse plus qu'un quart de son importance, mais un dossier de sinistre rouvert hier repart presque à neuf, avec

$$
e^{-\ln 2/60} \approx 0{,}99 ,
$$

parce que chaque consultation remet l'horloge à zéro (démonstration, point 6). L'agent présente donc au gestionnaire d'abord les éléments des dossiers vivants, et non les plaintes les plus anciennes. Sans cette remise à zéro, un dossier actif mais ancien disparaîtrait du contexte au moment même où le gestionnaire en a besoin. L'indicateur suivi est le taux de résolution au premier contact.

### Secteur public — une mémoire de conversation qui ne déborde pas

Un service public en ligne accessible par UAE Pass répond en arabe et en anglais. À l'intérieur d'une session, le temps se compte en échanges plutôt qu'en heures. Chaque souvenir conversationnel garde 90 % de son poids à chaque nouvel échange (q = 0,9). Après 10 échanges, un détail donné au début vaut 0,9¹⁰ ≈ 0,35. Au-delà de 16 échanges (0,9¹⁶ ≈ 0,19), il passe sous le seuil de 0,2 et il est résumé au lieu d'être recopié dans le prompt. La langue préférée de l'usager fait exception : l'agent la relit à chaque tour, donc son horloge repart sans cesse de zéro et elle ne s'efface jamais. Sans ce tri, le prompt grossirait à chaque échange et le coût en tokens croîtrait comme le carré du nombre d'étapes (étape 72). On suit le nombre moyen de tokens par session et la justesse des réponses.

## Pièges et limites

- **Mélanger les unités.** Un λ réglé en heures et appliqué à des jours se trompe d'un facteur 24. On écrit l'unité dans le nom de la variable ou dans le commentaire.
- **Confondre λ et la demi-vie.** λ est un taux ; la demi-vie vaut ln 2 / λ. Un λ de 30 n'est pas « 30 jours de mémoire ».
- **Oublier que l'exponentielle n'atteint jamais zéro.** Sans seuil d'archivage, la mémoire grossit sans fin.
- **Prendre la décroissance pour une suppression.** Un score bas n'efface rien : une obligation de suppression (PDPL, politique de conservation) demande un vrai processus d'effacement.
- **Additionner la récence brute à d'autres signaux sans les mettre à la même échelle.** C'est le sujet de l'étape 17.

### Exercice feuille blanche

1. Sans regarder le code, écrire `decroissance_exponentielle` et `demi_vie`, puis vérifier que

$$
S(t_{1/2}) = S_0/2
$$

pour λ = 0,05.
2. Prédire, puis vérifier : avec λ = 0,2 par jour, que vaut S(10)/S₀ ? (Réponse : e⁻² ≈ 0,135.)
3. Trouver le bug : `return score0 * math.exp(lam * t)`. Que deviennent les souvenirs anciens ?

## Pour aller plus loin

La courbe d'oubli d'Ebbinghaus et les algorithmes de répétition espacée (SM-2) reposent sur la même idée d'un oubli rapide puis lent. Certains modèles cognitifs, comme ACT-R, utilisent une loi de puissance t⁻ᵈ, qui oublie encore plus lentement aux grands t qu'une exponentielle.

> Suite : [Score de pertinence d'un souvenir](<17-Memoire-Formule-Score-de-Pertinence.md>) — étape 17.
