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

    @api.depends("document_ids")
    def _compute_document_count(self):
        for contract in self:
            contract.document_count = len(contract.document_ids)

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
