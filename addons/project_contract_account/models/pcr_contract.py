# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PcrContract(models.Model):
    _inherit = "pcr.contract"

    invoice_ids = fields.One2many(
        "account.move", "pcr_contract_id", string="Счета"
    )
    invoice_count = fields.Integer(
        string="Счетов", compute="_compute_invoice_stats"
    )
    amount_invoiced = fields.Monetary(
        string="Выставлено по счетам",
        currency_field="currency_id",
        compute="_compute_invoice_stats",
        help="Сумма проведённых счетов по договору "
             "(возвраты вычитаются), в валюте договора.",
    )
    amount_residual_to_invoice = fields.Monetary(
        string="Осталось выставить",
        currency_field="currency_id",
        compute="_compute_invoice_stats",
        help="Разница между суммой договора и выставленными счетами.",
    )
    invoiced_progress = fields.Float(
        string="% выставлено",
        compute="_compute_invoice_stats",
        help="Доля суммы договора, покрытая счетами (1.0 = 100%).",
    )

    @api.depends(
        "amount",
        "currency_id",
        "invoice_ids",
        "invoice_ids.state",
        "invoice_ids.move_type",
        "invoice_ids.amount_total",
        "invoice_ids.currency_id",
        "invoice_ids.date",
        "invoice_ids.invoice_date",
    )
    def _compute_invoice_stats(self):
        # Знак вклада счёта в «выставленную» сумму: возвраты уменьшают её.
        sign_by_type = {
            "out_invoice": 1,
            "in_invoice": 1,
            "out_refund": -1,
            "in_refund": -1,
        }
        for contract in self:
            invoices = contract.invoice_ids
            contract.invoice_count = len(invoices)
            company = contract.env.company
            total = 0.0
            for move in invoices:
                sign = sign_by_type.get(move.move_type, 0)
                if not sign or move.state != "posted":
                    continue
                move_date = move.invoice_date or move.date or fields.Date.today()
                amount = move.currency_id._convert(
                    move.amount_total,
                    contract.currency_id,
                    company,
                    move_date,
                ) if contract.currency_id else move.amount_total
                total += sign * amount
            contract.amount_invoiced = total
            contract.amount_residual_to_invoice = contract.amount - total
            contract.invoiced_progress = (
                (total / contract.amount) if contract.amount else 0.0
            )

    def action_view_invoices(self):
        self.ensure_one()
        context = {"default_pcr_contract_id": self.id}
        if self.project_id:
            context["default_pcr_project_id"] = self.project_id.id
        if self.partner_id:
            context["default_partner_id"] = self.partner_id.id
        return {
            "type": "ir.actions.act_window",
            "name": _("Счета"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("pcr_contract_id", "=", self.id)],
            "context": context,
        }
