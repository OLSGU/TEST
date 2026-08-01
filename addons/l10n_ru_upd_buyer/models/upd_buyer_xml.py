# -*- coding: utf-8 -*-
import base64
from lxml import etree
from odoo import models, _
from odoo.exceptions import UserError


def _d(d):
    if not d:
        return ''
    return d.strftime('%d.%m.%Y') if hasattr(d, 'strftime') else str(d)

def _opt(el, attr, val):
    if val:
        el.set(attr, str(val))


class UpdBuyerXml(models.AbstractModel):
    _name = 'l10n.ru.upd.buyer.xml'
    _description = 'Генератор XML ON_NSCHFDOPPOK'

    def generate(self, r):
        xml_bytes = self._build(r)
        fname = f'{r.name}.xml'
        r.write({
            'xml_file': base64.b64encode(xml_bytes),
            'xml_filename': fname,
            'state': 'ready',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=l10n.ru.upd.buyer&id={r.id}'
                   f'&field=xml_file&download=true&filename={fname}',
            'target': 'new',
        }

    def _build(self, r):
        root = etree.Element('Файл')
        root.set('ИдФайл', r.name or '')
        root.set('ВерсФорм', r.version_format or '5.01')
        _opt(root, 'ВерсПрог', r.version_program)

        sv = etree.SubElement(root, 'СвУчДокОбор')
        sv.set('ИдОтпр', r.sender_id or '')
        sv.set('ИдПол', r.receiver_id or '')
        if r.edo_operator_inn:
            op = etree.SubElement(sv, 'СвОЭДОтпр')
            op.set('НаимОрг', r.edo_operator_name or '')
            op.set('ИННЮЛ', r.edo_operator_inn or '')
            op.set('ИдЭДО', r.edo_operator_eid or '')

        ip = etree.SubElement(root, 'ИнфПок')
        ip.set('КНД', '1115132')
        ip.set('ДатаИнфПок', _d(r.date_info_buyer))
        ip.set('ВремИнфПок', r.time_info_buyer or '')
        ip.set('НаимЭконСубСост', r.compiler_name or '')
        _opt(ip, 'ОснДоверОргСост', r.compiler_trust_basis)

        iip = etree.SubElement(ip, 'ИдИнфПрод')
        iip.set('ИдФайлИнфПр', r.seller_file_id or '')
        iip.set('ДатаФайлИнфПр', _d(r.seller_file_date))
        iip.set('ВремФайлИнфПр', r.seller_file_time or '')
        for ep in r.electronic_signature_ids:
            etree.SubElement(iip, 'ЭП').text = ep.signature_value or ''

        sod = etree.SubElement(ip, 'СодФХЖ4')
        svp = etree.SubElement(sod, 'СвПрин')
        if r.result_code:
            ks = etree.SubElement(svp, 'КодСодОпер')
            ks.set('КодИтога', r.result_code)
            _opt(ks, 'НаимДокРасх', r.discrepancy_doc_name)
            _opt(ks, 'ВидДокРасх', r.discrepancy_doc_type)
            _opt(ks, 'НомДокРасх', r.discrepancy_doc_number)
            if r.discrepancy_doc_date:
                ks.set('ДатаДокРасх', _d(r.discrepancy_doc_date))
            _opt(ks, 'ИдФайлДокРасх', r.discrepancy_file_id)

        if r.acceptor_type:
            sl = etree.SubElement(svp, 'СвЛицПрин')
            self._acceptor(sl, r)

        for ti in r.text_info_ids:
            te = etree.SubElement(svp, 'ТекстИнф')
            te.set('Идентиф', ti.identifier or '')
            te.set('Значен', ti.value or '')

        if r.payment_account or r.payment_bank_bik:
            pv = etree.SubElement(ip, 'СвПерВыр')
            _opt(pv, 'НомСч', r.payment_account)
            _opt(pv, 'БИК', r.payment_bank_bik)
            _opt(pv, 'НаимБанк', r.payment_bank_name)
            _opt(pv, 'КорСч', r.payment_corr_account)
            _opt(pv, 'ОКТМО', r.payment_okato)
            _opt(pv, 'КБК', r.payment_kbk)
            _opt(pv, 'УчНомДенОбяз', r.payment_obligation_number)
            _opt(pv, 'ОчерПлат', r.payment_order)
            _opt(pv, 'ВидПлат', r.payment_type)

        if not r.signatory_ids:
            raise UserError(_('Необходимо добавить хотя бы одного подписанта'))
        for sig in r.signatory_ids:
            self._signatory(ip, sig)

        return etree.tostring(root, xml_declaration=True,
                              encoding='windows-1251', pretty_print=True)

    def _fio(self, parent, ln, fn, mn):
        f = etree.SubElement(parent, 'ФИО')
        f.set('Фамилия', ln or '')
        f.set('Имя', fn or '')
        _opt(f, 'Отчество', mn)

    def _acceptor(self, parent, r):
        if r.acceptor_type == 'employee':
            e = etree.SubElement(parent, 'РабОргПок')
            e.set('Должность', r.acceptor_position or '')
            e.set('ОснПолн', r.acceptor_authority_basis or '')
            _opt(e, 'ИныеСвед', r.acceptor_other_info)
            self._fio(e, r.acceptor_last_name, r.acceptor_first_name, r.acceptor_middle_name)
        elif r.acceptor_type == 'rep_org':
            il = etree.SubElement(parent, 'ИнЛицо')
            p = etree.SubElement(il, 'ПредОргПрин')
            p.set('Должность', r.acceptor_position or '')
            p.set('ОснПолн', r.acceptor_authority_basis or '')
            _opt(p, 'ИННЮЛ', r.acceptor_org_inn)
            _opt(p, 'НаимОрг', r.acceptor_org_name)
            _opt(p, 'ИныеСвед', r.acceptor_other_info)
            self._fio(p, r.acceptor_last_name, r.acceptor_first_name, r.acceptor_middle_name)
        elif r.acceptor_type == 'individual':
            il = etree.SubElement(parent, 'ИнЛицо')
            fz = etree.SubElement(il, 'ФизЛицо')
            _opt(fz, 'ИныеСвед', r.acceptor_other_info)
            self._fio(fz, r.acceptor_last_name, r.acceptor_first_name, r.acceptor_middle_name)

    def _signatory(self, parent, sig):
        pod = etree.SubElement(parent, 'Подписант')
        pod.set('ОблПолн', sig.authority_scope or '')
        pod.set('Статус', sig.status or '')
        pod.set('ОснПолн', sig.authority_basis or '')
        _opt(pod, 'ОснПолнОрг', sig.authority_basis_org)
        if sig.signatory_type == 'fl':
            fl = etree.SubElement(pod, 'ФЛ')
            _opt(fl, 'ИННФЛ', sig.fl_inn)
            _opt(fl, 'ИныеСвед', sig.fl_other_info)
            self._fio(fl, sig.last_name, sig.first_name, sig.middle_name)
        elif sig.signatory_type == 'ip':
            ip = etree.SubElement(pod, 'ИП')
            ip.set('ИННФЛ', sig.ip_inn or '')
            _opt(ip, 'СвГосРегИП', sig.ip_reg_certificate)
            _opt(ip, 'ИныеСвед', sig.ip_other_info)
            self._fio(ip, sig.last_name, sig.first_name, sig.middle_name)
        elif sig.signatory_type == 'ul':
            ul = etree.SubElement(pod, 'ЮЛ')
            ul.set('ИННЮЛ', sig.ul_inn or '')
            _opt(ul, 'НаимОрг', sig.ul_org_name)
            ul.set('Должн', sig.ul_position or '')
            _opt(ul, 'ИныеСвед', sig.ul_other_info)
            self._fio(ul, sig.last_name, sig.first_name, sig.middle_name)
