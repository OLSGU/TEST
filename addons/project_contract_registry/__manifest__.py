# -*- coding: utf-8 -*-
{
    "name": "Реестр договоров и документов по проектам",
    "version": "19.0.1.0.0",
    "summary": "Учёт проектов, договоров и связанных документов (пилот)",
    "description": """
Пилотный модуль реестра договоров и документов по проектам.

Реализует базовую иерархию сущностей: Проект → Договор → Документ.
Архитектура single-company (одна компания). Поскольку официальная
локализация l10n_ru в Odoo больше не поставляется, российские реквизиты
контрагентов (ИНН/КПП/ОГРН) добавляются этим модулем прямо в res.partner.
""",
    "author": "Project Contract Registry",
    "website": "https://example.com",
    "category": "Services/Project",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/pcr_security.xml",
        "security/ir.model.access.csv",
        "security/pcr_record_rules.xml",
        "data/ir_sequence_data.xml",
        "views/res_partner_views.xml",
        "views/project_views.xml",
        "views/contract_views.xml",
        "views/document_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
