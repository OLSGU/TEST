# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _is_negative_stock_allowed(self):
        """Return True if a negative quantity is allowed for this quant.

        Negative stock is allowed when the exception flag is set on the
        product, its category or the location, or when the location is not
        a physical internal/transit one.
        """
        self.ensure_one()
        location = self.location_id
        product = self.product_id
        # Only physical internal locations hold "real" stock we care about.
        if location.usage not in ("internal", "transit"):
            return True
        # Services and non-tracked goods never produce meaningful stock.
        if not product.is_storable:
            return True
        return bool(
            product.allow_negative_stock
            or product.categ_id.allow_negative_stock
            or location.allow_negative_stock
        )

    @api.constrains("quantity")
    def _check_no_negative_stock(self):
        for quant in self:
            rounding = quant.product_id.uom_id.rounding or 0.01
            if float_compare(quant.quantity, 0.0, precision_rounding=rounding) >= 0:
                continue
            if quant._is_negative_stock_allowed():
                continue
            raise ValidationError(
                _(
                    "Отрицательный остаток запрещён.\n\n"
                    "Товар: %(product)s\n"
                    "Место хранения: %(location)s\n"
                    "Итоговый остаток: %(qty)s %(uom)s\n\n"
                    "Операция отменена, так как остаток стал бы отрицательным. "
                    "Проверьте наличие товара на складе или оформите приход.\n"
                    "При необходимости отрицательный остаток можно разрешить "
                    "в настройках товара, его категории или места хранения."
                )
                % {
                    "product": quant.product_id.display_name,
                    "location": quant.location_id.display_name,
                    "qty": quant.quantity,
                    "uom": quant.product_id.uom_id.name or "",
                }
            )
