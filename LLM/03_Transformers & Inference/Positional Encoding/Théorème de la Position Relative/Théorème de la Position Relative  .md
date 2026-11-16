```markdown

```

### 8.2. Théorème de la Position Relative  

**Formule de l'embedding positionnel :**  

PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right)

PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)  

**Application LLM :** 

Permet aux modèles de capturer l'ordre séquentiel sans réseaux récurrents.  

---