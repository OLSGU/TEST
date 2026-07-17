/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Полноэкранная сетка иконок приложений (аналог домашнего экрана Enterprise).
 * Всегда смонтирован (main_components), но отрисовывается только когда
 * state.open === true.
 */
export class AppLauncher extends Component {
    static template = "app_menu_appearance.AppLauncher";
    static props = {};

    setup() {
        this.launcher = useService("app_launcher");
        this.state = useState(this.launcher.state);
    }

    get apps() {
        return this.launcher.apps;
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
        this.launcher.selectApp(app);
    }

    onClose() {
        this.launcher.close();
    }
}

registry.category("main_components").add("AppLauncher", { Component: AppLauncher });
