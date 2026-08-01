# -*- coding: utf-8 -*-
import base64
import ftplib
import io
import logging
from urllib.parse import quote

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Тайм-ауты сетевых операций (секунды)
_HTTP_TIMEOUT = 30
_FTP_TIMEOUT = 30


class PcrDocument(models.Model):
    _name = "pcr.document"
    _description = "Документ"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Наименование", required=True, tracking=True)
    reference = fields.Char(
        string="Рег. номер",
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("Новый"),
    )
    active = fields.Boolean(default=True)
    contract_id = fields.Many2one(
        "pcr.contract",
        string="Договор",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    project_id = fields.Many2one(
        related="contract_id.project_id",
        string="Проект",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="contract_id.partner_id",
        string="Контрагент",
        store=True,
        readonly=True,
    )
    doc_type = fields.Selection(
        selection=[
            ("contract", "Договор"),
            ("annex", "Приложение"),
            ("act", "Акт"),
            ("invoice", "Счёт"),
            ("other", "Прочее"),
        ],
        string="Тип документа",
        default="other",
        required=True,
    )
    date = fields.Date(string="Дата документа", default=fields.Date.context_today)

    # Файл, отображаемый в интерфейсе. Не хранится в БД напрямую: физически
    # содержимое лежит в выбранном бэкенде (filestore / WebDAV / FTP).
    file = fields.Binary(
        string="Файл",
        compute="_compute_file",
        inverse="_inverse_file",
        help="Содержимое хранится в бэкенде, заданном в настройках "
        "(Реестр договоров → Настройки хранилища).",
    )
    file_name = fields.Char(string="Имя файла")
    # Локальное хранилище (используется только при storage_type='filestore').
    file_data = fields.Binary(string="Файл (локально)", attachment=True, copy=False)
    # Где физически хранится файл данной записи.
    storage_type = fields.Selection(
        selection=[
            ("filestore", "Локально (filestore)"),
            ("webdav", "WebDAV / Яндекс.Диск"),
            ("ftp", "FTP / FTPS"),
        ],
        string="Хранилище",
        readonly=True,
        copy=False,
    )
    # Путь/ключ файла во внешнем хранилище (для webdav/ftp).
    storage_key = fields.Char(string="Ключ хранения", readonly=True, copy=False)
    file_size = fields.Integer(string="Размер файла, байт", readonly=True)

    state = fields.Selection(
        selection=[
            ("draft", "Черновик"),
            ("confirmed", "Подтверждён"),
            ("archived", "В архиве"),
        ],
        string="Статус",
        default="draft",
        required=True,
        tracking=True,
    )
    note = fields.Text(string="Примечание")

    # ------------------------------------------------------------------
    # Вычисление / запись файла через выбранный бэкенд
    # ------------------------------------------------------------------
    @api.depends("file_data", "storage_type", "storage_key")
    def _compute_file(self):
        for doc in self:
            if not doc.storage_type or doc.storage_type == "filestore":
                doc.file = doc.file_data
                continue
            try:
                doc.file = doc._storage_read()
            except Exception as exc:  # noqa: BLE001 - форма должна открыться
                _logger.warning(
                    "Не удалось прочитать файл документа %s из хранилища %s: %s",
                    doc.id,
                    doc.storage_type,
                    exc,
                )
                doc.file = False

    def _inverse_file(self):
        for doc in self:
            data = doc.file
            target = doc._configured_backend()

            # Очистка файла
            if not data:
                doc._storage_delete_safe()
                doc.file_data = False
                doc.storage_type = target
                doc.storage_key = False
                doc.file_size = 0
                continue

            try:
                raw = base64.b64decode(data)
            except Exception:  # noqa: BLE001
                raw = b""

            # Удаляем предыдущее содержимое, если оно лежало в другом месте
            doc._storage_delete_safe()

            if target == "filestore":
                doc.file_data = data
                doc.storage_type = "filestore"
                doc.storage_key = False
            else:
                filename = doc.file_name or ("document_%s" % (doc.id or "new"))
                key = doc._storage_write(target, filename, raw)
                doc.file_data = False
                doc.storage_type = target
                doc.storage_key = key
            doc.file_size = len(raw)

    def unlink(self):
        for doc in self:
            doc._storage_delete_safe()
        return super().unlink()

    # ------------------------------------------------------------------
    # Конфигурация бэкендов
    # ------------------------------------------------------------------
    @api.model
    def _configured_backend(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pcr_document.storage_backend", "filestore")
        )

    @api.model
    def _webdav_config(self):
        icp = self.env["ir.config_parameter"].sudo()
        return {
            "url": (icp.get_param("pcr_document.webdav_url") or "").rstrip("/"),
            "username": icp.get_param("pcr_document.webdav_username") or "",
            "password": icp.get_param("pcr_document.webdav_password") or "",
            "base_dir": (icp.get_param("pcr_document.webdav_base_dir") or "").strip("/"),
        }

    @api.model
    def _ftp_config(self):
        icp = self.env["ir.config_parameter"].sudo()
        return {
            "host": icp.get_param("pcr_document.ftp_host") or "",
            "port": int(icp.get_param("pcr_document.ftp_port") or 21),
            "username": icp.get_param("pcr_document.ftp_username") or "",
            "password": icp.get_param("pcr_document.ftp_password") or "",
            "base_dir": (icp.get_param("pcr_document.ftp_base_dir") or "").strip("/"),
            "tls": (icp.get_param("pcr_document.ftp_tls") or "").lower()
            in ("true", "1"),
        }

    # ------------------------------------------------------------------
    # Диспетчеры чтения/записи/удаления
    # ------------------------------------------------------------------
    def _storage_write(self, backend, filename, raw):
        """Записать файл в бэкенд, вернуть storage_key."""
        self.ensure_one()
        if backend == "webdav":
            return self._webdav_write(self._webdav_config(), filename, raw)
        if backend == "ftp":
            return self._ftp_write(self._ftp_config(), filename, raw)
        raise UserError(_("Неизвестный тип хранилища: %s") % backend)

    def _storage_read(self):
        self.ensure_one()
        if not self.storage_key:
            return False
        if self.storage_type == "webdav":
            return self._webdav_read(self._webdav_config(), self.storage_key)
        if self.storage_type == "ftp":
            return self._ftp_read(self._ftp_config(), self.storage_key)
        return False

    def _storage_delete_safe(self):
        """Удалить внешний файл, не прерывая транзакцию при ошибке."""
        self.ensure_one()
        if self.storage_type not in ("webdav", "ftp") or not self.storage_key:
            return
        try:
            if self.storage_type == "webdav":
                self._webdav_delete(self._webdav_config(), self.storage_key)
            elif self.storage_type == "ftp":
                self._ftp_delete(self._ftp_config(), self.storage_key)
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "Не удалось удалить файл %s из хранилища %s: %s",
                self.storage_key,
                self.storage_type,
                exc,
            )

    # ------------------------------------------------------------------
    # WebDAV (в т.ч. Яндекс.Диск)
    # ------------------------------------------------------------------
    @api.model
    def _webdav_check(self, config):
        if not config.get("url"):
            raise UserError(_("Не указан URL WebDAV."))
        import requests

        try:
            resp = requests.request(
                "PROPFIND",
                config["url"] + "/",
                auth=(config["username"], config["password"]),
                headers={"Depth": "0"},
                timeout=_HTTP_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise UserError(_("Ошибка соединения WebDAV: %s") % exc)
        if resp.status_code in (401, 403):
            raise UserError(_("WebDAV: ошибка авторизации (%s).") % resp.status_code)
        if resp.status_code >= 400:
            raise UserError(
                _("WebDAV вернул код %s при проверке.") % resp.status_code
            )
        return True

    def _webdav_write(self, config, filename, raw):
        if not config.get("url"):
            raise UserError(_("Не настроен URL WebDAV (Настройки хранилища)."))
        import requests

        auth = (config["username"], config["password"])
        segments = [s for s in config["base_dir"].split("/") if s] + [str(self.id)]

        # Создаём каталоги по уровням (MKCOL); существующие игнорируем.
        accum = config["url"]
        for seg in segments:
            accum = accum + "/" + quote(seg)
            try:
                requests.request(
                    "MKCOL", accum, auth=auth, timeout=_HTTP_TIMEOUT
                )
            except requests.RequestException as exc:
                raise UserError(_("Ошибка WebDAV (MKCOL): %s") % exc)

        key = "/".join(segments + [filename])
        remote = config["url"] + "/" + "/".join(quote(p) for p in key.split("/"))
        try:
            resp = requests.put(
                remote, data=raw, auth=auth, timeout=_HTTP_TIMEOUT
            )
        except requests.RequestException as exc:
            raise UserError(_("Ошибка WebDAV (загрузка): %s") % exc)
        if resp.status_code >= 400:
            raise UserError(
                _("WebDAV отклонил загрузку файла (код %s).") % resp.status_code
            )
        return key

    def _webdav_read(self, config, key):
        import requests

        remote = config["url"] + "/" + "/".join(quote(p) for p in key.split("/"))
        resp = requests.get(
            remote,
            auth=(config["username"], config["password"]),
            timeout=_HTTP_TIMEOUT,
        )
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return base64.b64encode(resp.content)

    def _webdav_delete(self, config, key):
        import requests

        remote = config["url"] + "/" + "/".join(quote(p) for p in key.split("/"))
        resp = requests.delete(
            remote,
            auth=(config["username"], config["password"]),
            timeout=_HTTP_TIMEOUT,
        )
        if resp.status_code not in (200, 204, 404):
            resp.raise_for_status()

    # ------------------------------------------------------------------
    # FTP / FTPS
    # ------------------------------------------------------------------
    @api.model
    def _ftp_connect(self, config):
        if not config.get("host"):
            raise UserError(_("Не указан хост FTP."))
        try:
            if config.get("tls"):
                ftp = ftplib.FTP_TLS(timeout=_FTP_TIMEOUT)
            else:
                ftp = ftplib.FTP(timeout=_FTP_TIMEOUT)
            ftp.connect(config["host"], config["port"] or 21)
            ftp.login(config["username"], config["password"])
            if config.get("tls"):
                ftp.prot_p()
            ftp.set_pasv(True)
        except (ftplib.all_errors) as exc:
            raise UserError(_("Ошибка соединения FTP: %s") % exc)
        return ftp

    @api.model
    def _ftp_check(self, config):
        ftp = self._ftp_connect(config)
        try:
            ftp.voidcmd("NOOP")
        finally:
            self._ftp_quit(ftp)
        return True

    @staticmethod
    def _ftp_quit(ftp):
        try:
            ftp.quit()
        except Exception:  # noqa: BLE001
            try:
                ftp.close()
            except Exception:  # noqa: BLE001
                pass

    @staticmethod
    def _ftp_makedirs(ftp, dirs):
        for seg in dirs:
            try:
                ftp.cwd(seg)
            except ftplib.error_perm:
                ftp.mkd(seg)
                ftp.cwd(seg)

    def _ftp_write(self, config, filename, raw):
        ftp = self._ftp_connect(config)
        try:
            dirs = [s for s in config["base_dir"].split("/") if s] + [str(self.id)]
            self._ftp_makedirs(ftp, dirs)
            ftp.storbinary("STOR " + filename, io.BytesIO(raw))
        except ftplib.all_errors as exc:
            raise UserError(_("Ошибка FTP (загрузка): %s") % exc)
        finally:
            self._ftp_quit(ftp)
        return "/".join(dirs + [filename])

    def _ftp_read(self, config, key):
        ftp = self._ftp_connect(config)
        buf = io.BytesIO()
        try:
            ftp.retrbinary("RETR " + key, buf.write)
        except ftplib.error_perm as exc:
            if str(exc).startswith("550"):  # файл не найден
                return False
            raise UserError(_("Ошибка FTP (чтение): %s") % exc)
        finally:
            self._ftp_quit(ftp)
        return base64.b64encode(buf.getvalue())

    def _ftp_delete(self, config, key):
        ftp = self._ftp_connect(config)
        try:
            ftp.delete(key)
        except ftplib.error_perm:
            pass  # уже отсутствует
        finally:
            self._ftp_quit(ftp)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("reference") or vals["reference"] == _("Новый"):
                vals["reference"] = self.env["ir.sequence"].next_by_code(
                    "pcr.document"
                ) or _("Новый")
        return super().create(vals_list)

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_archive_doc(self):
        self.write({"state": "archived"})

    def action_set_draft(self):
        self.write({"state": "draft"})
