/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

/**
 * Кнопка в systray для повторного открытия полноэкранного лаунчера.
 * Регистрируется только в режиме отображения меню "apps".
 */
export class AppLauncherSystray extends Component {
    static template = "app_menu_appearance.AppLauncherSystray";
    static props = {};

    setup() {
        this.launcher = useService("app_launcher");
    }

    onClick() {
        this.launcher.toggle();
    }
}

if ((session.app_menu_display_mode || "list") === "apps") {
    registry.category("systray").add(
        "app_launcher",
        { Component: AppLauncherSystray },
        { sequence: 1 }
    );
}
