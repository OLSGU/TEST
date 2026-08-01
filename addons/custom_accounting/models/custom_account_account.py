# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class CustomAccountAccount(models.Model):
    """
    Счёт плана счетов.
    Расширяет стандартную модель account.account дополнительными полями
    и связывает с иерархией групп custom.account.group.
    """
    _name = 'custom.account.account'
    _description = 'Chart of Accounts — Account'
    _order = 'code'
    _rec_name = 'display_name'

    # ── Identity ─────────────────────────────────────────────────────
    code = fields.Char(
        string='Account Code',
        required=True,
        size=64,
        index=True,
        help='Unique numeric/alphanumeric account code (e.g. "1010", "7001")',
    )
    name = fields.Char(
        string='Account Name',
        required=True,
        translate=True,
    )
    display_name = fields.Char(
        string='Display',
        compute='_compute_display_name',
        store=True,
        index=True,
    )
    short_name = fields.Char(
        string='Short Name',
        size=32,
        help='Abbreviated name used in reports.',
    )

    # ── Classification ───────────────────────────────────────────────
    account_type = fields.Selection(
        selection=[
            ('asset_current',        'Current Assets'),
            ('asset_non_current',    'Non-Current Assets'),
            ('asset_cash',           'Cash & Bank'),
            ('asset_receivable',     'Receivable'),
            ('liability_current',    'Current Liabilities'),
            ('liability_non_current','Non-Current Liabilities'),
            ('liability_payable',    'Payable'),
            ('equity',               'Equity'),
            ('equity_unaffected',    'Retained Earnings'),
            ('income',               'Income'),
            ('income_other',         'Other Income'),
            ('expense',              'Expenses'),
            ('expense_depreciation', 'Depreciation'),
            ('expense_direct_cost',  'Cost of Revenue'),
            ('off_balance',          'Off-Balance Sheet'),
        ],
        string='Type',
        required=True,
        default='expense',
        index=True,
    )
    group_id = fields.Many2one(
        comodel_name='custom.account.group',
        string='Account Group',
        index=True,
        help='Группа плана счетов, к которой относится данный счёт.',
    )

    # ── Balance side ─────────────────────────────────────────────────
    normal_balance = fields.Selection(
        selection=[('debit', 'Debit (Дебет)'), ('credit', 'Credit (Кредит)')],
        string='Normal Balance Side',
        required=True,
        default='debit',
        help='The side on which the account normally carries a balance.',
    )
    internal_group = fields.Selection(
        selection=[
            ('asset',     'Asset'),
            ('liability', 'Liability'),
            ('equity',    'Equity'),
            ('income',    'Income'),
            ('expense',   'Expense'),
        ],
        string='Internal Group',
        compute='_compute_internal_group',
        store=True,
    )

    # ── Currency & Company ────────────────────────────────────────────
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Account Currency',
        help='Forces all journal items on this account to use a specific currency.',
    )

    # ── Settings ─────────────────────────────────────────────────────
    reconcile = fields.Boolean(
        string='Allow Reconciliation',
        default=False,
        help='Enable if this account can have journal items reconciled.',
    )
    deprecated = fields.Boolean(
        string='Deprecated',
        default=False,
        index=True,
        help='Deprecated accounts cannot be used for new journal entries.',
    )
    active = fields.Boolean(default=True)
    note = fields.Text(string='Internal Notes')

    # ── Related odoo account ─────────────────────────────────────────
    odoo_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Linked Odoo Account',
        help='Link to the standard Odoo account.account record for integration.',
        index=True,
        ondelete='set null',
    )

    # ── Analytic ─────────────────────────────────────────────────────
    tag_ids = fields.Many2many(
        comodel_name='account.account.tag',
        relation='custom_account_account_tag_rel',
        column1='custom_account_id',
        column2='tag_id',
        string='Tags',
    )

    # ── Statistics ───────────────────────────────────────────────────
    journal_line_count = fields.Integer(
        string='Journal Lines',
        compute='_compute_journal_line_count',
    )

    # ── Computes ─────────────────────────────────────────────────────
    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.code} {rec.name}' if rec.code else rec.name

    @api.depends('account_type')
    def _compute_internal_group(self):
        mapping = {
            'asset_current':        'asset',
            'asset_non_current':    'asset',
            'asset_cash':           'asset',
            'asset_receivable':     'asset',
            'liability_current':    'liability',
            'liability_non_current':'liability',
            'liability_payable':    'liability',
            'equity':               'equity',
            'equity_unaffected':    'equity',
            'income':               'income',
            'income_other':         'income',
            'expense':              'expense',
            'expense_depreciation': 'expense',
            'expense_direct_cost':  'expense',
            'off_balance':          'asset',
        }
        for rec in self:
            rec.internal_group = mapping.get(rec.account_type, 'asset')

    def _compute_journal_line_count(self):
        Line = self.env['custom.account.move.line']
        for rec in self:
            rec.journal_line_count = Line.search_count([('custom_account_id', '=', rec.id)])

    # ── Constraints ──────────────────────────────────────────────────
    _sql_constraints = [
        ('code_company_unique', 'UNIQUE(code, company_id)', 'The account code must be unique per company.'),
    ]

    @api.constrains('deprecated', 'reconcile')
    def _check_deprecated(self):
        for rec in self:
            if rec.deprecated and self.env['custom.account.move.line'].search(
                [('custom_account_id', '=', rec.id)], limit=1
            ):
                pass  # allow deprecation even with lines — just warn

    # ── CRUD overrides ───────────────────────────────────────────────
    @api.onchange('account_type')
    def _onchange_account_type(self):
        """Auto-fill normal balance side based on account type."""
        debit_types = {
            'asset_current', 'asset_non_current', 'asset_cash',
            'asset_receivable', 'expense', 'expense_depreciation',
            'expense_direct_cost', 'off_balance',
        }
        if self.account_type in debit_types:
            self.normal_balance = 'debit'
        else:
            self.normal_balance = 'credit'

    @api.onchange('group_id')
    def _onchange_group_id(self):
        if self.group_id and self.group_id.account_type and not self.account_type:
            self.account_type = self.group_id.account_type

    # ── Actions ──────────────────────────────────────────────────────
    def action_view_journal_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Journal Lines for %s') % self.display_name,
            'res_model': 'custom.account.move.line',
            'view_mode': 'list,form',
            'domain': [('custom_account_id', '=', self.id)],
        }
