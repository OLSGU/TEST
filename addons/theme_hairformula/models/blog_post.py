from odoo import models, fields


class BlogPost(models.Model):
    """
    HairFormula extension — links blog posts to the products they reference.
    Powers the "Products from the article" block on the Expert Page.
    """
    _inherit = 'blog.post'

    hairformula_product_ids = fields.Many2many(
        comodel_name='product.template',
        relation='blog_post_hf_product_rel',
        column1='blog_post_id',
        column2='product_template_id',
        string='Featured Products',
        help='Products to surface in the "Products from the article" '
             'block at the bottom of this post.',
    )
