# Théorème de la Limite Centrale (TLC) — version Typora (tout en blocs `$$ ... $$`)

## 1) À quoi sert le TLC ?

Le TLC explique pourquoi la somme (ou la moyenne) d’un grand nombre de contributions indépendantes, une fois **centrée** et **normalisée**, devient **approximativement normale**.  

Il sert notamment à construire des **intervalles de confiance**, des **tests**, et à justifier la **normalité asymptotique** de nombreux estimateurs.

---

## 2) Énoncé formel (i.i.d. : Lindeberg–Lévy) + notations (tout dans un seul bloc)

$$
\begin{aligned}
&X_1,\dots,X_n \text{ sont i.i.d.},\quad \mathbb{E}[X_1]=\mu,\quad \mathrm{Var}(X_1)=\sigma^2\in(0,\infty),\\[4pt]
&S_n=\sum_{i=1}^{n}X_i,\quad \bar{X}_n=\frac{1}{n}\sum_{i=1}^{n}X_i,\\[4pt]
&\frac{S_n-n\mu}{\sigma\sqrt{n}}\xrightarrow{d}\mathcal{N}(0,1),\quad
\sqrt{n}\,\frac{\bar{X}_n-\mu}{\sigma}\xrightarrow{d}\mathcal{N}(0,1),\\[4pt]
&\xrightarrow{d}\ \text{ signifie convergence en loi (convergence en distribution)},\quad
\mathcal{N}(0,1)\ \text{ est la loi normale centrée réduite}.
\end{aligned}
$$

---

## 3) Interprétation pratique (approximation pour grand `n`)

$$
\begin{aligned}
&\text{Pour } n \text{ grand, } \sqrt{n}\,\frac{\bar{X}_n-\mu}{\sigma}\approx \mathcal{N}(0,1),\\[4pt]
&\text{ce qui équivaut à l’approximation } \bar{X}_n \approx \mathcal{N}\!\left(\mu,\frac{\sigma^2}{n}\right),\\[4pt]
&\text{(approximation : pas une égalité exacte, mais une bonne loi limite).}
\end{aligned}
$$

---

# 4) Démonstrations (esquisses des méthodes principales)

## A) Preuve par fonctions caractéristiques (la plus classique)

$$
\begin{aligned}
&\varphi_X(t)=\mathbb{E}\!\left[e^{itX}\right]\ \text{ (fonction caractéristique)},\\[4pt]
&Z_n=\frac{S_n-n\mu}{\sigma\sqrt{n}},\quad
\varphi_{Z_n}(t)=\left[\varphi_{\frac{X_1-\mu}{\sigma}}\!\left(\frac{t}{\sqrt{n}}\right)\right]^n,\\[6pt]
&\varphi_{\frac{X_1-\mu}{\sigma}}(u)=1-\frac{u^2}{2}+o(u^2)\quad (u\to 0),\\[6pt]
&\Rightarrow\ 
\varphi_{Z_n}(t)=\left(1-\frac{t^2}{2n}+o\!\left(\frac{1}{n}\right)\right)^n \longrightarrow e^{-t^2/2},\\[6pt]
&e^{-t^2/2}\ \text{ est la fonction caractéristique de }\ \mathcal{N}(0,1),\\[4pt]
&\Rightarrow\ Z_n\xrightarrow{d}\mathcal{N}(0,1)\ \text{ (théorème de continuité de Lévy)}.
\end{aligned}
$$

---

## B) Méthode des moments / cumulants (idée)

$$
\begin{aligned}
&\text{But : pour tout entier fixé } k,\quad \mathbb{E}[Z_n^k]\longrightarrow \mathbb{E}[Z^k],\\[4pt]
&Z\sim\mathcal{N}(0,1)\ \Rightarrow\ \text{ les moments limites sont ceux de la normale},\\[4pt]
&\text{(nécessite en général des hypothèses de moments pour contrôler les développements).}
\end{aligned}
$$

---

## C) TLC général : Lindeberg–Feller (indépendantes non identiques)

$$
\begin{aligned}
&X_{n,1},\dots,X_{n,n}\ \text{ indépendantes},\quad \mathbb{E}[X_{n,i}]=0,\\[4pt]
&s_n^2=\sum_{i=1}^{n}\mathrm{Var}(X_{n,i}),\\[6pt]
&\forall\varepsilon>0,\quad
\frac{1}{s_n^2}\sum_{i=1}^{n}\mathbb{E}\!\left[X_{n,i}^2\,\mathbf{1}_{\{|X_{n,i}|>\varepsilon s_n\}}\right]\longrightarrow 0
\quad \text{(condition de Lindeberg)},\\[8pt]
&\Rightarrow\ \frac{\sum_{i=1}^{n}X_{n,i}}{s_n}\xrightarrow{d}\mathcal{N}(0,1).
\end{aligned}
$$

---

## D) Condition de Lyapunov (suffisante, souvent plus simple)

$$
\begin{aligned}
&X_1,\dots,X_n\ \text{ indépendantes centrées},\quad s_n^2=\sum_{i=1}^n\mathrm{Var}(X_i),\\[4pt]
&\exists\delta>0\ \text{ tel que }\ 
\frac{1}{s_n^{2+\delta}}\sum_{i=1}^n\mathbb{E}\!\left[|X_i|^{2+\delta}\right]\longrightarrow 0
\quad \text{(condition de Lyapunov)},\\[6pt]
&\Rightarrow\ \frac{\sum_{i=1}^n X_i}{s_n}\xrightarrow{d}\mathcal{N}(0,1).
\end{aligned}
$$

---

## E) Berry–Esseen (TLC quantitatif : vitesse de convergence)

$$
\begin{aligned}
&X_i \text{ i.i.d.},\quad \mathbb{E}[X_1]=\mu,\quad \mathrm{Var}(X_1)=\sigma^2>0,\quad \mathbb{E}[|X_1-\mu|^3]<\infty,\\[6pt]
&\rho=\mathbb{E}[|X_1-\mu|^3],\quad \Phi \text{ est la CDF de } \mathcal{N}(0,1),\\[6pt]
&\sup_{x\in\mathbb{R}}
\left|
\mathbb{P}\!\left(\frac{S_n-n\mu}{\sigma\sqrt{n}}\le x\right)-\Phi(x)
\right|
\le
\frac{C\,\rho}{\sigma^3\sqrt{n}},\\[4pt]
&\text{où } C \text{ est une constante universelle (borne de vitesse).}
\end{aligned}
$$

---

# 5) Exemples concrets (usage direct)

## Exemple 1 — Bernoulli (proportion)

$$
\begin{aligned}
&X_i\sim \mathrm{Bernoulli}(p),\quad \mu=p,\quad \sigma^2=p(1-p),\quad \hat{p}=\bar{X}_n,\\[6pt]
&\sqrt{n}\,\frac{\hat{p}-p}{\sqrt{p(1-p)}}\xrightarrow{d}\mathcal{N}(0,1),\\[8pt]
&\text{IC 95\% (approx) :}\quad
\hat{p}\ \pm\ 1.96\,\sqrt{\frac{\hat{p}(1-\hat{p})}{n}},\\[4pt]
&\text{(approximation TLC : utile pour quantifier l’incertitude sur une proportion).}
\end{aligned}
$$

---

## Exemple 2 — Exponentielle (asymétrique mais variance finie)

$$
\begin{aligned}
&X_i\sim \mathrm{Exp}(\lambda),\quad \mu=\frac{1}{\lambda},\quad \sigma^2=\frac{1}{\lambda^2},\\[6pt]
&\sqrt{n}\,\frac{\bar{X}_n-\frac{1}{\lambda}}{\frac{1}{\lambda}}\xrightarrow{d}\mathcal{N}(0,1),\\[4pt]
&\text{(la loi de départ n’est pas normale, mais la moyenne devient quasi normale).}
\end{aligned}
$$

---

## Exemple 3 — Somme de dés

$$
\begin{aligned}
&X_i\in\{1,2,3,4,5,6\}\ \text{ uniforme},\quad \mu=3.5,\quad \sigma^2=\frac{35}{12},\\[6pt]
&\frac{S_n-3.5n}{\sqrt{\left(\frac{35}{12}\right)n}}\xrightarrow{d}\mathcal{N}(0,1),\\[6pt]
&\mathbb{P}(S_n\le a)\approx \Phi\!\left(\frac{a-3.5n}{\sqrt{\left(\frac{35}{12}\right)n}}\right)
\quad \text{(approximation normale).}
\end{aligned}
$$

---

# 6) Normalité asymptotique des estimateurs (statistique)

## Schéma “moyenne d’une influence”

$$
\begin{aligned}
&\hat{\theta}_n \approx \theta+\frac{1}{n}\sum_{i=1}^{n}\psi(X_i),\quad \mathrm{Var}(\psi(X_1))<\infty,\\[6pt]
&\Rightarrow\ \sqrt{n}\,(\hat{\theta}_n-\theta)\xrightarrow{d}\mathcal{N}\!\left(0,\mathrm{Var}(\psi(X_1))\right).
\end{aligned}
$$

## Méthode Delta (si l’estimateur est une transformation d’une moyenne)

$$
\begin{aligned}
&\hat{\theta}_n=g(\bar{X}_n),\quad g \text{ dérivable en } \mu,\\[4pt]
&\Rightarrow\ \sqrt{n}\,\left(g(\bar{X}_n)-g(\mu)\right)\xrightarrow{d}
\mathcal{N}\!\left(0,(g'(\mu))^2\sigma^2\right).
\end{aligned}
$$

---

# 7) Rôle dans les forêts aléatoires (arbres / bagging)

$$
\begin{aligned}
&\hat{f}_{\mathrm{RF}}(x)=\frac{1}{B}\sum_{b=1}^{B}T_b(x),\\[4pt]
&\text{(moyenne de prédictions d’arbres ; sous certaines conditions, une normalité asymptotique est plausible)},\\[6pt]
&\text{IC (schéma) :}\quad \hat{f}(x)\ \pm\ z_{0.975}\,\widehat{\mathrm{SE}}(\hat{f}(x)),\\[4pt]
&\text{où } \widehat{\mathrm{SE}}(\hat{f}(x)) \text{ est estimée par des techniques (jackknife, IJ, subsampling, etc.).}
\end{aligned}
$$

---

# 8) Rôle dans les LLMs (évaluation et comparaison A/B)

## A) IC sur une métrique moyenne (loss/score moyen)

$$
\begin{aligned}
&Y_i=\ell(\text{modèle},\text{exemple }i),\quad \bar{Y}_n=\frac{1}{n}\sum_{i=1}^{n}Y_i,\\[6pt]
&\sqrt{n}\,\frac{\bar{Y}_n-\mathbb{E}[Y]}{\sqrt{\mathrm{Var}(Y)}}\xrightarrow{d}\mathcal{N}(0,1),\\[6pt]
&\text{IC 95\% (approx) :}\quad \bar{Y}_n\ \pm\ 1.96\,\frac{s_Y}{\sqrt{n}}
\quad \text{où } s_Y \text{ est l’écart-type empirique des } Y_i.
\end{aligned}
$$

## B) Comparaison appariée de deux modèles (différences)

$$
\begin{aligned}
&D_i=Y_i^{(A)}-Y_i^{(B)},\quad \bar{D}_n=\frac{1}{n}\sum_{i=1}^{n}D_i,\\[6pt]
&\sqrt{n}\,\frac{\bar{D}_n-\mathbb{E}[D]}{\sqrt{\mathrm{Var}(D)}}\xrightarrow{d}\mathcal{N}(0,1),\\[6pt]
&\text{(base d’un test et d’un IC sur le gain moyen entre modèles).}
\end{aligned}
$$

---

# 9) Points d’attention (quand le TLC classique peut échouer)

$$
\begin{aligned}
&\text{Si }\mathrm{Var}(X_1)=\infty,\ \text{le TLC classique peut échouer (queues lourdes).}\\[4pt]
&\text{Dans certains cas, on obtient des limites stables :}\quad
n^{-1/\alpha}\sum_{i=1}^{n}(X_i-\text{centrage})\xrightarrow{d}\text{Stable}_\alpha,\quad 0<\alpha<2.\\[4pt]
&\text{Si dépendances fortes : il faut des TLC adaptés (martingales, mixing, etc.).}
\end{aligned}
$$