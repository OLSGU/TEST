/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

/**
 * Применяет персональные настройки внешнего вида (цвет верхней панели и режим
 * отображения меню приложений) к корню документа. Значения приходят из
 * session_info (см. models/ir_http.py), поэтому доступны сразу при загрузке.
 */
export function applyAppMenuAppearance() {
    const root = document.documentElement;
    const body = document.body;

    // --- Цвет верхней полосы меню ---
    const color = session.menu_bar_color;
    if (color) {
        root.style.setProperty("--app-menu-bar-color", color);
        body.classList.add("o_app_menu_custom_color");
    } else {
        root.style.removeProperty("--app-menu-bar-color");
        body.classList.remove("o_app_menu_custom_color");
    }

    // --- Режим отображения меню приложений ---
    const mode = session.app_menu_display_mode || "list";
    body.classList.toggle("o_app_menu_display_apps", mode === "apps");
    body.classList.toggle("o_app_menu_display_list", mode === "list");
}

export const appMenuAppearanceService = {
    start() {
        applyAppMenuAppearance();
        return { apply: applyAppMenuAppearance };
    },
};

registry.category("services").add("app_menu_appearance", appMenuAppearanceService);
