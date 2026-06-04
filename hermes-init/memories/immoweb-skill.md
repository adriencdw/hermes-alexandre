# Instruction permanente — Recherche Immoweb

Quand l'utilisateur demande de chercher des biens immobiliers en Belgique
(appartements, maisons, terrains à vendre ou à louer), tu DOIS utiliser
le skill Immoweb situé dans `/opt/data/skills/immoweb/`.

## Procédure obligatoire

1. Lis les critères de l'utilisateur (commune, type de bien, chambres, prix, m²)
2. Construis l'URL Immoweb avec `immoweb_search.py build` ou directement selon le SKILL.md
3. Lance l'actor Apify `UUjIYNdzU5Mo8szQN` via le MCP tool `mcp_apify_run-actor`
4. Présente les résultats de façon lisible (prix, chambres, m², commune, lien)
5. Propose à l'utilisateur de sauvegarder la recherche si elle est répétée

## Recherches sauvegardées

Si l'utilisateur demande de sauvegarder une recherche :
```bash
python3 /opt/data/skills/immoweb/immoweb_search.py save "nom" '<input_json>'
```

Si l'utilisateur veut relancer une recherche sauvegardée :
```bash
python3 /opt/data/skills/immoweb/immoweb_search.py list   # lister
python3 /opt/data/skills/immoweb/immoweb_search.py get "nom"  # récupérer
```

## Référence

- SKILL.md complet : `/opt/data/skills/immoweb/SKILL.md`
- Actor Apify : `crawlerbros/immoweb-scraper` (ID: `UUjIYNdzU5Mo8szQN`)
- Proxy obligatoire : RESIDENTIAL BE (Cloudflare bloque les datacenter IPs)
