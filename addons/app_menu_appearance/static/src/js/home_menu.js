/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Главный экран с иконками приложений — клиентское действие (реальная страница
 * в области контента, а не оверлей). Аналог домашнего меню Odoo Enterprise.
 *
 * Список приложений с иконками берётся из штатного menu-сервиса; выбор плитки
 * открывает соответствующее приложение.
 */
export class HomeMenu extends Component {
    static template = "app_menu_appearance.HomeMenu";
    static props = ["*"];

    setup() {
        this.menuService = useService("menu");
        this.state = useState({ query: "" });
    }

    get apps() {
        const apps = this.menuService.getApps();
        const query = this.state.query.trim().toLowerCase();
        if (!query) {
            return apps;
        }
        return apps.filter((app) => (app.name || "").toLowerCase().includes(query));
    }

    /** Источник иконки приложения (учитывает разные форматы webIconData). */
    iconSrc(app) {
        const data = app.webIconData;
        if (!data) {
            return false;
        }
        if (data.startsWith("data:") || data.startsWith("/")) {
            return data;
        }
        return "data:image/png;base64," + data;
    }

    onSelect(app) {
        this.menuService.selectMenu(app);
    }
}

registry.category("actions").add("app_menu_appearance.home_menu", HomeMenu);
