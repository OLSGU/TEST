# -*- coding: utf-8 -*-
# Odoo 19 Community — ON_NSCHFDOPPOK (КНД 1115132, версия 5.01)

import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UpdBuyer(models.Model):
    _name = 'l10n.ru.upd.buyer'
    _description = 'Файл обмена информации покупателя КНД 1115132'
    _order = 'date_info_buyer desc, id desc'

    # ---- <Файл> ----
    name = fields.Char('ИдФайл', required=True, size=255)
    version_format = fields.Char('ВерсФорм', required=True, default='5.01', size=5)
    version_program = fields.Char('ВерсПрог', size=40)

    # ---- СвУчДокОбор ----
    sender_id = fields.Char('ИдОтпр', required=True, size=46)
    receiver_id = fields.Char('ИдПол', required=True, size=46)
    edo_operator_name = fields.Char('НаимОрг оператора ЭДО', size=1000)
    edo_operator_inn = fields.Char('ИННЮЛ оператора ЭДО', size=10)
    edo_operator_eid = fields.Char('ИдЭДО оператора', size=3)

    # ---- ИнфПок ----
    knd_code = fields.Char('КНД', default='1115132', readonly=True, size=7)
    date_info_buyer = fields.Date('ДатаИнфПок', required=True, default=fields.Date.context_today)
    time_info_buyer = fields.Char('ВремИнфПок ЧЧ.ММ.СС', required=True, size=8)
    compiler_name = fields.Char('НаимЭконСубСост', required=True, size=1000)
    compiler_trust_basis = fields.Char('ОснДоверОргСост', size=120)

    # ---- ИдИнфПрод ----
    seller_file_id = fields.Char('ИдФайлИнфПр', required=True, size=255)
    seller_file_date = fields.Date('ДатаФайлИнфПр', required=True)
    seller_file_time = fields.Char('ВремФайлИнфПр ЧЧ.ММ.СС', required=True, size=8)
    electronic_signature_ids = fields.One2many(
        'l10n.ru.upd.buyer.ep', 'upd_buyer_id', 'ЭП файла продавца')

    # ---- СодФХЖ4 / КодСодОпер ----
    result_code = fields.Selection([
        ('1', '1 – Принято без расхождений'),
        ('2', '2 – Принято с расхождениями'),
        ('3', '3 – Не принято'),
    ], 'КодИтога')
    discrepancy_doc_name = fields.Char('НаимДокРасх', size=255)
    discrepancy_doc_type = fields.Selection([
        ('2', '2 – Акт'), ('3', '3 – Претензия'),
    ], 'ВидДокРасх')
    discrepancy_doc_number = fields.Char('НомДокРасх', size=255)
    discrepancy_doc_date = fields.Date('ДатаДокРасх')
    discrepancy_file_id = fields.Char('ИдФайлДокРасх', size=255)

    # ---- СвЛицПрин ----
    acceptor_type = fields.Selection([
        ('employee', 'Работник орг. покупателя'),
        ('rep_org', 'Представитель другой орг.'),
        ('individual', 'Физическое лицо'),
    ], 'Тип принявшего')
    acceptor_last_name = fields.Char('Фамилия', size=60)
    acceptor_first_name = fields.Char('Имя', size=60)
    acceptor_middle_name = fields.Char('Отчество', size=60)
    acceptor_position = fields.Char('Должность', size=128)
    acceptor_other_info = fields.Char('ИныеСвед', size=255)
    acceptor_authority_basis = fields.Char('ОснПолн принявшего', size=120)
    acceptor_org_inn = fields.Char('ИНН орг. принципала', size=10)
    acceptor_org_name = fields.Char('Наим. орг. принципала', size=1000)

    text_info_ids = fields.One2many(
        'l10n.ru.upd.buyer.textinfo', 'upd_buyer_id', 'ТекстИнф')

    # ---- СвПерВыр ----
    payment_account = fields.Char('НомСч', size=20)
    payment_bank_bik = fields.Char('БИК банка', size=9)
    payment_bank_name = fields.Char('Наим. банка', size=1000)
    payment_corr_account = fields.Char('КорСч', size=20)
    payment_okato = fields.Char('ОКТМО', size=11)
    payment_kbk = fields.Char('КБК', size=20)
    payment_obligation_number = fields.Char('УчНомДенОбяз', size=22)
    payment_order = fields.Char('ОчерПлат', size=1)
    payment_type = fields.Selection([
        ('0', '0 – Электронно'), ('4', '4 – Почтовым переводом'),
    ], 'ВидПлат')

    # ---- Подписанты ----
    signatory_ids = fields.One2many(
        'l10n.ru.upd.buyer.signatory', 'upd_buyer_id', 'Подписанты')

    # ---- Служебные ----
    state = fields.Selection([
        ('draft', 'Черновик'), ('ready', 'Готов'), ('sent', 'Отправлен'),
    ], default='draft', string='Статус', required=True)
    xml_file = fields.Binary('XML файл', attachment=True, readonly=True)
    xml_filename = fields.Char('Имя XML файла', readonly=True)
    invoice_id = fields.Many2one(
        'account.move', 'Счёт-фактура',
        domain=[('move_type', 'in', ['in_invoice', 'in_refund'])],
        ondelete='set null')
    company_id = fields.Many2one(
        'res.company', 'Организация', required=True,
        default=lambda self: self.env.company)
    notes = fields.Text('Примечания')

    # ---- Constraints ----

    @api.constrains('version_format')
    def _check_version_format(self):
        for r in self:
            if r.version_format != '5.01':
                raise ValidationError(_('ВерсФорм должна быть 5.01'))

    @api.constrains('sender_id')
    def _check_sender(self):
        for r in self:
            if r.sender_id and not (4 <= len(r.sender_id) <= 46):
                raise ValidationError(_('ИдОтпр: 4–46 символов'))

    @api.constrains('receiver_id')
    def _check_receiver(self):
        for r in self:
            if r.receiver_id and not (4 <= len(r.receiver_id) <= 46):
                raise ValidationError(_('ИдПол: 4–46 символов'))

    @api.constrains('time_info_buyer')
    def _check_time_buyer(self):
        p = re.compile(r'^([01]\d|2[0-3])\.[0-5]\d\.[0-5]\d$')
        for r in self:
            if r.time_info_buyer and not p.match(r.time_info_buyer):
                raise ValidationError(_('ВремИнфПок: формат ЧЧ.ММ.СС'))

    @api.constrains('seller_file_time')
    def _check_time_seller(self):
        p = re.compile(r'^([01]\d|2[0-3])\.[0-5]\d\.[0-5]\d$')
        for r in self:
            if r.seller_file_time and not p.match(r.seller_file_time):
                raise ValidationError(_('ВремФайлИнфПр: формат ЧЧ.ММ.СС'))

    @api.constrains('payment_obligation_number')
    def _check_obligation(self):
        for r in self:
            if r.payment_obligation_number and len(r.payment_obligation_number) != 22:
                raise ValidationError(_('УчНомДенОбяз: ровно 22 знака'))

    # ---- Actions ----

    def action_set_ready(self):
        self.write({'state': 'ready'})

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_generate_xml(self):
        self.ensure_one()
        return self.env['l10n.ru.upd.buyer.xml'].generate(self)

    def action_view_xml(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}'
                   f'&field=xml_file&download=true&filename={self.xml_filename}',
            'target': 'new',
        }


class UpdBuyerEP(models.Model):
    _name = 'l10n.ru.upd.buyer.ep'
    _description = 'ЭП файла продавца'
    _order = 'sequence'

    upd_buyer_id = fields.Many2one('l10n.ru.upd.buyer', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    signature_value = fields.Text('Значение ЭП', required=True)


class UpdBuyerTextInfo(models.Model):
    _name = 'l10n.ru.upd.buyer.textinfo'
    _description = 'ТекстИнф'
    _order = 'sequence'

    upd_buyer_id = fields.Many2one('l10n.ru.upd.buyer', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    identifier = fields.Char('Идентификатор', required=True, size=50)
    value = fields.Char('Значение', required=True, size=2000)
