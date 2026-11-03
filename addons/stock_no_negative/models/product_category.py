# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    allow_negative_stock = fields.Boolean(
        string="Разрешить отрицательный остаток",
        help="Если включено, товары этой категории могут уходить в "
        "отрицательный остаток на внутренних складах.",
    )
