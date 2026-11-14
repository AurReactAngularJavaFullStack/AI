# 6. Transformer — Formules Manquantes

## Leçon 6.1 : Multi-Head Attention

**Définition**  
Extension du mécanisme d'attention qui permet au modèle de se concentrer simultanément sur différentes représentations sémantiques (syntaxe, sémantique, coréférence).

**Rôle**  
Permettre à l'agent de comprendre plusieurs aspects d'une phrase en parallèle.

### Équations Mathématiques

$$
\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W^O
$$

$$
\text{head}_i = \text{Attention}(Q W_i^Q, K W_i^K, V W_i^V)
$$

Où :

$$
W_i^Q \in \mathbb{R}^{d_{\text{model}} \times d_k}, \quad
W_i^K \in \mathbb{R}^{d_{\text{model}} \times d_k}, \quad
W_i^V \in \mathbb{R}^{d_{\text{model}} \times d_v}, \quad
W^O \in \mathbb{R}^{h d_v \times d_{\text{model}}}
$$

### Code Python

```python
import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model=512, n_heads=8):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def scaled_dot_product_attention(self, Q, K, V):
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        attn = torch.softmax(scores, dim=-1)
        return torch.matmul(attn, V)
    
    def forward(self, Q, K, V):
        batch_size = Q.size(0)
        
        Q = self.W_q(Q).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        heads = self.scaled_dot_product_attention(Q, K, V)
        
        concat = heads.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.W_o(concat)

# Exemple
mha = MultiHeadAttention(d_model=512, n_heads=8)
x = torch.randn(32, 10, 512)
output = mha(x, x, x)
print(output.shape)  # torch.Size([32, 10, 512])
```

### Démonstration Quantifiée

Avec

$$
d_{\text{model}} = 512
$$

et h = 8 têtes :

- Chaque tête opère sur dₖ = 512 / 8 = 64 dimensions
- Coût computationnel :

$$
O(n^2 \cdot d_{\text{model}})
$$

— identique à une seule tête
- Mémoire : 8 × n² pour les matrices d'attention

---

## Leçon 6.2 : Positional Encoding (Codage Positionnel)

**Définition**  
Comme l'attention est permutation-invariante, le positional encoding injecte l'information de position via des fonctions sinusoïdales.

**Rôle**  
Permettre au modèle de comprendre que « chien mord homme » ≠ « homme mord chien ».

### Équations Mathématiques

$$
PE_{(pos, 2i)} = \sin\left( \frac{pos}{10000^{2i / d_{\text{model}}}} \right)
$$

$$
PE_{(pos, 2i+1)} = \cos\left( \frac{pos}{10000^{2i / d_{\text{model}}}} \right)
$$

Où pos est la position du token et i est l'indice de dimension.

### Code Python

```python
import torch
import math

def positional_encoding(max_len, d_model):
    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len).unsqueeze(1).float()
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                         -(math.log(10000.0) / d_model))
    
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    
    return pe

pe = positional_encoding(100, 512)
print(pe.shape)  # torch.Size([100, 512])
```

### Démonstration Quantifiée

- Position 0 : PE = [0, 1, 0, 1, …]
- Position 1 :

$$
PE = [\sin(1), \cos(1), \sin(10^{-4}), \cos(10^{-4}), \ldots]
$$

- Propriété clé : PEₚₒₛ₊ₖ peut être exprimé comme une fonction linéaire de PEₚₒₛ

---

## Leçon 6.3 : Layer Normalization

**Définition**  
Normalise les activations à chaque couche pour stabiliser l'entraînement des réseaux profonds.

**Rôle**  
Éviter l'explosion/vanishing des gradients dans les Transformers profonds.

### Équations Mathématiques

$$
\text{LayerNorm}(x) = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} \cdot \gamma + \beta
$$

$$
\mu = \frac{1}{d} \sum_{i=1}^{d} x_i, \qquad
\sigma^2 = \frac{1}{d} \sum_{i=1}^{d} (x_i - \mu)^2
$$

### Code Python

```python
import torch
import torch.nn as nn

class LayerNorm(nn.Module):
    def __init__(self, d_model, eps=1e-5):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.beta = nn.Parameter(torch.zeros(d_model))
        self.eps = eps
    
    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.gamma * (x - mean) / (std + self.eps) + self.beta

ln = LayerNorm(512)
x = torch.randn(32, 10, 512) * 10
out = ln(x)
print(out.mean(), out.std())  # ≈ 0, ≈ 1
```

## Ce qui se passe dans ces trois codes

Le récit ligne par ligne, avec les nombres, est dans `06a_MultiHead_Attention.md`, `06b_Positional_Encoding.md` et `06c_Layer_Normalization.md`. Ici, le point qui ne se voit pas en lisant les formules seules :

`div_term` dans le positional encoding n'est pas une autre équation. `exp(2i * (-log(10000) / d))` vaut

$$
10000^{-2i/d} .
$$

Multiplier la position par ce terme, c'est la diviser par

$$
10000^{2i/d} ,
$$

comme dans le sinus du cours.

Dans cette LayerNorm, `x.std()` sans `unbiased=False` divise par d − 1, et `eps` est ajouté au dénominateur après la racine, pas sous elle. La formule du chapitre 6c divise par √(σ² + ϵ) avec σ² moyenné sur d, pas sur d − 1. L'écart est petit. Il devient visible quand on compare un pas d'entraînement au papier. Le code de `06c_Layer_Normalization.md` suit la formule.
