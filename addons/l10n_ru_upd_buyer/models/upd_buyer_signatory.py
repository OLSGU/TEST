# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UpdBuyerSignatory(models.Model):
    _name = 'l10n.ru.upd.buyer.signatory'
    _description = 'Подписант файла информации покупателя'
    _order = 'sequence'

    upd_buyer_id = fields.Many2one('l10n.ru.upd.buyer', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)

    authority_scope = fields.Selection([
        ('1', '1 – За подписание счётов-фактур'),
        ('2', '2 – За оформление операции'),
        ('3', '3 – За подписание и оформление'),
    ], 'ОблПолн', required=True)

    status = fields.Selection([
        ('3', '3 – Работник орг. покупателя'),
        ('4', '4 – Работник орг.-составителя'),
        ('5', '5 – Работник иной уполн. орг.'),
        ('6', '6 – Уполн. физическое лицо'),
    ], 'Статус', required=True)

    authority_basis = fields.Char('ОснПолн', required=True, size=255)
    authority_basis_org = fields.Char('ОснПолнОрг', size=255)

    signatory_type = fields.Selection([
        ('fl', 'Физическое лицо (ФЛ)'),
        ('ip', 'Индивидуальный предприниматель (ИП)'),
        ('ul', 'Юридическое лицо (ЮЛ)'),
    ], 'Тип подписанта', required=True, default='fl')

    last_name = fields.Char('Фамилия', required=True, size=60)
    first_name = fields.Char('Имя', required=True, size=60)
    middle_name = fields.Char('Отчество', size=60)

    # ФЛ
    fl_inn = fields.Char('ИННФЛ', size=12)
    fl_other_info = fields.Char('ИныеСвед (ФЛ)', size=255)

    # ИП
    ip_inn = fields.Char('ИННФЛ (ИП)', size=12)
    ip_reg_certificate = fields.Char('СвГосРегИП', size=100)
    ip_other_info = fields.Char('ИныеСвед (ИП)', size=255)

    # ЮЛ
    ul_inn = fields.Char('ИННЮЛ', size=10)
    ul_org_name = fields.Char('НаимОрг', size=1000)
    ul_position = fields.Char('Должн', size=128)
    ul_other_info = fields.Char('ИныеСвед (ЮЛ)', size=255)

    @api.constrains('ip_inn', 'signatory_type')
    def _check_ip(self):
        p = re.compile(r'^([0-9][1-9]|[1-9][0-9])[0-9]{10}$')
        for r in self:
            if r.signatory_type == 'ip':
                if not r.ip_inn:
                    raise ValidationError(_('ИННФЛ обязателен для ИП'))
                if not p.match(r.ip_inn):
                    raise ValidationError(_('ИННФЛ (ИП): 12 цифр'))

    @api.constrains('ul_inn', 'ul_position', 'signatory_type')
    def _check_ul(self):
        p = re.compile(r'^([0-9][1-9]|[1-9][0-9])[0-9]{8}$')
        for r in self:
            if r.signatory_type == 'ul':
                if not r.ul_inn:
                    raise ValidationError(_('ИННЮЛ обязателен для ЮЛ'))
                if not p.match(r.ul_inn):
                    raise ValidationError(_('ИННЮЛ: 10 цифр'))
                if not r.ul_position:
                    raise ValidationError(_('Должность обязательна для ЮЛ'))

    @api.depends('last_name', 'first_name', 'signatory_type')
    def _compute_display_name(self):
        labels = dict(self._fields['signatory_type'].selection)
        for r in self:
            r.display_name = (
                f'{r.last_name or ""} {r.first_name or ""} '
                f'[{labels.get(r.signatory_type, "")}]'
            ).strip()
