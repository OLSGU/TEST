# -*- coding: utf-8 -*-
{
    'name': 'Russia UPD Buyer (ON_NSCHFDOPPOK)',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'ЭДО: файл обмена информации покупателя (КНД 1115132)',
    'author': 'Custom',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/upd_buyer_views.xml',
        'views/account_move_views.xml',
        'views/upd_buyer_menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
