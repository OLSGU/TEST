# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Выбор бэкенда хранения файлов документов реестра (pcr.document)
    pcr_storage_backend = fields.Selection(
        selection=[
            ("filestore", "Локально (filestore Odoo)"),
            ("webdav", "WebDAV / Яндекс.Диск"),
            ("ftp", "FTP / FTPS"),
        ],
        string="Хранилище документов",
        default="filestore",
        config_parameter="pcr_document.storage_backend",
        help="Куда сохранять файлы документов реестра. Влияет только на "
        "модель pcr.document и на вновь загружаемые/изменяемые файлы.",
    )

    # --- WebDAV / Яндекс.Диск ---
    pcr_webdav_url = fields.Char(
        string="URL WebDAV",
        config_parameter="pcr_document.webdav_url",
        help="Базовый адрес WebDAV. Для Яндекс.Диска: https://webdav.yandex.ru",
    )
    pcr_webdav_username = fields.Char(
        string="Пользователь WebDAV",
        config_parameter="pcr_document.webdav_username",
    )
    pcr_webdav_password = fields.Char(
        string="Пароль WebDAV",
        config_parameter="pcr_document.webdav_password",
        help="Для Яндекс.Диска используйте пароль приложения.",
    )
    pcr_webdav_base_dir = fields.Char(
        string="Каталог WebDAV",
        default="odoo/pcr_documents",
        config_parameter="pcr_document.webdav_base_dir",
    )

    # --- FTP / FTPS ---
    pcr_ftp_host = fields.Char(
        string="Хост FTP",
        config_parameter="pcr_document.ftp_host",
    )
    pcr_ftp_port = fields.Integer(
        string="Порт FTP",
        default=21,
        config_parameter="pcr_document.ftp_port",
    )
    pcr_ftp_username = fields.Char(
        string="Пользователь FTP",
        config_parameter="pcr_document.ftp_username",
    )
    pcr_ftp_password = fields.Char(
        string="Пароль FTP",
        config_parameter="pcr_document.ftp_password",
    )
    pcr_ftp_base_dir = fields.Char(
        string="Каталог FTP",
        default="pcr_documents",
        config_parameter="pcr_document.ftp_base_dir",
    )
    pcr_ftp_tls = fields.Boolean(
        string="Использовать FTPS (TLS)",
        config_parameter="pcr_document.ftp_tls",
    )

    def action_pcr_test_storage(self):
        """Проверить соединение с выбранным внешним хранилищем.

        Тестирует ещё не сохранённые значения формы, чтобы можно было
        проверить реквизиты до нажатия «Сохранить».
        """
        self.ensure_one()
        Document = self.env["pcr.document"]
        if self.pcr_storage_backend == "webdav":
            config = {
                "url": (self.pcr_webdav_url or "").rstrip("/"),
                "username": self.pcr_webdav_username or "",
                "password": self.pcr_webdav_password or "",
                "base_dir": (self.pcr_webdav_base_dir or "").strip("/"),
            }
            Document._webdav_check(config)
        elif self.pcr_storage_backend == "ftp":
            config = {
                "host": self.pcr_ftp_host or "",
                "port": self.pcr_ftp_port or 21,
                "username": self.pcr_ftp_username or "",
                "password": self.pcr_ftp_password or "",
                "base_dir": (self.pcr_ftp_base_dir or "").strip("/"),
                "tls": bool(self.pcr_ftp_tls),
            }
            Document._ftp_check(config)
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
