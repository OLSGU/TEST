/** @odoo-module **/

/*
 * HairFormula — Assistant Block widget
 * =====================================
 * Bound to every `.s_hairformula_assistant` instance on the page.
 *
 * Flow:
 *   1. On start: fetch product.tag list, render the cloud
 *   2. User clicks a pill / types in search → debounced refresh
 *   3. Refresh calls /hairformula/assistant/recommend, re-renders preview
 *
 * Uses native fetch + JSON-RPC envelope (framework-agnostic — works on
 * Odoo 14 through 19 without import-path concerns).
 */

import publicWidget from "@web/legacy/js/public/public_widget";

/* ---------- helpers ---------- */

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
}

async function rpc(url, params = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: params,
            id: Math.floor(Math.random() * 1e9),
        }),
    });
    const data = await response.json();
    if (data.error) {
        throw new Error(data.error.message || 'RPC error');
    }
    return data.result;
}

/* ---------- widget ---------- */

publicWidget.registry.HairFormulaAssistant = publicWidget.Widget.extend({
    selector: '.s_hairformula_assistant',
    events: {
        'click .hf-tag-pill': '_onTagClick',
        'input .hf-search-input': '_onSearchInput',
    },

    init() {
        this._super(...arguments);
        this.selectedTagIds = new Set();
        this.searchText = '';
        this._searchTimer = null;
        this.allTags = [];
    },

    async start() {
        await this._super(...arguments);
        try {
            await this._loadTags();
            await this._refresh();
        } catch (err) {
            console.error('[HairFormula Assistant] init failed:', err);
            const cloud = this.el.querySelector('.hf-tag-cloud');
            if (cloud) {
                cloud.innerHTML = '<span class="hf-empty">Не удалось загрузить теги.</span>';
            }
        }
    },

    /* ---- data ---- */

    async _loadTags() {
        this.allTags = await rpc('/hairformula/assistant/tags');
        const cloud = this.el.querySelector('.hf-tag-cloud');
        if (!cloud) return;
        if (!this.allTags.length) {
            cloud.innerHTML = '<span class="hf-empty">Теги ещё не созданы. Добавьте их в бэкенде Odoo.</span>';
            return;
        }
        cloud.innerHTML = this.allTags.map(t =>
            `<button type="button" class="hf-tag-pill" data-tag-id="${t.id}">${escapeHtml(t.name)}</button>`
        ).join('');
    },

    async _fetchRecommendations() {
        return rpc('/hairformula/assistant/recommend', {
            tag_ids: Array.from(this.selectedTagIds),
            search_text: this.searchText,
            limit: 6,
        });
    },

    /* ---- events ---- */

    _onTagClick(ev) {
        const pill = ev.currentTarget;
        const id = parseInt(pill.dataset.tagId, 10);
        if (this.selectedTagIds.has(id)) {
            this.selectedTagIds.delete(id);
            pill.classList.remove('hf-tag-pill--active');
        } else {
            this.selectedTagIds.add(id);
            pill.classList.add('hf-tag-pill--active');
        }
        this._refresh();
    },

    _onSearchInput(ev) {
        this.searchText = ev.target.value || '';
        clearTimeout(this._searchTimer);
        this._searchTimer = setTimeout(() => this._refresh(), 300);
    },

    /* ---- rendering ---- */

    async _refresh() {
        const cards = this.el.querySelector('.hf-preview-cards');
        if (cards) cards.classList.add('hf-loading');
        try {
            const products = await this._fetchRecommendations();
            this._renderSelectedChips();
            this._renderCards(products);
        } catch (err) {
            console.error('[HairFormula Assistant] recommend failed:', err);
            if (cards) {
                cards.innerHTML = '<div class="hf-empty-state">Не удалось загрузить рекомендации.</div>';
            }
        } finally {
            if (cards) cards.classList.remove('hf-loading');
        }
    },

    _renderSelectedChips() {
        const container = this.el.querySelector('.hf-selected-chips');
        if (!container) return;
        const selected = this.allTags.filter(t => this.selectedTagIds.has(t.id));
        if (!selected.length) {
            container.innerHTML = '<span class="hf-empty">Выберите состояние волос</span>';
            return;
        }
        container.innerHTML = selected.map(t =>
            `<span class="hf-chip">${escapeHtml(t.name)}</span>`
        ).join('');
    },

    _renderCards(products) {
        const grid = this.el.querySelector('.hf-preview-cards');
        if (!grid) return;
        if (!products.length) {
            grid.innerHTML = '<div class="hf-empty-state">Под выбранные критерии товаров не нашлось.</div>';
            return;
        }
        grid.innerHTML = products.map(p => {
            const price = `${Number(p.price).toFixed(2)} ${escapeHtml(p.currency)}`;
            return `
                <a href="${escapeHtml(p.url)}" class="hf-product-card">
                    <div class="hf-product-image">
                        <img src="${escapeHtml(p.image_url)}" alt="${escapeHtml(p.name)}" loading="lazy"/>
                    </div>
                    <div class="hf-product-name">${escapeHtml(p.name)}</div>
                    <div class="hf-product-price">${price}</div>
                </a>
            `;
        }).join('');
    },
});

export default publicWidget.registry.HairFormulaAssistant;
