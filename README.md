![Banner](./assets/banner.svg)

# 🛒 Supermarket API

![Python](https://img.shields.io/badge/-Python-3776ab?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![Pydantic](https://img.shields.io/badge/-Pydantic-e92063?style=for-the-badge&logo=pydantic&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-d71f00?style=for-the-badge&logo=sqlalchemy&logoColor=white) ![MySQL](https://img.shields.io/badge/-MySQL-4479a1?style=for-the-badge&logo=mysql&logoColor=white) ![SQLite](https://img.shields.io/badge/-SQLite-003b57?style=for-the-badge&logo=sqlite&logoColor=white) ![Swagger](https://img.shields.io/badge/-Swagger-85ea2d?style=for-the-badge&logo=swagger&logoColor=000) ![Uvicorn](https://img.shields.io/badge/-Uvicorn-2a2a2a?style=for-the-badge&logo=gunicorn&logoColor=white)

Supermarket API es una API REST autoalojada que extrae el **catálogo completo** de productos de supermercados españoles 🛒 — nombre, descripción, marca, precio actual estimado, precio por unidad, categoría, EAN y foto — y lo sirve con búsqueda, filtros y paginación. Construida con **FastAPI** y **arquitectura por capas** (clean architecture), guarda los datos en **MySQL** o **SQLite** vía SQLAlchemy.

> 💡 Los precios son los de la tienda online de cada cadena y pueden variar por zona: trátalos como **precio actual estimado**. El scraping usa concurrencia limitada y reintentos con backoff para no saturar las webs de origen.

---

## ⚙️ Stack técnico

- 🧩 **Backend**: FastAPI, Python 3.12+, Pydantic v2 y pydantic-settings para configuración vía `.env`.
- 🗄️ **Persistencia**: SQLAlchemy 2.0 (ORM), MySQL en producción (PyMySQL) y SQLite en desarrollo sin configurar nada.
- 🕷️ **Scraping**: httpx asíncrono con reintentos, backoff exponencial y límite de concurrencia (semáforos asyncio).
- 📖 **Documentación**: OpenAPI/Swagger generada automáticamente en `/docs`, con descripciones por campo.
- 🏗️ **Arquitectura**: capas `api → services → repositories → models/schemas`, dependencias en una sola dirección.
- 🆕 **HTTP QUERY**: endpoints de consulta con el método QUERY (RFC 10008, junio 2026) conviviendo con los GET clásicos.
- 💾 **Backups automáticos**: antes de cada reemplazo de catálogo se genera un script `.sql` restaurable, con retención configurable.

---

## ✨ Qué puedes hacer

- 🛒 Descargar el catálogo **completo** de Mercadona, Consum, Masymas y Lidl (~26.000 productos) con una sola petición.
- 🔍 Buscar productos por nombre, descripción o marca, con filtros por supermercado y categoría, paginados.
- 📊 Consultar el estado de cada catálogo: cuántos productos hay y cuándo se scrapeó por última vez.
- ⏱️ Lanzar scrapings en segundo plano y seguir su progreso sin bloquear la API.
- 💾 Descargar backups `.sql` del catálogo para restaurarlo si un scraping sale mal.
- 🔄 Cruzar el mismo producto entre cadenas gracias al código de barras (EAN).

---

## 🚀 Características

- **Catálogo completo, no muestras**: recorre todas las categorías y páginas de cada tienda online.
- **Scraping resiliente**: reintentos con backoff, y las categorías que Mercadona rate-limita se recuperan en una pasada final pausada.
- **Datos normalizados**: cada supermercado devuelve un formato distinto; la API los unifica en un único esquema `Product`.
- **Backups con red de seguridad**: cada reemplazo de catálogo guarda antes un `.sql` del estado anterior, en la misma transacción.

## 🏛️ Arquitectura

```mermaid
%%{init: {
    "theme": "base",
    "flowchart": {
        "htmlLabels": false,
        "nodeSpacing": 60,
        "rankSpacing": 90,
        "padding": 20,
        "curve": "basis"
    },
    "themeVariables": {
        "fontSize": "15px",
        "primaryColor": "#1f2937",
        "primaryTextColor": "#f9fafb",
        "primaryBorderColor": "#60a5fa",
        "lineColor": "#94a3b8",
        "tertiaryColor": "#0f172a"
    }
}}%%

flowchart LR
    U["👤 Cliente"] --> A

    subgraph S1["🌐 API FastAPI :8000"]
        direction LR
        A["🔌 api/routes<br/>GET · QUERY · POST"] --> B["🧠 services<br/>catálogo · scraping · backups"]
        B --> C["🗄️ repositories<br/>único acceso a BBDD"]
    end

    subgraph S2["🕷️ Scrapers"]
        direction TB
        D["🟢 mercadona.py"]
        E["🟠 aktios.py<br/>Consum + Masymas"]
        L["🔵 lidl.py"]
    end

    subgraph S3["🏪 Tiendas online"]
        direction TB
        F["tienda.mercadona.es"]
        G["tienda.consum.es"]
        H["tienda.masymas.com"]
        I["www.lidl.es"]
    end

    B --> D
    B --> E
    B --> L
    D -- "httpx async" --> F
    E -- "httpx async" --> G
    E -- "httpx async" --> H
    L -- "httpx async" --> I
    C --> DB[("💽 MySQL / SQLite<br/>products<br/>product_backups")]

    classDef api fill:#0f172a,stroke:#38bdf8,color:#f8fafc,stroke-width:2px;
    classDef scraper fill:#111827,stroke:#c084fc,color:#f8fafc,stroke-width:2px;
    classDef tienda fill:#08111f,stroke:#34d399,color:#f8fafc,stroke-width:2px;
    classDef user fill:#1f2937,stroke:#f59e0b,color:#fff7ed,stroke-width:2px,stroke-dasharray: 5 3;

    class A,B,C api;
    class D,E,L scraper;
    class F,G,H,I tienda;
    class U user;

    style S1 fill:#08111f,stroke:#38bdf8,stroke-width:1.5px,stroke-dasharray: 4 4,color:#e2e8f0
    style S2 fill:#0b1220,stroke:#c084fc,stroke-width:1.5px,stroke-dasharray: 4 4,color:#e2e8f0
    style S3 fill:#08111f,stroke:#34d399,stroke-width:1.5px,stroke-dasharray: 4 4,color:#e2e8f0
```

| Componente | Tecnología | Detalle |
| ---------- | ---------- | ------- |
| API | FastAPI + Uvicorn | Capa HTTP con GET, POST y **QUERY (RFC 10008)**. Swagger en `/docs`. Puerto **8000**. |
| Scrapers | httpx asíncrono | Mercadona (API de categorías), Aktios (API compartida por Consum y Masymas) y Lidl (API de búsqueda de su web). |
| BBDD | MySQL / SQLite vía SQLAlchemy | `products` (catálogo) y `product_backups` (scripts .sql de respaldo). |

### 🏪 Fuentes de datos

| Supermercado | Fuente | Productos aprox. |
| ------------ | ------ | ---------------- |
| Mercadona | API pública `tienda.mercadona.es/api` (árbol de categorías) | ~4.400 |
| Consum | API REST Aktios `tienda.consum.es/api/rest/V1.0` (paginada por offset) | ~9.200 |
| Masymas | API REST Aktios `tienda.masymas.com/api/rest/V1.0` (misma plataforma) | ~7.700 |
| Lidl | API de búsqueda `www.lidl.es/q/api/search` (doble pasada por offset) | ~4.800 |

---

## 📡 Endpoints

| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| `GET` | `/products` | Productos con filtros (`supermarket`, `q`, `category`) y paginación |
| `QUERY` | `/products` | Igual, pero con los filtros en el body como JSON (RFC 10008) |
| `GET` / `QUERY` | `/supermarkets` | Supermercados con nº de productos y fecha del último scraping |
| `POST` | `/scrape` | Lanza el scraping de todos los supermercados en segundo plano |
| `POST` | `/scrape/{supermarket}` | Lanza el scraping de uno: `mercadona`, `consum`, `masymas` o `lidl` |
| `GET` / `QUERY` | `/scrape/status` | Estado de los trabajos de scraping |
| `GET` | `/backups` | Lista los backups automáticos del catálogo |
| `GET` | `/backups/{id}/download` | Descarga el backup como fichero `.sql` restaurable |

```bash
# Descargar todos los catálogos (tarda unos minutos, corre en segundo plano)
curl -X POST http://localhost:8000/scrape

# Buscar aceite de oliva en Mercadona (GET clásico)
curl "http://localhost:8000/products?supermarket=mercadona&q=aceite%20de%20oliva"

# Lo mismo con el método QUERY (filtros en el body)
curl -X QUERY http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"supermarket": "mercadona", "q": "aceite de oliva"}'
```

---

## 🚀 Instalación y uso

```bash
python3 -m venv .venv
source .venv/bin/activate   # o usa uv / .venv/bin/uvicorn directamente
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Documentación interactiva en <http://localhost:8000/docs>.

### 🗄️ Base de datos

Sin configurar nada, la API usa **SQLite** en `data/products.db` — perfecto para desarrollo.

Para **MySQL** en producción, copia `.env.example` a `.env` y ajusta la URL:

```bash
SUPERMARKET_API_DATABASE_URL=mysql+pymysql://usuario:password@host:3306/supermarket_api?charset=utf8mb4
```

La base de datos debe existir (`CREATE DATABASE supermarket_api CHARACTER SET utf8mb4;`); las tablas se crean solas al arrancar la API. Si tienes catálogos JSON de versiones anteriores, impórtalos con `python -m scripts.import_json`.

---

## 📁 Estructura del proyecto

```
SUPERMARKET-API/
├── .env.example             # Variables de entorno de ejemplo
├── .gitignore               # Archivos y carpetas que Git no debe seguir
├── LICENSE                  # Licencia del proyecto
├── README.md                # Documentación principal del proyecto
├── requirements.txt         # Dependencias de Python
│
├── assets/                  # Recursos del repositorio
│   └── banner.svg           # Banner del README
│
├── data/                    # Datos locales (SQLite y JSON; ignorado por Git)
│
├── scripts/                 # Scripts de utilidad
│   └── import_json.py       # Importa catálogos JSON antiguos a la BBDD
│
└── app/                     # Código fuente de la API
    ├── main.py              # Punto de entrada: crea la app y registra el router
    │
    ├── api/                 # Capa HTTP
    │   ├── router.py        # Router principal que agrupa todas las rutas
    │   └── routes/
    │       ├── products.py  # GET y QUERY de productos y supermercados
    │       ├── scrape.py    # POST de scraping y GET/QUERY de su estado
    │       └── backups.py   # Listado y descarga de backups .sql
    │
    ├── services/            # Lógica de negocio
    │   ├── catalog_service.py # Consultas de catálogo y supermercados
    │   ├── scrape_service.py  # Trabajos de scraping en segundo plano
    │   └── backup_service.py  # Listado y descarga de backups
    │
    ├── repositories/        # Único acceso a la base de datos
    │   ├── product_repository.py # Guardar, contar y buscar productos
    │   └── backup_repository.py  # Generar scripts .sql y retención
    │
    ├── scrapers/            # Extracción de datos
    │   ├── __init__.py      # Punto de entrada: scrape("mercadona")
    │   ├── http.py          # Cliente httpx y GET con reintentos
    │   ├── mercadona.py     # API de categorías de Mercadona
    │   ├── aktios.py        # API compartida por Consum y Masymas
    │   └── lidl.py          # API de búsqueda de www.lidl.es
    │
    ├── models/              # Tablas de la base de datos (SQLAlchemy ORM)
    │   ├── product.py       # Tabla products
    │   └── backup.py        # Tabla product_backups
    │
    ├── schemas/             # Formas de entrada/salida (Pydantic)
    │   ├── product.py       # Product, filtros, paginación y ScrapeJob
    │   └── backup.py        # Ficha de backup
    │
    └── core/                # Configuración e infraestructura
        ├── config.py        # Settings vía variables de entorno / .env
        └── database.py      # Engine, sesiones y creación de tablas
```

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si quieres añadir un supermercado, mejorar un scraper o proponer una funcionalidad:

1. Haz un fork del repositorio
2. Crea una rama para tu cambio (`git checkout -b feature/nuevo-supermercado`)
3. Abre un Pull Request contando qué hace y por qué

Para cambios grandes, abre antes un issue y lo comentamos.

---

## 📄 Licencia

Este proyecto está bajo licencia **Apache 2.0** — puedes usarlo, modificarlo y distribuirlo libremente, siempre que conserves los avisos de copyright ([LICENSE](LICENSE) y [NOTICE](NOTICE)) e indiques los ficheros que modifiques. Incluye concesión explícita de patentes y el software se ofrece "tal cual", **sin garantías de ningún tipo ni responsabilidad para el autor**. Las contribuciones enviadas al proyecto quedan bajo esta misma licencia (cláusula 5).

Copyright (c) 2026 David Torro. Ver el archivo [LICENSE](LICENSE) para más detalles.

> ⚠️ Los datos de productos pertenecen a sus respectivos supermercados (Mercadona, Consum, Masymas y Lidl) y se extraen de sus tiendas online públicas. Este proyecto es educativo: úsalo de forma responsable y respeta los términos de uso de cada web.
