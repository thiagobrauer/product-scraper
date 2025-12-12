-- Initialize database schema for product scraping

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE,
    name VARCHAR(500) NOT NULL,
    price VARCHAR(50),
    original_price VARCHAR(50),
    description TEXT,
    image_url TEXT,
    images JSONB,
    url TEXT,
    brand VARCHAR(200),
    category VARCHAR(500),
    color VARCHAR(100),
    sizes JSONB,
    material VARCHAR(500),
    specifications JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups on products
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Product enrichments table (stores AI-generated data)
CREATE TABLE IF NOT EXISTS product_enrichments (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,

    -- Attributes (physical characteristics)
    sleeve_type VARCHAR(50),
    neckline VARCHAR(50),
    fit VARCHAR(50),
    closure_type VARCHAR(50),
    pattern VARCHAR(50),
    heel_height VARCHAR(50),
    toe_style VARCHAR(50),
    uv_protection VARCHAR(50),
    material_parsed JSONB,  -- { "primary": "...", "secondary": "...", "percentage": "..." }
    care_instructions TEXT,
    key_features JSONB,  -- ["feature1", "feature2", ...]

    -- Categorization
    occasions JSONB,  -- ["beach", "pool", ...]
    seasons JSONB,  -- ["summer", "spring", ...]
    style_tags JSONB,  -- ["sporty", "casual", ...]
    target_gender VARCHAR(50),
    target_age_group VARCHAR(50),
    target_age_range VARCHAR(50),
    search_keywords JSONB,  -- ["keyword1", "keyword2", ...]
    complementary_categories JSONB,  -- ["swimwear", "sunscreen", ...]

    -- Content (SEO and marketing)
    seo_title VARCHAR(200),
    meta_description TEXT,
    short_description TEXT,
    marketing_highlights JSONB,  -- ["highlight1", "highlight2", ...]
    image_alt_text TEXT,

    -- Metadata
    model VARCHAR(100),  -- AI model used for enrichment
    version VARCHAR(20),  -- Enrichment schema version
    enriched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups on enrichments
CREATE INDEX IF NOT EXISTS idx_enrichments_product_id ON product_enrichments(product_id);
CREATE INDEX IF NOT EXISTS idx_enrichments_model ON product_enrichments(model);
CREATE INDEX IF NOT EXISTS idx_enrichments_enriched_at ON product_enrichments(enriched_at);

-- GIN indexes for JSONB array searches
CREATE INDEX IF NOT EXISTS idx_enrichments_occasions ON product_enrichments USING GIN (occasions);
CREATE INDEX IF NOT EXISTS idx_enrichments_seasons ON product_enrichments USING GIN (seasons);
CREATE INDEX IF NOT EXISTS idx_enrichments_style_tags ON product_enrichments USING GIN (style_tags);
CREATE INDEX IF NOT EXISTS idx_enrichments_search_keywords ON product_enrichments USING GIN (search_keywords);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at on products
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update updated_at on enrichments
DROP TRIGGER IF EXISTS update_enrichments_updated_at ON product_enrichments;
CREATE TRIGGER update_enrichments_updated_at
    BEFORE UPDATE ON product_enrichments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View to get products with their latest enrichment
CREATE OR REPLACE VIEW products_with_enrichments AS
SELECT
    p.*,
    e.id AS enrichment_id,
    e.sleeve_type,
    e.neckline,
    e.fit,
    e.closure_type,
    e.pattern,
    e.uv_protection,
    e.material_parsed,
    e.care_instructions,
    e.key_features,
    e.occasions,
    e.seasons,
    e.style_tags,
    e.target_gender,
    e.target_age_group,
    e.target_age_range,
    e.search_keywords,
    e.complementary_categories,
    e.seo_title,
    e.meta_description,
    e.short_description,
    e.marketing_highlights,
    e.image_alt_text,
    e.model AS enrichment_model,
    e.version AS enrichment_version,
    e.enriched_at
FROM products p
LEFT JOIN LATERAL (
    SELECT *
    FROM product_enrichments pe
    WHERE pe.product_id = p.id
    ORDER BY pe.enriched_at DESC
    LIMIT 1
) e ON true;
