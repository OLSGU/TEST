from odoo import models, fields


class ProductTemplate(models.Model):
    """
    HairFormula extensions to product.template — adds the editorial content
    blocks shown on the custom product page (Time Deficiency, Deep Dive tabs,
    Featured Ingredients).
    """
    _inherit = 'product.template'

    # ---- Time Deficiency block (just after Add to Cart on product page) ----
    time_deficiency_html = fields.Html(
        string='Time Deficiency',
        translate=True,
        sanitize=True,
        help='Short editorial block shown right under Add to Cart. '
             'Typically bullet points: who it\'s for, what it solves, how to apply.',
    )

    # ---- Deep Dive tabs (full-width section below product detail) ----
    deep_dive_ritual_html = fields.Html(
        string='Deep Dive — Ritual',
        translate=True,
        sanitize=True,
        help='Content for the "Ritual" tab in the Deep Dive section. '
             'Describe the usage ritual, mood, timing.',
    )
    deep_dive_composition_html = fields.Html(
        string='Deep Dive — Pure Composition',
        translate=True,
        sanitize=True,
        help='Content for the "Pure Composition" tab in the Deep Dive section. '
             'Describe what\'s in the formula at a deeper level.',
    )

    # ---- Featured Ingredients (icon row under Deep Dive) ----
    hairformula_ingredient_ids = fields.Many2many(
        comodel_name='hairformula.ingredient',
        relation='product_template_hf_ingredient_rel',
        column1='product_template_id',
        column2='ingredient_id',
        string='Featured Ingredients',
        help='Pick the 3–6 ingredients you want to highlight as a visual '
             'signature for this product.',
    )
