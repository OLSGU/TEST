/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// Цвет по умолчанию (используется как значение палитры, если поле пустое).
const DEFAULT_COLOR = "#714B67";

/**
 * Поле выбора цвета: нативный <input type="color"> + отображение HEX-значения
 * и кнопка сброса к цвету темы. Регистрируется как виджет "menu_bar_color".
 */
export class MenuBarColorField extends Component {
    static template = "app_menu_appearance.MenuBarColorField";
    static props = { ...standardFieldProps };

    get value() {
        return this.props.record.data[this.props.name] || "";
    }

    get pickerColor() {
        return this.value || DEFAULT_COLOR;
    }

    onColorChange(ev) {
        this.props.record.update({ [this.props.name]: ev.target.value });
    }

    onReset() {
        this.props.record.update({ [this.props.name]: false });
    }
}

export const menuBarColorField = {
    component: MenuBarColorField,
    displayName: "Цвет панели меню",
    supportedTypes: ["char"],
};

registry.category("fields").add("menu_bar_color", menuBarColorField);
