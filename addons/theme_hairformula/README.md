# theme_hairformula

Premium hair care e-commerce theme for **Odoo 19 Community**.

## What's in this module (v19.0.5.0.0 — full scope complete)

### Foundation
- Brand palette as primary SCSS variables
- Bootstrap overrides — `$primary` set to brand CTA
- Typography: Cormorant Garamond (display) + Manrope (body) via Google Fonts

### Snippets (drag-droppable in website editor)
- **HairFormula Hero** — main page hero
- **HairFormula Assistant** — interactive tag-based product recommender

### Backend & data
- New model: **`hairformula.ingredient`** with name, icon, description, sequence
- Extended `product.template` with: `time_deficiency_html`, `deep_dive_ritual_html`, `deep_dive_composition_html`, `hairformula_ingredient_ids`
- Extended `blog.post` with: `hairformula_product_ids` (M2M to product.template)
- New menu: `Sales → Products → HairFormula Ingredients`
- "HairFormula" tab on product form
- "HairFormula" group on blog post form
- Access rights: public/portal/user read; sales manager full CRUD on ingredients
- Seed data: 6 hair-condition tags, 6 product categories, 5 starter ingredients
- JSON-RPC controller `/hairformula/assistant/{tags,recommend}` powering Assistant Block
- Pre-built `/assistant` page

### Catalog (`/shop`)
- **Smart-Filter** pill bar at the top — top-level categories as terracotta pills, "Все" / category navigation
- Product cards restyled (warm cream image area, Cormorant title, brand hover)

### Product page (`/shop/<slug>`)
- **Time Deficiency** block — editorial micro-block after Add to Cart with brand-coloured left border
- **Deep Dive** full-width section below product detail:
  - Two tabs (`Ritual` / `Pure Composition`) using Bootstrap native tab.js
  - Persistent ingredient signature row below tabs — circular icons + names (icon image, or styled initial fallback)
- All blocks render conditionally

### Expert Page (`/blog/<post>`)
- **Products from the article** full-width section below blog content
- Grid of cards (3/2/1 columns by screen) showing linked products with image, name, price, terracotta CTA
- Editorial typography lift on post title and subtitle
- Renders only when post has linked products

## Installation

1. Drop the `theme_hairformula/` folder into your Odoo addons path
2. `Apps → Update Apps List`
3. Search "HairFormula" and click Install
4. `Website → Configuration → Themes → HairFormula` → activate

## After install — quick walkthrough

**Homepage:**
- Drag `HairFormula Hero` from Structure panel
- Replace placeholder portrait + bottle via Odoo image editor

**Assistant Block:**
- Visit `/assistant` (auto-created on install)
- 6 hair-condition tags load from `product.tag`
- For real cards, products need `Sales > Tags` and `Website > Is Published`

**Catalog:**
- Visit `/shop` — Smart-Filter pill bar at top
- Products need `eCommerce > Categories` set to appear under the right pill

**Product page:**
- Open any product → **HairFormula** tab in the backend form
- Fill: Featured Ingredients, Time Deficiency, Deep Dive — Ritual, Deep Dive — Pure Composition
- `Go to Website` to see the rendered page

**Expert Page (blog):**
- Create a blog post in `Website → Blog Posts`
- In the form, scroll down to the **HairFormula** group → pick Featured Products
- Publish, visit the post URL — "Products from the article" section appears below the article

## Architecture notes

- **All custom fields use sanitized HTML** — content managers get a rich editor, no XSS risk
- **Tabs use Bootstrap's native tab.js** — no custom JavaScript needed
- **Ingredient row persists across product page tabs** — designed as a "product signature"
- **Icon fallback in CSS** — products without ingredient icons still look polished (styled initial in brand color)
- **XPath targets verified against odoo/odoo v19.0 source:**
  - `.o_wsale_product_details_content_section_cta` (Time Deficiency)
  - `#product_detail` (Deep Dive)
  - `#o_wsale_container` (Smart-Filter)
  - `#o_wblog_post_main` (Products from article)
- All custom CSS namespaced under `.hf-*` / `.s_hairformula_*` — no Odoo core collisions
- Assistant widget uses native `fetch()` — version-agnostic across Odoo 14→19
- Smart-Filter uses standard `/shop/category/<id>` URLs — no custom controller, works with pagination/search/SEO

## Module structure

```
theme_hairformula/
├── __manifest__.py
├── __init__.py
├── README.md
├── controllers/
│   ├── __init__.py
│   └── assistant.py
├── models/
│   ├── __init__.py
│   ├── hairformula_ingredient.py
│   ├── product_template.py
│   └── blog_post.py
├── data/
│   ├── product_tags.xml
│   ├── product_public_categories.xml
│   ├── hairformula_ingredients.xml
│   └── assistant_page.xml
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── website_templates.xml
│   ├── website_sale_templates.xml
│   ├── website_sale_product_templates.xml
│   ├── website_blog_templates.xml
│   ├── hairformula_ingredient_views.xml
│   ├── product_template_views.xml
│   ├── blog_post_views.xml
│   └── snippets/
│       ├── s_hairformula_hero.xml
│       ├── s_hairformula_assistant.xml
│       └── snippets.xml
└── static/
    └── src/
        ├── scss/
        │   ├── primary_variables.scss
        │   ├── bootstrap_overridden.scss
        │   └── theme.scss
        ├── js/
        │   └── assistant_widget.js
        └── img/
            ├── hero_placeholder.svg
            ├── bottle_placeholder.svg
            ├── snippet_thumb_hero.svg
            └── snippet_thumb_assistant.svg
```

## Dependencies

- `website` · `website_sale` · `website_blog`

## License

LGPL-3
