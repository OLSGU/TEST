# -*- coding: utf-8 -*-
"""
Расширение account.move — кнопка «Создать УПД покупателя»
на форме входящего счёта-фактуры.
"""
import uuid
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    upd_buyer_ids = fields.One2many(
        'l10n.ru.upd.buyer', 'invoice_id',
        string='УПД покупателя',
    )
    upd_buyer_count = fields.Integer(
        compute='_compute_upd_buyer_count',
        string='Кол-во УПД',
    )

    @api.depends('upd_buyer_ids')
    def _compute_upd_buyer_count(self):
        for rec in self:
            rec.upd_buyer_count = len(rec.upd_buyer_ids)

    def action_create_upd_buyer(self):
        """Создать файл информации покупателя на основании счёта."""
        self.ensure_one()

        if self.move_type not in ('in_invoice', 'in_refund'):
            raise UserError(_('УПД покупателя создаётся только для входящих счетов-фактур.'))

        now = datetime.now()
        company = self.company_id
        partner = self.partner_id  # продавец

        # ИНН покупателя (наша компания) и продавца (контрагент)
        buyer_inn = company.vat or ''
        seller_inn = partner.vat or ''

        # Убираем префикс RU если есть
        if buyer_inn.upper().startswith('RU'):
            buyer_inn = buyer_inn[2:]
        if seller_inn.upper().startswith('RU'):
            seller_inn = seller_inn[2:]

        # Формируем ИдФайл по правилам ФНС:
        # ON_NSCHFDOPPOK_ИННотпр_ИННпол_YYYYMMDD_GUID
        date_str = now.strftime('%Y%m%d')
        guid = str(uuid.uuid4()).upper()
        file_id = f'ON_NSCHFDOPPOK_{buyer_inn}_{seller_inn}_{date_str}_{guid}'
        # Обрезаем до 255 символов если вдруг длиннее
        file_id = file_id[:255]

        # Время в формате ЧЧ.ММ.СС
        time_str = now.strftime('%H.%M.%S')

        # Наименование покупателя (составителя файла)
        compiler_name = company.name or ''

        # Данные для ИдИнфПрод — заполняем из имеющихся данных счёта
        # Если у счёта есть ref (номер документа продавца) — используем
        seller_ref = self.ref or self.name or ''

        vals = {
            'name': file_id,
            'version_format': '5.01',
            'version_program': 'Odoo 19',
            'date_info_buyer': now.date(),
            'time_info_buyer': time_str,
            'compiler_name': compiler_name,
            'seller_file_id': seller_ref,
            'seller_file_date': self.invoice_date or now.date(),
            'seller_file_time': time_str,
            'invoice_id': self.id,
            'company_id': company.id,
            'state': 'draft',
            # Заполняем платёжные реквизиты из банковских счетов компании
            'payment_bank_name': company.bank_ids[:1].bank_id.name if company.bank_ids else '',
            'payment_account': company.bank_ids[:1].acc_number if company.bank_ids else '',
        }

        upd = self.env['l10n.ru.upd.buyer'].create(vals)

        # Если у компании есть директор/подписант — добавим автоматически
        # В Odoo Community нет поля director, добавим пустого подписанта-заглушку
        # чтобы пользователь видел что нужно заполнить
        self.env['l10n.ru.upd.buyer.signatory'].create({
            'upd_buyer_id': upd.id,
            'authority_scope': '3',   # За подписание и оформление
            'status': '3',            # Работник организации покупателя
            'authority_basis': 'Устав',
            'signatory_type': 'ul',
            'last_name': '',
            'first_name': '',
            'ul_inn': buyer_inn[:10] if len(buyer_inn) >= 10 else buyer_inn,
            'ul_org_name': company.name or '',
            'ul_position': 'Руководитель',
        })

        # Открываем созданный документ
        return {
            'type': 'ir.actions.act_window',
            'name': _('УПД покупателя'),
            'res_model': 'l10n.ru.upd.buyer',
            'res_id': upd.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_upd_buyer(self):
        """Открыть список УПД покупателя по этому счёту."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('УПД покупателя'),
            'res_model': 'l10n.ru.upd.buyer',
            'view_mode': 'list,form',
            'domain': [('invoice_id', '=', self.id)],
            'context': {'default_invoice_id': self.id},
        }
