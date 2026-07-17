/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";

/**
 * Состояние и логика полноэкранного лаунчера приложений.
 *
 * В режиме отображения меню "apps" лаунчер открывается на домашнем экране
 * (когда ещё не открыто ни одно действие) и по кнопке в systray. Список
 * приложений с иконками берётся из штатного menu-сервиса Odoo.
 */
export const appLauncherService = {
    dependencies: ["menu"],
    start(env, { menu }) {
        const isAppsMode = (session.app_menu_display_mode || "list") === "apps";
        // Если в URL уже есть открытое действие/модель — значит мы не на
        // «домашнем» экране, автозапуск лаунчера не нужен.
        const hash = browser.location.hash || "";
        const hasAction = /(action|model|menu_id)=/.test(hash);

        const state = reactive({
            open: isAppsMode && !hasAction,
        });

        return {
            state,
            get apps() {
                return menu.getApps();
            },
            open() {
                state.open = true;
            },
            close() {
                state.open = false;
            },
            toggle() {
                state.open = !state.open;
            },
            selectApp(app) {
                state.open = false;
                menu.selectMenu(app);
            },
        };
    },
};

registry.category("services").add("app_launcher", appLauncherService);
