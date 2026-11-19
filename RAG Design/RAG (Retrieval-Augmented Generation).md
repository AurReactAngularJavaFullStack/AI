## **RAG (Retrieval-Augmented Generation)**

### **Définition**

- **Système IA qui combine la recherche d’informations dans ta base documentaire interne (Retrieval)** et **la génération de réponses personnalisées (LLM)**.
   ➔ En gros, l’IA va puiser dans ta doc privée pour répondre précisément aux questions des clients/actuaires/souscripteurs.

### **Rôle & Intérêts**

- **Répondre vite** aux requêtes réglementaires, actuarielles, ou clients.
- **Personnalisation** du service : FAQ dynamique, génération de rapports, documentation automatisée, onboarding accéléré.
- **Barrière de sortie** : tes clients s’habituent à des réponses ultra-ciblées sur leur portefeuille, ils ne pourront pas migrer facilement chez un concurrent “générique”.

### **Pros**

- Gain de productivité énorme (support, onboarding, conformité).
- Moins de dépendance à la formation humaine → moins de turnover.
- Crée un actif propriétaire : ta base documentaire + la couche d’IA fine-tunée.

### **Cons**

- Coût initial : collecter la bonne data, setup du pipeline RAG, monitoring (logs, hallucinations).
- Maintenance continue : nouveaux documents à intégrer, risques de fuite/confidentialité (RGPD/PII).
- Risque de “hallucination” si le corpus est trop pauvre ou pas maintenu.

### **Exemple concret (chiffré, SaaS tarification climatique)**

- **Base documentaire** : 2 000 pages internes (règles actuarielles, études météo, guidelines conformité).
- **Implémentation RAG** :
  - Coût initial de setup (OpenAI/Anthropic + vector DB + infra) : 9 000 €
  - Maintenance mensuelle (update doc, monitoring, infra) : 800 €/mois
- **Productivité** :
  - 40% tickets support automatisés (vs. 5% sans RAG)
  - Onboarding client : 2 jours (vs. 8 jours auparavant)
  - Clients économisent en moyenne 15 h/mois de recherche réglementaire interne (valorisé à 90 €/h = 1 350 €/mois par client)
- **Barrière de sortie** :
  - Pour quitter ta solution, le client doit exporter/reconstituer tout son historique de cas + prompts + FAQs sur mesure (coût de sortie estimé : 7 000–10 000 € en consultance, vs. 0 en restant chez toi).