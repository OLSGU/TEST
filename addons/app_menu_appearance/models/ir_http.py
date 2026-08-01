# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """Прокидываем персональные настройки в session_info, чтобы фронтенд
        мог применить их сразу при загрузке веб-клиента (без доп. запроса).
        """
        result = super().session_info()
        user = self.env.user
        result["app_menu_display_mode"] = user.app_menu_display_mode or "list"
        result["menu_bar_color"] = user.menu_bar_color or ""
        return result
