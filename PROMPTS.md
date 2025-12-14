# Product Data AI Enrichment Guide

This document contains prompts and schemas for enriching e-commerce product data using AI.

---

## Overview

| Prompt | Purpose |
|--------|---------|
| **Attributes Extraction** | Extract structured attributes like sleeve type, neckline, material, etc. |
| **Categorization & Tagging** | Generate occasions, seasons, style tags, and search keywords |
| **Content Generation** | Create SEO titles, meta descriptions, and marketing copy |

---

## 1. Attributes Extraction

### Prompt

```
You are a product data specialist. Extract structured attributes from the product information provided.

Analyze the product name, description, and any available metadata. Extract ONLY attributes that are explicitly mentioned or can be confidently inferred. Use null for attributes that cannot be determined.

Respond in JSON format following this schema:
{
  "sleeve_type": "short" | "long" | "sleeveless" | "3/4" | null,
  "neckline": "round" | "v-neck" | "polo" | "high" | "square" | null,
  "fit": "regular" | "slim" | "loose" | "oversized" | null,
  "closure_type": "button" | "zipper" | "buckle" | "elastic" | "tie" | "none" | null,
  "pattern": "solid" | "striped" | "printed" | "floral" | "geometric" | "checkered" | null,
  "heel_height": "flat" | "low" | "medium" | "high" | null,
  "toe_style": "round" | "pointed" | "square" | "open" | null,
  "uv_protection": string | null,
  "material_parsed": {
    "primary": string | null,
    "secondary": string | null,
    "percentage": string | null
  },
  "care_instructions": string[] | null,
  "key_features": string[]
}
```

### Example Input

```json
{
  "name": "Camiseta de praia infantojuvenil UV raglan 4-16A - Laranja",
  "description": "Possui manga longa, gola redonda, barra tradicional e proteção UV 50+. Marca: Poliéster reciclado 90%; Elastano 10%",
  "material": "Poliéster reciclado 90%; Elastano 10%"
}
```

### Example Output

```json
{
  "sleeve_type": "long",
  "neckline": "round",
  "fit": "regular",
  "closure_type": "none",
  "pattern": "solid",
  "heel_height": null,
  "toe_style": null,
  "uv_protection": "UV 50+",
  "material_parsed": {
    "primary": "recycled polyester",
    "secondary": "elastane",
    "percentage": "90% / 10%"
  },
  "care_instructions": null,
  "key_features": ["UV protection", "raglan sleeves", "beach wear"]
}
```

---

## 2. Categorization & Tagging

### Prompt

```
You are a product categorization specialist for an e-commerce platform. Generate relevant tags and categorizations to improve product discoverability.

Based on the product information, generate:
- Occasions: when/where this product would be used
- Seasons: which seasons this is appropriate for
- Style tags: descriptive style attributes
- Target audience: who this product is for
- Search keywords: terms customers might use to find this

Be specific and practical. Only include relevant tags. Respond in JSON:
{
  "occasions": string[],
  "seasons": string[],
  "style_tags": string[],
  "target_audience": {
    "gender": "male" | "female" | "unisex" | "boys" | "girls" | "kids",
    "age_group": "baby" | "toddler" | "child" | "teen" | "adult" | "senior",
    "age_range": string | null
  },
  "search_keywords": string[],
  "complementary_categories": string[]
}
```

### Example Input

```json
{
  "name": "Camiseta de praia infantojuvenil UV raglan 4-16A - Laranja",
  "description": "Pensando na sua pequena, a Camiseta de praia infantojuvenil UV raglan vai ajudar a protegê-la. É perfeita para curtir o sol, com muita proteção e segurança.",
  "category": "Infantil > Meninas > Moda praia"
}
```

### Example Output

```json
{
  "occasions": ["beach", "pool", "water sports", "outdoor activities", "vacation"],
  "seasons": ["spring", "summer"],
  "style_tags": ["sporty", "casual", "protective wear", "activewear"],
  "target_audience": {
    "gender": "girls",
    "age_group": "child",
    "age_range": "4-16 years"
  },
  "search_keywords": [
    "camiseta UV infantil",
    "proteção solar criança",
    "roupa de praia menina",
    "rashguard infantil",
    "camiseta manga longa praia"
  ],
  "complementary_categories": ["swimwear", "sunscreen", "beach accessories", "swim shorts"]
}
```

---

## 3. Content Generation

### Prompt

```
You are a marketing copywriter for an e-commerce platform. Generate optimized content for the product provided.

Create:
1. SEO title: max 60 characters, include key attributes and brand
2. Meta description: max 155 characters, compelling and keyword-rich
3. Short description: 1-2 sentences for product cards
4. Marketing highlights: 3-5 bullet points for product page
5. Alt text: accessible image description

Write in the same language as the original product. Be accurate - don't invent features not mentioned in the source.

Respond in JSON:
{
  "seo_title": string,
  "meta_description": string,
  "short_description": string,
  "marketing_highlights": string[],
  "image_alt_text": string
}
```

### Example Input

```json
{
  "name": "Camiseta de praia infantojuvenil UV raglan 4-16A - Laranja",
  "description": "Possui manga longa, gola redonda, barra tradicional e proteção UV 50+. Tecido: Poliéster reciclado 90%; Elastano 10%",
  "brand": "Accessori",
  "color": "Laranja"
}
```

### Example Output

```json
{
  "seo_title": "Camiseta UV 50+ Infantil Manga Longa Praia | Accessori",
  "meta_description": "Camiseta de praia infantil com proteção UV 50+. Manga longa, poliéster reciclado. Tamanhos 4-16 anos. Ideal para sol e piscina.",
  "short_description": "Camiseta infantil com proteção UV 50+ e manga longa raglan, perfeita para dias de praia e piscina com máxima proteção solar.",
  "marketing_highlights": [
    "Proteção solar UV 50+ para brincadeiras seguras ao sol",
    "Tecido sustentável com 90% poliéster reciclado",
    "Manga longa raglan para maior liberdade de movimento",
    "Disponível do tamanho 4 ao 16 anos",
    "Secagem rápida e fácil de lavar"
  ],
  "image_alt_text": "Camiseta infantil laranja de manga longa com proteção UV para praia"
}
```

---

## Final Enriched Data Structure

After running all three enrichment prompts, your product data should look like this:

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
  "material": "Poliéster reciclado 90%; Elastano 10%",
  "specifications": null,
  "enriched_data": {
    "attributes": {
      "sleeve_type": "long",
      "neckline": "round",
      "fit": "regular",
      "closure_type": "none",
      "pattern": "solid",
      "heel_height": null,
      "toe_style": null,
      "uv_protection": "UV 50+",
      "material_parsed": {
        "primary": "recycled polyester",
        "secondary": "elastane",
        "percentage": "90% / 10%"
      },
      "care_instructions": null,
      "key_features": ["UV protection", "raglan sleeves", "beach wear"]
    },
    "categorization": {
      "occasions": ["beach", "pool", "water sports", "outdoor activities", "vacation"],
      "seasons": ["spring", "summer"],
      "style_tags": ["sporty", "casual", "protective wear", "activewear"],
      "target_audience": {
        "gender": "girls",
        "age_group": "child",
        "age_range": "4-16 years"
      },
      "search_keywords": [
        "camiseta UV infantil",
        "proteção solar criança",
        "roupa de praia menina",
        "rashguard infantil",
        "camiseta manga longa praia"
      ],
      "complementary_categories": ["swimwear", "sunscreen", "beach accessories", "swim shorts"]
    },
    "content": {
      "seo_title": "Camiseta UV 50+ Infantil Manga Longa Praia | Accessori",
      "meta_description": "Camiseta de praia infantil com proteção UV 50+. Manga longa, poliéster reciclado. Tamanhos 4-16 anos. Ideal para sol e piscina.",
      "short_description": "Camiseta infantil com proteção UV 50+ e manga longa raglan, perfeita para dias de praia e piscina com máxima proteção solar.",
      "marketing_highlights": [
        "Proteção solar UV 50+ para brincadeiras seguras ao sol",
        "Tecido sustentável com 90% poliéster reciclado",
        "Manga longa raglan para maior liberdade de movimento",
        "Disponível do tamanho 4 ao 16 anos",
        "Secagem rápida e fácil de lavar"
      ],
      "image_alt_text": "Camiseta infantil laranja de manga longa com proteção UV para praia"
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

---

## Implementation Tips

### Single vs. Multiple Prompts

| Approach | Pros | Cons |
|----------|------|------|
| **Single prompt** | Fewer API calls, lower cost | Quality degrades with complexity |
| **Multiple prompts** | Better quality, easier to debug | More API calls, higher cost |
| **Grouped prompts** (recommended) | Balance of quality and cost | Moderate complexity |

### Best Practices

1. **Always validate JSON output** - LLMs can sometimes produce malformed JSON
2. **Add retry logic** - API calls can fail; implement exponential backoff
3. **Cache results** - Store enriched data to avoid re-processing
4. **Version your prompts** - Track which prompt version generated each enrichment
5. **Handle encoding** - Clean up encoding issues (e.g., "SandÃ¡lia" → "Sandália") before enrichment
6. **Test with edge cases** - Products with minimal descriptions, unusual categories, etc.

### Rate Limiting Considerations

- Anthropic API has rate limits; batch your requests appropriately
- Consider processing products in parallel with a concurrency limit
- For large catalogs, use a queue system (Redis, RabbitMQ, etc.)

---

## Next Steps

- [ ] Implement data cleaning/encoding fix before enrichment
- [ ] Add image analysis enrichment using vision models
- [ ] Create validation schemas for enrichment outputs
- [ ] Build a pipeline to process products in batch
- [ ] Set up monitoring for enrichment quality