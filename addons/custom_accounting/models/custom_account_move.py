# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class CustomAccountMoveLine(models.Model):
    """
    Строка журнальной записи, привязанная к плану счетов.
    Заполняется автоматически при подтверждении инвойса/счёта
    исходя из проводок, сформированных по правилам локализации.
    """
    _name = 'custom.account.move.line'
    _description = 'Custom Journal Entry Line'
    _order = 'sequence, id'

    # ── Links ────────────────────────────────────────────────────────
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        required=True,
        ondelete='cascade',
        index=True,
        auto_join=True,
    )
    move_name = fields.Char(
        related='move_id.name',
        string='Entry Number',
        store=True,
    )
    odoo_move_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Source Odoo Line',
        help='Ссылка на стандартную строку account.move.line.',
        index=True,
        ondelete='set null',
    )
    custom_account_id = fields.Many2one(
        comodel_name='custom.account.account',
        string='Account (Plan)',
        index=True,
    )

    # ── Sort ─────────────────────────────────────────────────────────
    sequence = fields.Integer(string='Sequence', default=10)

    # ── Date & Period ─────────────────────────────────────────────────
    date = fields.Date(string='Date', related='move_id.date', store=True, index=True)
    period_id = fields.Many2one(
        comodel_name='custom.account.period',
        string='Period',
        compute='_compute_period_id',
        store=True,
        index=True,
    )

    # ── Description ───────────────────────────────────────────────────
    name = fields.Char(string='Label', default='/')
    ref = fields.Char(string='Reference')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', index=True)
    odoo_account_code = fields.Char(string='Odoo Account Code', readonly=True)
    odoo_account_name = fields.Char(string='Odoo Account Name', readonly=True)

    # ── Amounts ───────────────────────────────────────────────────────
    debit = fields.Monetary(string='Debit', currency_field='company_currency_id', default=0.0)
    credit = fields.Monetary(string='Credit', currency_field='company_currency_id', default=0.0)
    balance = fields.Monetary(
        string='Balance', compute='_compute_balance', store=True,
        currency_field='company_currency_id',
    )
    amount_currency = fields.Monetary(string='Amount in Currency', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency')
    company_id = fields.Many2one(comodel_name='res.company', related='move_id.company_id', store=True)
    company_currency_id = fields.Many2one(comodel_name='res.currency', related='move_id.currency_id', store=True)

    # ── State ─────────────────────────────────────────────────────────
    move_state = fields.Selection(related='move_id.state', string='Entry State', store=True, index=True)
    reconciled = fields.Boolean(string='Reconciled', default=False, readonly=True)

    # ── Line type ─────────────────────────────────────────────────────
    line_type = fields.Selection(
        selection=[
            ('receivable', 'Receivable / Payable'),
            ('tax',        'Tax'),
            ('product',    'Product / Service'),
            ('other',      'Other'),
        ],
        string='Line Type',
        default='other',
        readonly=True,
    )

    # ── Analytic ──────────────────────────────────────────────────────
    analytic_distribution = fields.Json(string='Analytic Distribution')
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='custom_move_line_tax_rel',
        column1='line_id',
        column2='tax_id',
        string='Taxes',
    )
    note = fields.Text(string='Internal Notes')

    # ── Computes ──────────────────────────────────────────────────────
    @api.depends('debit', 'credit')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.debit - rec.credit

    @api.depends('date', 'company_id')
    def _compute_period_id(self):
        Period = self.env['custom.account.period']
        for rec in self:
            if not rec.date:
                rec.period_id = False
                continue
            period = Period.search([
                ('date_start', '<=', rec.date),
                ('date_stop', '>=', rec.date),
                ('company_id', '=', rec.company_id.id),
                ('state', '=', 'draft'),
            ], limit=1)
            rec.period_id = period


# ─────────────────────────────────────────────────────────────────────────────
def _resolve_line_type(account):
    """Тип строки по типу стандартного счёта Odoo."""
    if not account:
        return 'other'
    atype = account.account_type
    if atype in ('asset_receivable', 'liability_payable'):
        return 'receivable'
    if atype in ('income', 'income_other', 'expense',
                 'expense_depreciation', 'expense_direct_cost'):
        return 'product'
    if atype in ('asset_current', 'liability_current'):
        return 'tax'
    return 'other'


def _sort_key(line):
    """Порядок строк: дебиторка/кредиторка → продукты → налоги → прочее."""
    atype = line.account_id.account_type if line.account_id else ''
    if atype in ('asset_receivable', 'liability_payable'):
        return (0, line.id)
    if atype in ('income', 'income_other', 'expense',
                 'expense_depreciation', 'expense_direct_cost'):
        return (1, line.id)
    if atype in ('asset_current', 'liability_current'):
        return (2, line.id)
    return (3, line.id)


# ─────────────────────────────────────────────────────────────────────────────
class AccountMoveCustomExt(models.Model):
    """
    Расширение account.move.
    Автоматически заполняет custom_journal_line_ids при action_post()
    из стандартных проводок, созданных по правилам локализации.
    """
    _inherit = 'account.move'

    custom_journal_line_ids = fields.One2many(
        comodel_name='custom.account.move.line',
        inverse_name='move_id',
        string='Custom Journal Lines',
        copy=False,
    )
    custom_total_debit = fields.Monetary(
        string='Total Debit', compute='_compute_custom_totals', currency_field='currency_id',
    )
    custom_total_credit = fields.Monetary(
        string='Total Credit', compute='_compute_custom_totals', currency_field='currency_id',
    )
    custom_balance = fields.Monetary(
        string='Net Balance', compute='_compute_custom_totals', currency_field='currency_id',
    )
    custom_is_balanced = fields.Boolean(string='Balanced', compute='_compute_custom_totals')
    custom_lines_synced = fields.Boolean(string='Lines Synced', default=False, copy=False)

    @api.depends('custom_journal_line_ids.debit', 'custom_journal_line_ids.credit')
    def _compute_custom_totals(self):
        for move in self:
            lines = move.custom_journal_line_ids
            d = sum(lines.mapped('debit'))
            c = sum(lines.mapped('credit'))
            move.custom_total_debit = d
            move.custom_total_credit = c
            move.custom_balance = d - c
            move.custom_is_balanced = abs(d - c) < 0.01

    # ── Hooks ─────────────────────────────────────────────────────────
    def action_post(self):
        """
        После подтверждения Odoo формирует account.move.line по правилам
        локализации (НДС, счета доходов/расходов, дебиторка/кредиторка).
        Мы читаем эти строки и заполняем custom_journal_line_ids.
        """
        res = super().action_post()
        invoices = self.filtered(
            lambda m: m.move_type in (
                'out_invoice', 'out_refund',
                'in_invoice', 'in_refund',
            )
        )
        if invoices:
            invoices._sync_custom_lines_from_localization()
        return res

    def button_draft(self):
        """При сбросе в черновик очищаем custom lines — они устаревают."""
        res = super().button_draft()
        self.filtered(
            lambda m: m.move_type in (
                'out_invoice', 'out_refund',
                'in_invoice', 'in_refund',
            )
        )._clear_custom_lines()
        return res

    # ── Core ──────────────────────────────────────────────────────────
    def _sync_custom_lines_from_localization(self):
        """
        Синхронизирует custom journal lines из стандартных account.move.line.

        Сопоставление счёта (в порядке приоритета):
        1. Точное совпадение по коду счёта (custom.account.account.code == account.account.code)
        2. Совпадение по типу счёта (account_type) — первый подходящий кастомный счёт
        3. Строка создаётся без кастомного счёта (пользователь может заполнить вручную)
        """
        CustomLine = self.env['custom.account.move.line']
        CustomAccount = self.env['custom.account.account']

        company_ids = self.mapped('company_id').ids

        # Кэш: (code, company_id) → custom_account
        all_ca = CustomAccount.search([
            ('company_id', 'in', company_ids),
            ('deprecated', '=', False),
        ])
        by_code = {}
        by_type = {}
        for ca in all_ca:
            k_code = (ca.code, ca.company_id.id)
            k_type = (ca.account_type, ca.company_id.id)
            by_code.setdefault(k_code, ca)
            by_type.setdefault(k_type, ca)

        for move in self:
            # Очистить старые custom lines
            move.custom_journal_line_ids.sudo().unlink()

            # Получить стандартные проводки, отсортированные по смысловому типу
            odoo_lines = sorted(move.line_ids, key=_sort_key)

            vals_list = []
            for seq, line in enumerate(odoo_lines, start=10):
                std_code = line.account_id.code or ''
                cid = move.company_id.id

                # 1. По коду
                ca = by_code.get((std_code, cid))
                # 2. По типу счёта
                if not ca and line.account_id:
                    ca = by_type.get((line.account_id.account_type, cid))

                vals_list.append({
                    'move_id':            move.id,
                    'odoo_move_line_id':  line.id,
                    'custom_account_id':  ca.id if ca else False,
                    'sequence':           seq,
                    'name':               line.name or line.account_id.name or '/',
                    'ref':                move.ref or '',
                    'partner_id':         line.partner_id.id if line.partner_id else False,
                    'odoo_account_code':  std_code,
                    'odoo_account_name':  line.account_id.name or '',
                    'debit':              line.debit,
                    'credit':             line.credit,
                    'currency_id':        line.currency_id.id if line.currency_id else False,
                    'amount_currency':    line.amount_currency,
                    'reconciled':         line.reconciled,
                    'analytic_distribution': line.analytic_distribution or False,
                    'line_type':          _resolve_line_type(line.account_id),
                })

            if vals_list:
                CustomLine.create(vals_list)
                _logger.info(
                    'custom_accounting: %d lines synced for move %s (%s)',
                    len(vals_list), move.name, move.move_type,
                )

            move.custom_lines_synced = True

    def _clear_custom_lines(self):
        for move in self:
            move.custom_journal_line_ids.sudo().unlink()
            move.custom_lines_synced = False

    # ── Manual resync ─────────────────────────────────────────────────
    def action_sync_custom_lines(self):
        """Ручная ресинхронизация (после обновления плана счетов)."""
        posted = self.filtered(lambda m: m.state == 'posted')
        if posted:
            posted._sync_custom_lines_from_localization()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type':    'success',
                'title':   _('Synced'),
                'message': _('%d document(s) updated.') % len(posted),
                'sticky': False,
            },
        }
