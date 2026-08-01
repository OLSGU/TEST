# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PcrContract(models.Model):
    _name = "pcr.contract"
    _description = "Договор"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_signed desc, id desc"

    name = fields.Char(
        string="Номер договора",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("Новый"),
        tracking=True,
    )
    title = fields.Char(string="Предмет договора", tracking=True)
    active = fields.Boolean(default=True)
    project_id = fields.Many2one(
        "pcr.project",
        string="Проект",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    partner_id = fields.Many2one("res.partner", string="Контрагент", tracking=True)
    contract_type = fields.Selection(
        selection=[
            ("service", "Услуги"),
            ("supply", "Поставка"),
            ("work", "Подряд"),
            ("other", "Прочее"),
        ],
        string="Тип договора",
        default="service",
    )
    date_signed = fields.Date(string="Дата подписания")
    date_start = fields.Date(string="Действует с")
    date_end = fields.Date(string="Действует по")
    currency_id = fields.Many2one(
        "res.currency",
        string="Валюта",
        default=lambda self: self.env.company.currency_id,
    )
    amount = fields.Monetary(
        string="Сумма", currency_field="currency_id", tracking=True
    )
    state = fields.Selection(
        selection=[
            ("draft", "Черновик"),
            ("signed", "Подписан"),
            ("active", "Действует"),
            ("closed", "Закрыт"),
            ("terminated", "Расторгнут"),
        ],
        string="Статус",
        default="draft",
        required=True,
        tracking=True,
    )
    document_ids = fields.One2many("pcr.document", "contract_id", string="Документы")
    document_count = fields.Integer(
        string="Документов", compute="_compute_document_count"
    )
    note = fields.Html(string="Примечание")

    # --- Бухгалтерия: связь со счетами и расчёт сумм по договору ---
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

    @api.depends("document_ids")
    def _compute_document_count(self):
        for contract in self:
            contract.document_count = len(contract.document_ids)

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("Новый"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "pcr.contract"
                ) or _("Новый")
        return super().create(vals_list)

    def action_set_signed(self):
        self.write({"state": "signed"})

    def action_set_active(self):
        self.write({"state": "active"})

    def action_set_closed(self):
        self.write({"state": "closed"})

    def action_set_terminated(self):
        self.write({"state": "terminated"})

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_view_documents(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Документы"),
            "res_model": "pcr.document",
            "view_mode": "list,form",
            "domain": [("contract_id", "=", self.id)],
            "context": {"default_contract_id": self.id},
        }

    def action_view_invoices(self):
        self.ensure_one()
        context = {"default_pcr_contract_id": self.id}
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
