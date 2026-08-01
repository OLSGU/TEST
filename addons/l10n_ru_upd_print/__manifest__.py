# -*- coding: utf-8 -*-
{
    'name': 'Russia UPD Print (Печатная форма УПД)',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Печатная форма УПД (универсальный передаточный документ) для входящих и исходящих счетов',
    'author': 'Custom',
    'depends': ['account'],
    'data': [
        'report/upd_report.xml',
        'report/upd_template.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
