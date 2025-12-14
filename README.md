# E-commerce Product Scraper

A platform-agnostic web scraper for e-commerce websites with AI-powered data enrichment, built with hexagonal architecture (ports and adapters pattern).

## Features

- Scrapes product details from e-commerce websites (currently supports Riachuelo)
- AI-powered product enrichment using Claude API (attributes, categorization, marketing content)
- REST API to query products with enrichment data
- Interactive CLI menu to select products to scrape
- Saves scraped and enriched data to PostgreSQL database
- Platform-agnostic architecture - easily extendable to other e-commerce sites
- Docker support for easy deployment

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized setup)
- Firefox browser (for local development)
- Anthropic API key (for AI enrichment)

## Quick Start with Docker

> **Note:** The API serves data from the database. You must run the scraper first to populate the database with products before querying the API.

### 1. Configure Environment Variables

Copy the example environment file and add your Anthropic API key:

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```bash
ANTHROPIC_API_KEY=your_actual_api_key_here
```

> **Note:** The scraper will work without an API key, but AI enrichment will be skipped.

### 2. Start the Database

```bash
docker-compose up -d db
```

### 2. Run the Scraper to Populate Data

```bash
docker-compose run --rm app
```

This will:
1. Launch the scraper with an interactive menu
2. Scrape selected products from the e-commerce site
3. Enrich products with AI-generated data (if `ANTHROPIC_API_KEY` is set)
4. Save everything to the database

### 3. Start the API Server

After scraping products, start the API to query them:

```bash
docker-compose up -d api
```

### 4. Access the API

Once the API is running, access it at:
- API Documentation: http://localhost:8000/docs
- List all products: http://localhost:8000/api/products
- Get specific product: http://localhost:8000/api/products/1

> **Tip:** If the API returns an empty list, make sure you've run the scraper (step 2) to populate the database first.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Health check |
| `/api/products` | GET | List all products with enrichment data |
| `/api/products/{id}` | GET | Get a specific product by ID |

### Example Response

```json
{
  "id": 1,
  "sku": "15240878",
  "name": "Camiseta de praia infantojuvenil UV raglan 4-16A - Laranja",
  "price": "R$69.99",
  "original_price": null,
  "description": "...",
  "image_url": "...",
  "images": ["..."],
  "url": "...",
  "brand": "Accessori",
  "category": "Infantil > Meninas > Moda praia",
  "color": "Laranja",
  "sizes": ["4", "6", "8", "10", "12", "14", "16"],
  "material": "Poliester reciclado 90%; Elastano 10%",
  "specifications": null,
  "enriched_data": {
    "attributes": {
      "sleeve_type": "long",
      "neckline": "round",
      "fit": "regular",
      "uv_protection": "UV 50+",
      "material_parsed": {
        "primary": "recycled polyester",
        "secondary": "elastane",
        "percentage": "90% / 10%"
      },
      "key_features": ["UV protection", "raglan sleeves", "beach wear"]
    },
    "categorization": {
      "occasions": ["beach", "pool", "water sports"],
      "seasons": ["spring", "summer"],
      "style_tags": ["sporty", "casual", "protective wear"],
      "target_audience": {
        "gender": "girls",
        "age_group": "child",
        "age_range": "4-16 years"
      },
      "search_keywords": ["camiseta UV infantil", "protecao solar crianca"]
    },
    "content": {
      "seo_title": "Camiseta UV 50+ Infantil Manga Longa Praia | Accessori",
      "meta_description": "Camiseta de praia infantil com protecao UV 50+...",
      "short_description": "Camiseta infantil com protecao UV 50+...",
      "marketing_highlights": ["Protecao solar UV 50+", "Tecido sustentavel"]
    },
    "enrichment_metadata": {
      "model": "claude-sonnet-4-20250514",
      "enriched_at": "2025-12-12T10:30:00Z",
      "version": "1.0"
    }
  },
  "created_at": "2025-12-11T14:58:04.120Z",
  "updated_at": "2025-12-11T19:39:01.076Z"
}
```

## AI Enrichment

When the `ANTHROPIC_API_KEY` is configured, the scraper uses Claude AI to analyze scraped product data and generate additional structured information. This enrichment enhances the raw product data with three categories of AI-generated content:

### Attributes

Extracted and normalized product characteristics:

| Field | Description |
|-------|-------------|
| `sleeve_type` | Type of sleeve (e.g., long, short, sleeveless) |
| `neckline` | Neckline style (e.g., round, v-neck, crew) |
| `fit` | Fit type (e.g., regular, slim, loose) |
| `pattern` | Pattern description (e.g., solid, striped, floral) |
| `closure_type` | How the garment closes (e.g., zipper, buttons) |
| `uv_protection` | UV protection level if applicable |
| `material_parsed` | Structured breakdown of materials with percentages |
| `care_instructions` | Washing and care recommendations |
| `key_features` | List of main product features |

### Categorization

Classification and targeting information:

| Field | Description |
|-------|-------------|
| `occasions` | Suitable usage occasions (e.g., beach, casual, formal) |
| `seasons` | Appropriate seasons (e.g., summer, winter, all-season) |
| `style_tags` | Style descriptors (e.g., sporty, elegant, minimalist) |
| `target_audience` | Gender, age group, and age range |
| `search_keywords` | SEO-optimized search terms in Portuguese |
| `complementary_categories` | Related product categories |

### Content

Marketing and SEO content:

| Field | Description |
|-------|-------------|
| `seo_title` | Optimized title for search engines |
| `meta_description` | SEO meta description |
| `short_description` | Concise product summary |
| `marketing_highlights` | Key selling points as bullet points |
| `image_alt_text` | Accessible alt text for product images |

## Using Custom Search Terms

The scraper reads product codes from a CSV file. By default, it uses `search-terms.csv`, but you can use your own file.

### Converting Excel to CSV

If you have product codes in an Excel file (.xlsx), convert it to CSV:

1. Open your Excel file
2. Go to **File > Save As**
3. Choose **CSV (Comma delimited) (*.csv)** as the format
4. Save the file in the project root folder

### CSV Format

The CSV file should have a header row and product codes in the first column:

```csv
search_term
15247848
15247830
15727475
```

### Running with a Custom File

When you run the scraper, it will prompt you for the CSV file path:

```
==================================================
E-COMMERCE PRODUCT SCRAPER
==================================================

CSV file path [search-terms.csv]: my-products.csv
```

- Press **Enter** to use the default `search-terms.csv`
- Type a filename (e.g., `my-products.csv`) to use a different file

You can also specify the file via command-line argument:

```bash
python scraper.py -f my-products.csv
```

## Local Development

### Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
playwright install firefox
```

3. Run the scraper:

```bash
# Without database or AI enrichment
python scraper.py

# With database and AI enrichment
DATABASE_URL="postgresql://scraper:scraper123@localhost:5432/scraper_db" \
ANTHROPIC_API_KEY="your-api-key" \
python scraper.py
```

4. Run the API:

```bash
DATABASE_URL="postgresql://scraper:scraper123@localhost:5432/scraper_db" \
python -m uvicorn api:app --reload
```

## Usage

When you run the scraper, you'll see an interactive menu:

```
==================================================
E-COMMERCE PRODUCT SCRAPER
==================================================

==================================================
AVAILABLE SEARCH TERMS
==================================================
   1. 15247848
   2. 15247830
   3. 15727475
   ...

--------------------------------------------------
OPTIONS:
  a   - Scrape ALL products
  1-N - Scrape a specific product (enter the number)
  c   - Enter a CUSTOM search term
  q   - Quit
--------------------------------------------------

Your choice:
```

### Options

| Input | Action |
|-------|--------|
| `1` | Scrape product #1 from the list |
| `1-5` | Scrape products #1 through #5 |
| `a` | Scrape ALL products from the list |
| `c` | Enter a custom search term |
| `q` | Quit |

## Project Structure

```
├── api.py                     # FastAPI application
├── scraper.py                 # Main scraper orchestrator
├── search-terms.csv           # Product codes to scrape
├── docker-compose.yml         # Docker services configuration
├── Dockerfile                 # Python app container
├── init.sql                   # Database schema
├── requirements.txt           # Python dependencies
├── PROMPTS.md                 # AI enrichment prompts documentation
└── src/
    ├── core/                  # Domain layer (business logic)
    │   ├── dependencies/      # Shared interfaces
    │   └── modules/
    │       └── products/
    │           ├── scrape_product/        # Scraping use case
    │           │   ├── actions/           # Single-purpose operations
    │           │   ├── entities/          # Domain entities (Product)
    │           │   ├── exceptions/        # Domain exceptions
    │           │   ├── gateways/          # Port interfaces (protocols)
    │           │   ├── inputs/            # Input DTOs
    │           │   ├── responses/         # Response DTOs
    │           │   └── use_case/          # Use case orchestration
    │           ├── enrich_product/        # AI enrichment use case
    │           │   ├── actions/           # AI prompt actions
    │           │   ├── entities/          # Enrichment entities
    │           │   ├── exceptions/        # AI exceptions
    │           │   ├── gateways/          # AI gateway protocol
    │           │   ├── inputs/            # Input DTOs
    │           │   ├── responses/         # Response DTOs
    │           │   └── use_case/          # Enrichment orchestration
    │           └── get_products/          # API query use case
    │               ├── entities/          # ProductWithEnrichment entity
    │               ├── gateways/          # Query gateway protocol
    │               ├── responses/         # Response DTOs
    │               └── use_case/          # Query use cases
    └── infrastructure/        # Adapters layer
        ├── adapters/
        │   ├── console_logger_adapter.py
        │   └── products/
        │       ├── scrape_product/        # Scraping adapters
        │       │   ├── playwright_browser_adapter.py
        │       │   ├── riachuelo_ecommerce_adapter.py
        │       │   └── postgres_product_repository_adapter.py
        │       ├── enrich_product/        # AI enrichment adapters
        │       │   ├── claude_ai_adapter.py
        │       │   └── postgres_enrichment_repository_adapter.py
        │       └── get_products/          # API query adapters
        │           └── postgres_product_query_adapter.py
        └── api/               # API layer
            ├── controllers/   # Request handlers
            │   └── products_controller.py
            └── routes/        # FastAPI routes
                └── products.py
```

## Architecture

The project follows hexagonal architecture:

- **Core Layer**: Contains business logic, domain entities, and port interfaces (gateways)
- **Infrastructure Layer**: Contains adapters that implement the gateway interfaces
- **API Layer**: FastAPI routes and controllers

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         SCRAPER FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│  CLI → ScrapeProductUseCase → EcommerceGateway → Browser        │
│                    ↓                                            │
│         EnrichProductUseCase → AIGateway → Claude API           │
│                    ↓                                            │
│         ProductRepository → PostgreSQL                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          API FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│  HTTP Request → Route → Controller → UseCase → Gateway → DB     │
│       ↓                                                         │
│  HTTP Response ← Route ← Controller ← UseCase ← Gateway ← DB    │
└─────────────────────────────────────────────────────────────────┘
```

### Adding a New E-commerce Platform

1. Create a new adapter implementing `EcommerceGateway`:

```python
# src/infrastructure/adapters/products/scrape_product/amazon_ecommerce_adapter.py

class AmazonEcommerceAdapter:
    def __init__(self, browser_gateway: BrowserGateway):
        self.browser = browser_gateway

    @property
    def platform_name(self) -> str:
        return "Amazon"

    def navigate_to_search(self, query: str) -> str:
        # Amazon-specific search navigation
        ...

    def find_product_link(self, query: str) -> str:
        # Amazon-specific product link extraction
        ...

    def navigate_to_product(self, product_url: str, save_debug_files: bool = False) -> None:
        # Amazon-specific product page navigation
        ...

    def extract_product_details(self) -> Product:
        # Amazon-specific data extraction
        ...
```

2. Update `scraper.py` to use your new adapter:

```python
from src.infrastructure.adapters.products.scrape_product.amazon_ecommerce_adapter import (
    AmazonEcommerceAdapter,
)

# In main():
ecommerce_adapter = AmazonEcommerceAdapter(browser_adapter)
```

## Database Schema

### Products Table

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL | Primary key |
| sku | VARCHAR(50) | Product SKU (unique) |
| name | VARCHAR(500) | Product name |
| price | VARCHAR(50) | Current price |
| original_price | VARCHAR(50) | Original price (if on sale) |
| description | TEXT | Product description |
| image_url | TEXT | Main image URL |
| images | JSONB | Array of image URLs |
| url | TEXT | Product page URL |
| brand | VARCHAR(200) | Brand name |
| category | VARCHAR(500) | Product category |
| color | VARCHAR(100) | Color |
| sizes | JSONB | Available sizes |
| material | VARCHAR(500) | Material composition |
| specifications | JSONB | Additional specifications |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Record update time |

### Product Enrichments Table

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL | Primary key |
| product_id | INTEGER | Foreign key to products |
| sleeve_type | VARCHAR(50) | Extracted sleeve type |
| neckline | VARCHAR(50) | Extracted neckline |
| fit | VARCHAR(50) | Extracted fit |
| pattern | VARCHAR(50) | Extracted pattern |
| uv_protection | VARCHAR(50) | UV protection level |
| material_parsed | JSONB | Parsed material info |
| key_features | JSONB | Key features array |
| occasions | JSONB | Usage occasions |
| seasons | JSONB | Appropriate seasons |
| style_tags | JSONB | Style tags |
| target_gender | VARCHAR(50) | Target gender |
| target_age_group | VARCHAR(50) | Target age group |
| search_keywords | JSONB | SEO keywords |
| seo_title | VARCHAR(200) | Generated SEO title |
| meta_description | TEXT | Generated meta description |
| short_description | TEXT | Generated short description |
| marketing_highlights | JSONB | Marketing bullet points |
| model | VARCHAR(100) | AI model used |
| version | VARCHAR(20) | Enrichment version |
| enriched_at | TIMESTAMP | Enrichment timestamp |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | None (runs without persistence) |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | None (runs without AI enrichment) |
| `API_PORT` | Port for the API server | 8000 |

## Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `app` | Interactive scraper | - |
| `api` | REST API server | 8000 |
| `db` | PostgreSQL database | 5432 |

### Commands

```bash
# Start all services
docker-compose up

# Start only API and database
docker-compose up -d db api

# Run scraper interactively
docker-compose run --rm app

# Rebuild after code changes
docker-compose build --no-cache

# View logs
docker-compose logs -f api
```

## Future Improvements

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for a list of planned enhancements and potential features.

## License

MIT
