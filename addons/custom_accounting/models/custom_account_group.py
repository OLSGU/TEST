# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class CustomAccountGroup(models.Model):
    """
    Группа счетов (раздел плана счетов).
    Обеспечивает иерархическую структуру: Раздел → Подраздел → Счета.
    """
    _name = 'custom.account.group'
    _description = 'Account Group (Plan of Accounts Section)'
    _order = 'complete_code, name'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'

    # ── Identification ──────────────────────────────────────────────
    code = fields.Char(
        string='Code',
        required=True,
        size=10,
        help='Short numeric or alphanumeric code for this group (e.g. "1", "10", "101")',
    )
    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    complete_name = fields.Char(
        string='Full Name',
        compute='_compute_complete_name',
        store=True,
    )
    complete_code = fields.Char(
        string='Full Code',
        compute='_compute_complete_code',
        store=True,
        index=True,
    )

    # ── Hierarchy ────────────────────────────────────────────────────
    parent_id = fields.Many2one(
        comodel_name='custom.account.group',
        string='Parent Group',
        index=True,
        ondelete='restrict',
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(
        comodel_name='custom.account.group',
        inverse_name='parent_id',
        string='Child Groups',
    )
    level = fields.Integer(
        string='Level',
        compute='_compute_level',
        store=True,
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
        string='Account Type',
        help='Default account type for accounts in this group.',
    )
    note = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    # ── Computed counts ──────────────────────────────────────────────
    account_count = fields.Integer(
        string='Accounts',
        compute='_compute_account_count',
    )

    # ── Computes ─────────────────────────────────────────────────────
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = f'{rec.parent_id.complete_name} / {rec.name}'
            else:
                rec.complete_name = rec.name

    @api.depends('code', 'parent_id.complete_code')
    def _compute_complete_code(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_code = f'{rec.parent_id.complete_code}.{rec.code}'
            else:
                rec.complete_code = rec.code

    @api.depends('parent_id')
    def _compute_level(self):
        for rec in self:
            level = 0
            parent = rec.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            rec.level = level

    def _compute_account_count(self):
        Account = self.env['custom.account.account']
        for rec in self:
            rec.account_count = Account.search_count([('group_id', '=', rec.id)])

    # ── Constraints ──────────────────────────────────────────────────
    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive account groups.'))

    _sql_constraints = [
        ('code_parent_unique', 'UNIQUE(code, parent_id)', 'The code must be unique within the same parent group.'),
    ]

    # ── Actions ──────────────────────────────────────────────────────
    def action_view_accounts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Accounts in %s') % self.complete_name,
            'res_model': 'custom.account.account',
            'view_mode': 'list,form',
            'domain': [('group_id', '=', self.id)],
            'context': {'default_group_id': self.id},
        }
