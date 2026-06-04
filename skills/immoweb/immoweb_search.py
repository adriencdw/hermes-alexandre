#!/usr/bin/env python3
"""
Skill Immoweb — URL builder + recherches sauvegardées.
Usage:
  immoweb_search.py build <params_json>     → construit une URL Immoweb
  immoweb_search.py save <nom> <input_json> → sauvegarde une recherche
  immoweb_search.py list                    → liste les recherches sauvegardées
  immoweb_search.py get <nom>               → retourne l'input JSON d'une recherche
  immoweb_search.py delete <nom>            → supprime une recherche sauvegardée
"""

import json
import os
import sys
from urllib.parse import urlencode

SAVED_PATH = "/opt/data/saved_searches.json"
BASE_URL = "https://www.immoweb.be/en/search"

PROPERTY_TYPES = {
    "maison": "house", "house": "house",
    "appartement": "apartment", "apartment": "apartment",
    "villa": "villa",
    "penthouse": "penthouse",
    "terrain": "land", "land": "land",
    "bureau": "office", "office": "office",
}

TRANSACTIONS = {
    "vente": "for-sale", "vendre": "for-sale", "for-sale": "for-sale", "sale": "for-sale",
    "location": "for-rent", "louer": "for-rent", "for-rent": "for-rent", "rent": "for-rent",
}

COMMUNES = {
    "woluwe-saint-pierre": "BE-1150", "woluwe saint pierre": "BE-1150", "wsp": "BE-1150",
    "woluwe-saint-lambert": "BE-1200", "woluwe saint lambert": "BE-1200", "wsl": "BE-1200",
    "auderghem": "BE-1160",
    "uccle": "BE-1180",
    "ixelles": "BE-1050",
    "etterbeek": "BE-1040",
    "schaerbeek": "BE-1030",
    "bruxelles": "BE-1000", "brussels": "BE-1000",
    "waterloo": "BE-1410",
    "rhode-saint-genese": "BE-1640", "rhode saint genese": "BE-1640",
    "forest": "BE-1190",
    "anderlecht": "BE-1070",
    "molenbeek": "BE-1080",
    "jette": "BE-1090",
    "laeken": "BE-1020",
}


def build_url(params: dict) -> str:
    """Construit une URL Immoweb depuis un dict de critères."""
    prop_type = params.get("type", "house")
    prop_type = PROPERTY_TYPES.get(prop_type.lower(), prop_type)

    transaction = params.get("transaction", "for-sale")
    transaction = TRANSACTIONS.get(transaction.lower(), transaction)

    filters = {"countries": "BE"}

    # Codes postaux
    postal_codes = params.get("postalCodes", params.get("communes", []))
    if isinstance(postal_codes, str):
        postal_codes = [postal_codes]
    resolved = []
    for pc in postal_codes:
        resolved.append(COMMUNES.get(pc.lower(), pc))
    if resolved:
        filters["postalCodes"] = ",".join(resolved)

    # Chambres
    if "minBedrooms" in params:
        filters["minBedroomCount"] = params["minBedrooms"]
    if "maxBedrooms" in params:
        filters["maxBedroomCount"] = params["maxBedrooms"]

    # Prix
    if "minPrice" in params:
        filters["minPrice"] = params["minPrice"]
    if "maxPrice" in params:
        filters["maxPrice"] = params["maxPrice"]

    # Surface
    if "minSurface" in params:
        filters["minSurface"] = params["minSurface"]
    if "maxSurface" in params:
        filters["maxSurface"] = params["maxSurface"]

    # Classe énergie
    if "energyClass" in params:
        filters["energyClass"] = params["energyClass"]

    url = f"{BASE_URL}/{prop_type}/{transaction}?{urlencode(filters)}"
    return url


def build_actor_input(params: dict, max_items: int = 20) -> dict:
    """Construit l'input JSON complet pour l'actor Apify."""
    url = build_url(params)
    return {
        "searchUrls": [url],
        "maxItems": max_items,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
            "apifyProxyCountry": "BE"
        }
    }


def load_saved() -> dict:
    if not os.path.exists(SAVED_PATH):
        return {}
    with open(SAVED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_search(name: str, actor_input: dict):
    searches = load_saved()
    searches[name] = actor_input
    os.makedirs(os.path.dirname(SAVED_PATH), exist_ok=True)
    with open(SAVED_PATH, "w", encoding="utf-8") as f:
        json.dump(searches, f, indent=2, ensure_ascii=False)
    print(f"Recherche '{name}' sauvegardée.")


def list_searches():
    searches = load_saved()
    if not searches:
        print("Aucune recherche sauvegardée.")
        return
    print(f"{len(searches)} recherche(s) sauvegardée(s) :\n")
    for name, data in searches.items():
        urls = data.get("searchUrls", [])
        print(f"  • {name}")
        for url in urls:
            print(f"    {url}")


def get_search(name: str) -> dict:
    searches = load_saved()
    if name not in searches:
        print(f"Recherche '{name}' introuvable.", file=sys.stderr)
        sys.exit(1)
    return searches[name]


def delete_search(name: str):
    searches = load_saved()
    if name not in searches:
        print(f"Recherche '{name}' introuvable.", file=sys.stderr)
        sys.exit(1)
    del searches[name]
    with open(SAVED_PATH, "w", encoding="utf-8") as f:
        json.dump(searches, f, indent=2, ensure_ascii=False)
    print(f"Recherche '{name}' supprimée.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "build":
        params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        result = build_actor_input(params)
        print(json.dumps(result, indent=2))

    elif cmd == "save":
        if len(sys.argv) < 4:
            print("Usage: immoweb_search.py save <nom> <input_json>")
            sys.exit(1)
        save_search(sys.argv[2], json.loads(sys.argv[3]))

    elif cmd == "list":
        list_searches()

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: immoweb_search.py get <nom>")
            sys.exit(1)
        result = get_search(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: immoweb_search.py delete <nom>")
            sys.exit(1)
        delete_search(sys.argv[2])

    else:
        print(f"Commande inconnue: {cmd}")
        sys.exit(1)
