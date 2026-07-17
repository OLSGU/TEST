/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

const HOME_ACTION = { type: "ir.actions.client", tag: "app_menu_appearance.home_menu" };

/**
 * Кнопка «Главное меню» в systray — возвращает на экран с иконками приложений.
 * Регистрируется только в режиме отображения меню "apps".
 */
export class HomeMenuButton extends Component {
    static template = "app_menu_appearance.HomeMenuButton";
    static props = {};

    setup() {
        this.action = useService("action");
    }

    onClick() {
        this.action.doAction(HOME_ACTION);
    }
}

if ((session.app_menu_display_mode || "list") === "apps") {
    registry.category("systray").add(
        "app_menu_home",
        { Component: HomeMenuButton },
        { sequence: 1 }
    );
}
