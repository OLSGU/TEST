# -*- coding: utf-8 -*-
{
    "name": "Мост: Договоры ↔ Бухгалтерия",
    "version": "19.0.1.0.0",
    "summary": "Связь реестра проектов/договоров со счетами (account.move)",
    "description": """
Мост между реестром договоров (project_contract_registry) и бухгалтерией
(account, Odoo Community).

Что даёт модуль:

* В счёте/счёте-фактуре (account.move) появляются поля «Договор» и «Проект».
* При выборе договора проект подтягивается автоматически.
* Договоры и проекты в счёте фильтруются по выбранному контакту (контрагенту).
* В договоре считаются суммы по связанным проведённым счетам
  (Выставлено / Осталось выставить / % выставлено), с учётом возвратов и
  приведением к валюте договора; добавлены смарт-кнопка и вкладка «Счета».

Архитектура single-company. Отдельный пакет, чтобы ядро реестра оставалось
независимым от бухгалтерии.
""",
    "author": "Project Contract Registry",
    "website": "https://example.com",
    "category": "Accounting/Accounting",
    "license": "LGPL-3",
    "depends": ["project_contract_registry", "account"],
    "data": [
        "views/account_move_views.xml",
        "views/contract_views.xml",
    ],
    "application": False,
    "installable": True,
}
