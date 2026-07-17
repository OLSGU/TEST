# -*- coding: utf-8 -*-
{
    "name": "Отображение меню приложений",
    "version": "19.0.1.0.0",
    "summary": (
        "Персональные настройки интерфейса: вид меню приложений "
        "(список / иконки как в Enterprise) и цвет верхней панели меню"
    ),
    "description": """
Модуль добавляет персональные (на уровне пользователя) настройки внешнего вида:

* **Вид меню приложений** — переключение между отображением меню списком и
  форматом крупных иконок на основном экране (как в Odoo Enterprise).
* **Цвет верхней полосы меню** — выбор произвольного цвета верхней навигационной
  панели.

Настройки хранятся на модели ``res.users`` и применяются индивидуально для
каждого пользователя. Изменить их можно в разделе *Настройки → Предпочтения*
(или через меню пользователя → «Мои настройки»).
""",
    "author": "Project Contract Registry",
    "website": "https://example.com",
    "category": "Tools",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "app_menu_appearance/static/src/scss/app_menu_appearance.scss",
            "app_menu_appearance/static/src/js/app_menu_appearance_service.js",
            "app_menu_appearance/static/src/js/menu_bar_color_field.js",
            "app_menu_appearance/static/src/js/menu_bar_color_field.xml",
        ],
    },
    "application": False,
    "installable": True,
}
