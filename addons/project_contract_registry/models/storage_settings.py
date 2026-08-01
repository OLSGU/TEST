# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Параметры хранятся в ir.config_parameter под этими ключами.
_PARAMS = {
    "backend": "pcr_document.storage_backend",
    "webdav_url": "pcr_document.webdav_url",
    "webdav_username": "pcr_document.webdav_username",
    "webdav_password": "pcr_document.webdav_password",
    "webdav_base_dir": "pcr_document.webdav_base_dir",
    "ftp_host": "pcr_document.ftp_host",
    "ftp_port": "pcr_document.ftp_port",
    "ftp_username": "pcr_document.ftp_username",
    "ftp_password": "pcr_document.ftp_password",
    "ftp_base_dir": "pcr_document.ftp_base_dir",
    "ftp_tls": "pcr_document.ftp_tls",
}


class PcrStorageSettings(models.TransientModel):
    """Отдельный визард настроек хранилища документов реестра.

    Намеренно НЕ наследует res.config.settings, чтобы не вмешиваться в
    общесистемную страницу настроек (она использует одну модель
    res.config.settings, и отдельный primary-вид для неё ломает UI).
    Значения читаются/пишутся напрямую в ir.config_parameter.
    """

    _name = "pcr.storage.settings"
    _description = "Настройки хранилища документов"

    backend = fields.Selection(
        selection=[
            ("filestore", "Локально (filestore Odoo)"),
            ("webdav", "WebDAV / Яндекс.Диск"),
            ("ftp", "FTP / FTPS"),
        ],
        string="Хранилище документов",
        default="filestore",
        required=True,
        help="Куда сохранять файлы документов реестра. Влияет только на "
        "модель pcr.document и на вновь загружаемые/изменяемые файлы.",
    )

    # --- WebDAV / Яндекс.Диск ---
    webdav_url = fields.Char(
        string="URL WebDAV",
        help="Базовый адрес WebDAV. Для Яндекс.Диска: https://webdav.yandex.ru",
    )
    webdav_username = fields.Char(string="Пользователь WebDAV")
    webdav_password = fields.Char(
        string="Пароль WebDAV",
        help="Для Яндекс.Диска используйте пароль приложения.",
    )
    webdav_base_dir = fields.Char(string="Каталог WebDAV")

    # --- FTP / FTPS ---
    ftp_host = fields.Char(string="Хост FTP")
    ftp_port = fields.Integer(string="Порт FTP", default=21)
    ftp_username = fields.Char(string="Пользователь FTP")
    ftp_password = fields.Char(string="Пароль FTP")
    ftp_base_dir = fields.Char(string="Каталог FTP")
    ftp_tls = fields.Boolean(string="Использовать FTPS (TLS)")

    # ------------------------------------------------------------------
    # Загрузка текущих значений из ir.config_parameter
    # ------------------------------------------------------------------
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        icp = self.env["ir.config_parameter"].sudo()
        res["backend"] = icp.get_param(_PARAMS["backend"], "filestore")
        res["webdav_url"] = icp.get_param(_PARAMS["webdav_url"], "")
        res["webdav_username"] = icp.get_param(_PARAMS["webdav_username"], "")
        res["webdav_password"] = icp.get_param(_PARAMS["webdav_password"], "")
        res["webdav_base_dir"] = icp.get_param(
            _PARAMS["webdav_base_dir"], "odoo/pcr_documents"
        )
        res["ftp_host"] = icp.get_param(_PARAMS["ftp_host"], "")
        res["ftp_port"] = int(icp.get_param(_PARAMS["ftp_port"]) or 21)
        res["ftp_username"] = icp.get_param(_PARAMS["ftp_username"], "")
        res["ftp_password"] = icp.get_param(_PARAMS["ftp_password"], "")
        res["ftp_base_dir"] = icp.get_param(_PARAMS["ftp_base_dir"], "pcr_documents")
        res["ftp_tls"] = (icp.get_param(_PARAMS["ftp_tls"]) or "").lower() in (
            "true",
            "1",
        )
        return res

    # ------------------------------------------------------------------
    # Сохранение
    # ------------------------------------------------------------------
    def action_save(self):
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param(_PARAMS["backend"], self.backend or "filestore")
        icp.set_param(_PARAMS["webdav_url"], self.webdav_url or "")
        icp.set_param(_PARAMS["webdav_username"], self.webdav_username or "")
        icp.set_param(_PARAMS["webdav_password"], self.webdav_password or "")
        icp.set_param(_PARAMS["webdav_base_dir"], self.webdav_base_dir or "")
        icp.set_param(_PARAMS["ftp_host"], self.ftp_host or "")
        icp.set_param(_PARAMS["ftp_port"], str(self.ftp_port or 21))
        icp.set_param(_PARAMS["ftp_username"], self.ftp_username or "")
        icp.set_param(_PARAMS["ftp_password"], self.ftp_password or "")
        icp.set_param(_PARAMS["ftp_base_dir"], self.ftp_base_dir or "")
        icp.set_param(_PARAMS["ftp_tls"], "True" if self.ftp_tls else "False")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Настройки хранилища"),
                "message": _("Сохранено."),
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    # ------------------------------------------------------------------
    # Проверка подключения (по текущим, ещё не сохранённым значениям)
    # ------------------------------------------------------------------
    def action_test(self):
        self.ensure_one()
        document = self.env["pcr.document"]
        if self.backend == "webdav":
            document._webdav_check(
                {
                    "url": (self.webdav_url or "").rstrip("/"),
                    "username": self.webdav_username or "",
                    "password": self.webdav_password or "",
                    "base_dir": (self.webdav_base_dir or "").strip("/"),
                }
            )
        elif self.backend == "ftp":
            document._ftp_check(
                {
                    "host": self.ftp_host or "",
                    "port": self.ftp_port or 21,
                    "username": self.ftp_username or "",
                    "password": self.ftp_password or "",
                    "base_dir": (self.ftp_base_dir or "").strip("/"),
                    "tls": bool(self.ftp_tls),
                }
            )
        else:
            raise UserError(
                _("Для локального хранилища (filestore) проверка не требуется.")
            )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Хранилище"),
                "message": _("Подключение успешно установлено."),
                "type": "success",
                "sticky": False,
            },
        }
