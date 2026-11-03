# -*- coding: utf-8 -*-
from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    allow_negative_stock = fields.Boolean(
        string="Разрешить отрицательный остаток",
        help="Если включено, остатки в этом месте хранения могут "
        "становиться отрицательными.",
    )
