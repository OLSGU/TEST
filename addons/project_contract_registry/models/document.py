# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PcrDocument(models.Model):
    _name = "pcr.document"
    _description = "Документ"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Наименование", required=True, tracking=True)
    reference = fields.Char(
        string="Рег. номер",
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("Новый"),
    )
    active = fields.Boolean(default=True)
    contract_id = fields.Many2one(
        "pcr.contract",
        string="Договор",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    project_id = fields.Many2one(
        related="contract_id.project_id",
        string="Проект",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="contract_id.partner_id",
        string="Контрагент",
        store=True,
        readonly=True,
    )
    doc_type = fields.Selection(
        selection=[
            ("contract", "Договор"),
            ("annex", "Приложение"),
            ("act", "Акт"),
            ("invoice", "Счёт"),
            ("other", "Прочее"),
        ],
        string="Тип документа",
        default="other",
        required=True,
    )
    date = fields.Date(string="Дата документа", default=fields.Date.context_today)
    file = fields.Binary(string="Файл", attachment=True)
    file_name = fields.Char(string="Имя файла")
    state = fields.Selection(
        selection=[
            ("draft", "Черновик"),
            ("confirmed", "Подтверждён"),
            ("archived", "В архиве"),
        ],
        string="Статус",
        default="draft",
        required=True,
        tracking=True,
    )
    note = fields.Text(string="Примечание")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("reference") or vals["reference"] == _("Новый"):
                vals["reference"] = self.env["ir.sequence"].next_by_code(
                    "pcr.document"
                ) or _("Новый")
        return super().create(vals_list)

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_archive_doc(self):
        self.write({"state": "archived"})

    def action_set_draft(self):
        self.write({"state": "draft"})
