# -*- coding: utf-8 -*-
{
    'name': 'Custom Accounting — Chart of Accounts & Journal Entries',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Extended accounting module: Chart of Accounts, Journal Entries breakdown on invoice/bill',
    'description': """
Custom Accounting Module for Odoo 19.0 Community
=================================================

Features:
- Full Chart of Accounts (план счетов) with hierarchy support
- Account types: assets, liabilities, equity, income, expenses
- Journal Entry breakdown tab on invoices and bills
- Account groups and account tags
- Accounting periods management
- Trial balance reporting
- Extended journal entry lines view inside invoice form
    """,
    'author': 'Custom Dev',
    'website': 'https://example.com',
    'depends': [
        'account',
        'base_setup',
    ],
    'data': [
        # Security
        'security/custom_accounting_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/account_group_data.xml',
        'data/account_type_data.xml',
        'data/chart_of_accounts_data.xml',

        # Views — models
        'views/custom_account_group_views.xml',
        'views/custom_account_account_views.xml',
        'views/custom_account_period_views.xml',
        'views/custom_account_move_views.xml',       # Invoice / Bill extra tab

        # Menus
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_accounting/static/src/css/custom_accounting.css',
            'custom_accounting/static/src/js/journal_entry_widget.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
