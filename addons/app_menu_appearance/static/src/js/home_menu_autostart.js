/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";

const HOME_ACTION = { type: "ir.actions.client", tag: "app_menu_appearance.home_menu" };

/**
 * В режиме "apps" при заходе на «пустой» URL (без открытого действия/меню)
 * показываем главный экран с иконками вместо приложения по умолчанию.
 */
export const homeMenuAutostartService = {
    dependencies: ["action"],
    start(env, { action }) {
        if ((session.app_menu_display_mode || "list") !== "apps") {
            return;
        }
        const hash = browser.location.hash || "";
        const hasAction = /(action|model|menu_id)=/.test(hash);
        if (hasAction) {
            return;
        }
        env.bus.addEventListener(
            "WEB_CLIENT_READY",
            () => {
                action.doAction(HOME_ACTION);
            },
            { once: true }
        );
    },
};

registry.category("services").add("app_menu_home_autostart", homeMenuAutostartService);
