# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Российские реквизиты контрагента. Официальная локализация l10n_ru
    # в Odoo больше не поставляется, поэтому минимально необходимые поля
    # вводим здесь.
    l10n_ru_inn = fields.Char(string="ИНН", index=True)
    l10n_ru_kpp = fields.Char(string="КПП")
    l10n_ru_ogrn = fields.Char(string="ОГРН / ОГРНИП")

    @api.constrains("l10n_ru_inn", "l10n_ru_kpp", "l10n_ru_ogrn")
    def _check_ru_requisites(self):
        for partner in self:
            inn = (partner.l10n_ru_inn or "").strip()
            if inn:
                if not inn.isdigit() or len(inn) not in (10, 12):
                    raise ValidationError(_(
                        "ИНН должен состоять из 10 цифр (организация) "
                        "или 12 цифр (ИП/физлицо)."
                    ))
            kpp = (partner.l10n_ru_kpp or "").strip()
            if kpp and (not kpp.isdigit() or len(kpp) != 9):
                raise ValidationError(_("КПП должен состоять из 9 цифр."))
            ogrn = (partner.l10n_ru_ogrn or "").strip()
            if ogrn and (not ogrn.isdigit() or len(ogrn) not in (13, 15)):
                raise ValidationError(_(
                    "ОГРН должен состоять из 13 цифр (ОГРН) "
                    "или 15 цифр (ОГРНИП)."
                ))
