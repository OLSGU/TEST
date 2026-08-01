# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    pcr_contract_id = fields.Many2one(
        "pcr.contract",
        string="Договор",
        tracking=True,
        index=True,
        help="Договор из реестра, к которому относится счёт. "
             "Суммы счёта учитываются в расчёте по договору.",
    )
    pcr_project_id = fields.Many2one(
        "pcr.project",
        related="pcr_contract_id.project_id",
        string="Проект",
        store=True,
        readonly=True,
        index=True,
    )

    @api.onchange("pcr_contract_id")
    def _onchange_pcr_contract_id(self):
        """Подставляем контрагента из договора, если он ещё не задан."""
        for move in self:
            contract = move.pcr_contract_id
            if contract and contract.partner_id and not move.partner_id:
                move.partner_id = contract.partner_id

    @api.onchange("partner_id")
    def _onchange_partner_reset_contract(self):
        """Сбрасываем договор, если он не соответствует новому контрагенту."""
        for move in self:
            contract = move.pcr_contract_id
            if (
                contract
                and contract.partner_id
                and move.partner_id
                and contract.partner_id != move.partner_id
            ):
                move.pcr_contract_id = False
