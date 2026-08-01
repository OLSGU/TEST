# -*- coding: utf-8 -*-
{
    "name": "Реестр договоров и документов по проектам",
    "version": "19.0.1.2.0",
    "summary": "Учёт проектов, договоров и связанных документов (пилот)",
    "description": """
Пилотный модуль реестра договоров и документов по проектам.

Реализует базовую иерархию сущностей: Проект → Договор → Документ.
Архитектура single-company (одна компания). Реквизиты контрагентов
(ИНН/КПП) берутся из стандартного res.partner; для российских полей
рекомендуется установить локализацию l10n_ru.
""",
    "author": "Project Contract Registry",
    "website": "https://example.com",
    "category": "Services/Project",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/project_views.xml",
        "views/contract_views.xml",
        "views/document_views.xml",
        "views/storage_settings_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
