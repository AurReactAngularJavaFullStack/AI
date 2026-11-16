### 1.2 Théorème de Régularisation L2 (avec paramètre *λ*)

**Définition** : La régularisation L2 (aussi appelée weight decay) ajoute un terme de pénalité à la fonction de coût :

Jreg(θ)=J(θ)+(λ/2) * ∥θ∥22

où λ>0 est le paramètre de régularisation.

**Démonstration de l'effet sur les poids** : Le gradient devient : ∇θJreg(θ)=∇θJ(θ)+λθ

La mise à jour des paramètres : 

θt+1=θt−η(∇θJ(θt)+λθt)=(1−ηλ)θt−η∇θJ(θt)

Le terme (1−ηλ) agit comme un facteur de décroissance exponentielle sur les poids.

**Exemple** : 

Pour λ=0.001, η=0.01 : 

θt+1=(1−0.00001)θt−0.01∇θJ(θt)≈0.99999θt−0.01∇θJ(θt)

**Rôle dans les LLMs** : 

Le paramètre λ (lambda) contrôle le compromis biais-variance. 

Dans les grands modèles comme GPT-4, λ≈0.1 à 10^−5 est utilisé pour prévenir le surapprentissage et améliorer la généralisation.