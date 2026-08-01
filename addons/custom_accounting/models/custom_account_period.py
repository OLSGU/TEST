# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class CustomAccountPeriod(models.Model):
    """
    Учётный период (месяц / квартал / год).
    Используется для группировки проводок и закрытия периодов.
    """
    _name = 'custom.account.period'
    _description = 'Accounting Period'
    _order = 'date_start desc'

    name = fields.Char(string='Period Name', required=True)
    code = fields.Char(string='Code', size=12)
    date_start = fields.Date(string='Start Date', required=True)
    date_stop = fields.Date(string='End Date', required=True)
    period_type = fields.Selection(
        selection=[
            ('month',   'Monthly'),
            ('quarter', 'Quarterly'),
            ('year',    'Annual'),
            ('other',   'Other'),
        ],
        string='Period Type',
        default='month',
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        selection=[
            ('draft',  'Open'),
            ('done',   'Closed'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False,
    )
    note = fields.Text(string='Notes')

    # ── Computed ─────────────────────────────────────────────────────
    move_count = fields.Integer(
        string='Journal Entries',
        compute='_compute_move_count',
    )

    def _compute_move_count(self):
        for rec in self:
            rec.move_count = self.env['custom.account.move.line'].search_count([
                ('date', '>=', rec.date_start),
                ('date', '<=', rec.date_stop),
                ('company_id', '=', rec.company_id.id),
            ])

    # ── Constraints ──────────────────────────────────────────────────
    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        for rec in self:
            if rec.date_start > rec.date_stop:
                raise ValidationError(_('Start date must be before end date.'))

    _sql_constraints = [
        ('code_company_uniq', 'UNIQUE(code, company_id)', 'Period code must be unique per company.'),
    ]

    # ── Actions ──────────────────────────────────────────────────────
    def action_close(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'done'

    def action_reopen(self):
        for rec in self:
            if rec.state == 'done':
                rec.state = 'draft'

    def action_view_moves(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Journal Lines in %s') % self.name,
            'res_model': 'custom.account.move.line',
            'view_mode': 'list',
            'domain': [
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_stop),
                ('company_id', '=', self.company_id.id),
            ],
        }
