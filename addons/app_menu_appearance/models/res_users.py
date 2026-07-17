# -*- coding: utf-8 -*-
from odoo import fields, models

# Цвет по умолчанию верхней панели Odoo (фирменный «сливовый»). Пустое значение
# поля означает «использовать цвет темы», поэтому это лишь ориентир для UI.
DEFAULT_MENU_BAR_COLOR = "#714B67"


class ResUsers(models.Model):
    """Персональные настройки внешнего вида меню приложений.

    Поля хранятся на пользователе, поэтому вид меню и цвет верхней панели
    настраиваются индивидуально каждым пользователем в своих предпочтениях.
    """

    _inherit = "res.users"

    app_menu_display_mode = fields.Selection(
        selection=[
            ("list", "Список"),
            ("apps", "Иконки на основном экране (как Enterprise)"),
        ],
        string="Вид меню приложений",
        default="list",
        required=True,
        help=(
            "Способ отображения меню приложений для этого пользователя: "
            "компактным списком или крупными иконками на основном экране."
        ),
    )
    menu_bar_color = fields.Char(
        string="Цвет верхней панели меню",
        help=(
            "Цвет верхней навигационной панели в формате HEX (например, "
            "#714B67). Оставьте пустым, чтобы использовать цвет темы."
        ),
    )

    # Разрешаем обычным пользователям читать и изменять эти поля в собственных
    # предпочтениях (без прав администратора).
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            "app_menu_display_mode",
            "menu_bar_color",
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            "app_menu_display_mode",
            "menu_bar_color",
        ]
