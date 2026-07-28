from odoo import models, fields, api


class HairFormulaIngredient(models.Model):
    """
    A featured ingredient (e.g. Murumuru butter, Argan oil) displayed
    as an icon under the product page's Deep Dive section.

    Ingredients are reusable across products via M2M from product.template.
    """
    _name = 'hairformula.ingredient'
    _description = 'HairFormula Featured Ingredient'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    icon = fields.Image(string='Icon', max_width=256, max_height=256,
                        help='Square icon (PNG with transparency works best). '
                             'If empty, the product page shows a styled placeholder.')
    description = fields.Html(string='Description', translate=True,
                              help='Optional longer description — could be used '
                                   'in tooltips or an ingredient detail page later.')
    active = fields.Boolean(default=True)

    product_count = fields.Integer(
        string='Used in Products',
        compute='_compute_product_count',
    )

    @api.depends()
    def _compute_product_count(self):
        # Aggregate count of products referencing each ingredient
        for ing in self:
            ing.product_count = self.env['product.template'].search_count([
                ('hairformula_ingredient_ids', '=', ing.id),
            ])
