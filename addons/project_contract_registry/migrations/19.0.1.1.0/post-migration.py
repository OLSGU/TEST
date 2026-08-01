# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Перенос ранее загруженных файлов pcr.document на новую схему хранения.

    До версии 19.0.1.1.0 файл хранился в поле `file` (Binary, attachment=True),
    т.е. как ir.attachment с res_field='file'. Теперь локальные файлы лежат
    в поле `file_data`, а `file` стало вычисляемым. Переназначаем вложения
    и помечаем такие записи как хранящиеся локально (filestore).
    """
    if not version:
        return

    # Переназначаем существующие вложения со старого поля на новое.
    cr.execute(
        """
        UPDATE ir_attachment
           SET res_field = 'file_data'
         WHERE res_model = 'pcr.document'
           AND res_field = 'file'
        """
    )
    moved = cr.rowcount
    _logger.info("pcr.document: перенесено вложений file -> file_data: %s", moved)

    # Все существующие документы считаем хранящимися локально.
    cr.execute(
        """
        UPDATE pcr_document
           SET storage_type = 'filestore'
         WHERE storage_type IS NULL
        """
    )
