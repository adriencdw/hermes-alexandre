# Skill — Recherche Immoweb via Apify

## Rôle de ce skill

Tu es capable de scraper les annonces immobilières sur **Immoweb.be** (Belgique)
via l'actor Apify **crawlerbros/immoweb-scraper** (ID: `UUjIYNdzU5Mo8szQN`).

Utilise ce skill dès que l'utilisateur parle de :
- trouver / chercher des biens immobiliers en Belgique
- appartements, maisons, villas à vendre ou à louer
- critères : commune, code postal, chambres, superficie, prix, etc.

---

## Comment construire une recherche Immoweb

Les recherches se font via des **URLs Immoweb** passées à l'actor Apify.

### Structure de l'URL

```
https://www.immoweb.be/en/search/{TYPE}/{TRANSACTION}?countries=BE&{FILTRES}
```

### Types de biens (`TYPE`)
- `house` — maison
- `apartment` — appartement
- `villa` — villa
- `penthouse` — penthouse
- `land` — terrain
- `office` — bureau
- `house,apartment` — maison OU appartement

### Transaction (`TRANSACTION`)
- `for-sale` — à vendre
- `for-rent` — à louer

### Filtres disponibles (paramètres URL)

| Filtre | Paramètre URL | Exemple |
|---|---|---|
| Code(s) postal(aux) | `postalCodes=BE-1150,BE-1160` | Woluwe-Saint-Pierre + Auderghem |
| Chambres min | `minBedroomCount=2` | au moins 2 chambres |
| Chambres max | `maxBedroomCount=4` | au plus 4 chambres |
| Prix min (€) | `minPrice=200000` | à partir de 200 000 € |
| Prix max (€) | `maxPrice=600000` | jusqu'à 600 000 € |
| Surface min (m²) | `minSurface=80` | au moins 80 m² |
| Surface max (m²) | `maxSurface=200` | au plus 200 m² |
| Classe énergie | `energyClass=A,B` | classe A ou B |

### Codes postaux utiles (Bruxelles)

| Commune | Code postal |
|---|---|
| Woluwe-Saint-Pierre | BE-1150 |
| Woluwe-Saint-Lambert | BE-1200 |
| Auderghem | BE-1160 |
| Uccle | BE-1180 |
| Ixelles | BE-1050 |
| Etterbeek | BE-1040 |
| Schaerbeek | BE-1030 |
| Bruxelles-ville | BE-1000 |
| Waterloo | BE-1410 |
| Rhode-Saint-Genèse | BE-1640 |

### Exemple d'URL complète

```
https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&postalCodes=BE-1150,BE-1200&minBedroomCount=2&maxPrice=500000&minSurface=80
```

---

## Procédure de recherche

1. **Construis l'URL** selon les critères de l'utilisateur
2. **Lance l'actor Apify** via le tool MCP `mcp_apify_run-actor` :

```json
{
  "actorId": "UUjIYNdzU5Mo8szQN",
  "runInput": {
    "searchUrls": ["<URL_CONSTRUITE>"],
    "maxItems": 20,
    "proxyConfiguration": {
      "useApifyProxy": true,
      "apifyProxyGroups": ["RESIDENTIAL"],
      "apifyProxyCountry": "BE"
    }
  }
}
```

3. **Présente les résultats** de façon claire : prix, adresse, chambres, surface, lien
4. **Propose de sauvegarder** la recherche si l'utilisateur la fait plusieurs fois

---

## Recherches sauvegardées

Les recherches fréquentes sont stockées dans `/opt/data/saved_searches.json`.
Utilise le script `immoweb_search.py` pour les gérer.

### Sauvegarder une recherche
```bash
python3 /opt/data/skills/immoweb/immoweb_search.py save "nom_recherche" '{"searchUrls":["..."],"maxItems":20}'
```

### Lister les recherches sauvegardées
```bash
python3 /opt/data/skills/immoweb/immoweb_search.py list
```

### Relancer une recherche sauvegardée
```bash
python3 /opt/data/skills/immoweb/immoweb_search.py run "nom_recherche"
```

---

## Format de présentation des résultats

Pour chaque annonce, affiche :
- 🏠 **Type** — Adresse (commune, code postal)
- 💶 Prix
- 🛏 X chambres | 📐 X m²
- ⚡ Classe énergie (si dispo)
- 🔗 [Voir l'annonce](url)

Groupe par commune si plusieurs communes dans la recherche.
Trie par prix croissant par défaut sauf si l'utilisateur demande autrement.
