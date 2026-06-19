# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PcrProject(models.Model):
    _name = "pcr.project"
    _description = "Проект"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Название проекта", required=True, tracking=True)
    code = fields.Char(
        string="Код",
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("Новый"),
    )
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one("res.partner", string="Заказчик", tracking=True)
    manager_id = fields.Many2one(
        "res.users",
        string="Руководитель проекта",
        default=lambda self: self.env.user,
        tracking=True,
    )
    date_start = fields.Date(string="Дата начала")
    date_end = fields.Date(string="Дата окончания")
    description = fields.Text(string="Описание")
    state = fields.Selection(
        selection=[
            ("draft", "Черновик"),
            ("active", "В работе"),
            ("done", "Завершён"),
            ("cancelled", "Отменён"),
        ],
        string="Статус",
        default="draft",
        required=True,
        tracking=True,
    )
    contract_ids = fields.One2many("pcr.contract", "project_id", string="Договоры")
    contract_count = fields.Integer(
        string="Договоров", compute="_compute_contract_count"
    )

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for project in self:
            project.contract_count = len(project.contract_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code") or vals["code"] == _("Новый"):
                vals["code"] = self.env["ir.sequence"].next_by_code(
                    "pcr.project"
                ) or _("Новый")
        return super().create(vals_list)

    def action_set_active(self):
        self.write({"state": "active"})

    def action_set_done(self):
        self.write({"state": "done"})

    def action_set_cancelled(self):
        self.write({"state": "cancelled"})

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_view_contracts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Договоры"),
            "res_model": "pcr.contract",
            "view_mode": "list,form",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id},
        }
