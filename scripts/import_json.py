"""
Importa a la base de datos los catálogos JSON de versiones anteriores
(data/<supermercado>.json)
"""

import json
from pathlib import Path
from app.core.config import settings
from app.core.database import init_db
from app.repositories.product_repository import save_catalog
from app.schemas.product import Product

def main() -> None:
    init_db()
    for path in sorted(Path(settings.data_dir).glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        products = [Product(**raw) for raw in payload["products"]]
        save_catalog(payload["supermarket"], products)
        print(f"{payload['supermarket']}: {len(products)} products imported")


if __name__ == "__main__":
    main()
