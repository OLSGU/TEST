# custom_accounting — Odoo 19.0 Community

## Описание

Модуль расширенного бухгалтерского учёта для Odoo 19.0 Community.  
Добавляет **план счетов** с иерархией групп и **вкладку разбивки на журнальные записи** на формах инвойса и счёта.

---

## Функциональность

### 1. Группы счетов (`custom.account.group`)
- Иерархическая структура (родительские → дочерние группы)
- Поддержка произвольной вложенности (`parent_store`)
- Автоматические поля `complete_code` и `complete_name`
- Привязка к типу счёта (активы, пассивы, капитал, доходы, расходы)

### 2. План счетов (`custom.account.account`)
- Код + наименование счёта (уникальные в рамках компании)
- 15 типов счетов (согласно классификации Odoo)
- Нормальная сторона баланса (дебет/кредит)
- Флаги: reconcile (сверка), deprecated (устаревший)
- Привязка к группе плана счетов
- Линковка к стандартному `account.account` Odoo
- Теги для аналитики

### 3. Учётные периоды (`custom.account.period`)
- Месячные, квартальные, годовые периоды
- Открытие и закрытие периодов
- Автоматическая привязка строк к периоду по дате

### 4. Разбивка на журнальные записи (`custom.account.move.line`)
- Вкладка «Journal Entry Breakdown» на инвойсах и счетах
- Поля: счёт плана счетов, партнёр, дебет/кредит, валюта, период, налоги
- Кнопка **Sync Lines** — автоматический импорт из стандартных строк Odoo с сопоставлением по коду счёта
- Визуальный индикатор баланса (деб = кред)
- Предупреждение при несбалансированных строках

---

## Установка

1. Скопируйте папку `custom_accounting` в директорию `addons` вашего Odoo.
2. Перезапустите сервер Odoo.
3. Обновите список приложений: Настройки → Технические → Приложения → Обновить список.
4. Найдите "Custom Accounting" и нажмите **Установить**.

```bash
# Быстрая установка через CLI
./odoo-bin -d YOUR_DB -u custom_accounting --stop-after-init
```

---

## Структура файлов

```
custom_accounting/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── custom_account_group.py       # Группы плана счетов
│   ├── custom_account_account.py     # Счета плана счетов
│   ├── custom_account_period.py      # Учётные периоды
│   └── custom_account_move.py        # Расширение инвойса + строки записей
├── views/
│   ├── custom_account_group_views.xml
│   ├── custom_account_account_views.xml
│   ├── custom_account_period_views.xml
│   ├── custom_account_move_views.xml  # Наследование account.move + доп. вкладка
│   └── menu_views.xml
├── data/
│   ├── account_group_data.xml         # Типовые группы плана счетов
│   ├── account_type_data.xml
│   └── chart_of_accounts_data.xml     # Базовый план счетов (~40 счетов)
├── security/
│   ├── custom_accounting_security.xml
│   └── ir.model.access.csv
└── static/src/
    ├── css/custom_accounting.css
    └── js/journal_entry_widget.js
```

---

## Права доступа

| Группа | Доступ |
|--------|--------|
| `group_custom_accounting_user` | Просмотр плана счетов, разбивка на вкладке инвойса |
| `group_custom_accounting_manager` | Полный доступ: создание/редактирование счетов, групп, периодов |

---

## Меню

**Бухгалтерия → Plan of Accounts**
- Chart of Accounts
- Account Groups
- Accounting Periods
- Journal Lines (Plan)

---

## Зависимости

- `account` (стандартный модуль Odoo)
- `base_setup`

---

## Лицензия

LGPL-3
