# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Договор и проект фильтруются по выбранному контакту (partner_id) счёта:
    # показываем записи этого контрагента либо без привязки к контрагенту.
    pcr_contract_id = fields.Many2one(
        "pcr.contract",
        string="Договор",
        index=True,
        tracking=True,
        domain="['|', ('partner_id', '=', partner_id), ('partner_id', '=', False)]",
        help="Договор из реестра, к которому относится счёт. "
             "Суммы счёта учитываются в расчёте по договору.",
    )
    pcr_project_id = fields.Many2one(
        "pcr.project",
        string="Проект",
        index=True,
        domain="['|', ('partner_id', '=', partner_id), ('partner_id', '=', False)]",
        help="Проект из реестра. Подтягивается из выбранного договора, "
             "но может быть указан вручную.",
    )

    @api.onchange("pcr_contract_id")
    def _onchange_pcr_contract_id(self):
        """Договор задаёт проект и, при отсутствии, контрагента."""
        for move in self:
            contract = move.pcr_contract_id
            if not contract:
                continue
            if contract.project_id:
                move.pcr_project_id = contract.project_id
            if contract.partner_id and not move.partner_id:
                move.partner_id = contract.partner_id

    @api.onchange("partner_id")
    def _onchange_partner_reset_pcr_links(self):
        """Сбрасываем договор/проект, не относящиеся к новому контрагенту."""
        for move in self:
            partner = move.partner_id
            contract = move.pcr_contract_id
            if (
                contract
                and contract.partner_id
                and partner
                and contract.partner_id != partner
            ):
                move.pcr_contract_id = False
            project = move.pcr_project_id
            if (
                project
                and project.partner_id
                and partner
                and project.partner_id != partner
            ):
                move.pcr_project_id = False
