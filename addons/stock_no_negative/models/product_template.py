# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_negative_stock = fields.Boolean(
        string="Разрешить отрицательный остаток",
        help="Если включено, этот товар может уходить в отрицательный "
        "остаток на внутренних складах.",
    )
