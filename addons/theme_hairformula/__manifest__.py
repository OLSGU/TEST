{
    'name': 'HairFormula',
    'description': """
HairFormula — Premium hair care e-commerce theme.
Warm, editorial, refined cosmetics aesthetic.
    """,
    'category': 'Theme/eCommerce',
    'version': '19.0.5.0.0',
    'author': 'HairFormula',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        'website_blog',
    ],
    'data': [
        # Access rights — must load BEFORE views/data that reference the model
        'security/ir.model.access.csv',
        # Seed data — tags, categories, ingredients
        'data/product_tags.xml',
        'data/product_public_categories.xml',
        'data/hairformula_ingredients.xml',
        # Backend views
        'views/hairformula_ingredient_views.xml',
        'views/product_template_views.xml',
        'views/blog_post_views.xml',
        # Frontend templates + snippets
        'views/website_templates.xml',
        'views/website_sale_templates.xml',
        'views/website_sale_product_templates.xml',
        'views/website_blog_templates.xml',
        'views/snippets/s_hairformula_hero.xml',
        'views/snippets/s_hairformula_assistant.xml',
        'views/snippets/snippets.xml',
        # Pre-built /assistant page
        'data/assistant_page.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'theme_hairformula/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'theme_hairformula/static/src/scss/bootstrap_overridden.scss',
            'theme_hairformula/static/src/scss/theme.scss',
            'theme_hairformula/static/src/js/assistant_widget.js',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}
