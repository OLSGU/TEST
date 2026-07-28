from odoo import http
from odoo.http import request


class HairFormulaAssistantController(http.Controller):
    """
    JSON-RPC endpoints powering the Assistant Block snippet.

    The frontend widget calls these to fetch the tag cloud and to refresh
    product recommendations as the user picks tags / types in the search.
    """

    @http.route(
        '/hairformula/assistant/tags',
        type='json', auth='public', website=True, methods=['POST'],
    )
    def list_tags(self):
        """Return all product tags for the cloud (id + name)."""
        tags = request.env['product.tag'].sudo().search([], order='name')
        return [{'id': t.id, 'name': t.name} for t in tags]

    @http.route(
        '/hairformula/assistant/recommend',
        type='json', auth='public', website=True, methods=['POST'],
    )
    def recommend(self, tag_ids=None, category_id=None, search_text='', limit=6):
        """
        Return published, sellable products matching the chosen filters.

        Parameters
        ----------
        tag_ids : list[int]
            Selected product.tag IDs (matches products having ANY of them).
        category_id : int, optional
            Restrict to a product.public.category — backend supports it even
            though the current UI shows tags only; lets us add a category
            selector later without changing the API.
        search_text : str
            Free-text fuzzy match against product name / sale description.
        limit : int
            Max products to return (default 6).

        Returns
        -------
        list[dict] — { id, name, price, currency, image_url, url, tag_names }
        """
        tag_ids = tag_ids or []
        limit = max(1, min(int(limit or 6), 24))

        domain = [
            ('is_published', '=', True),
            ('sale_ok', '=', True),
        ]
        if tag_ids:
            domain.append(('product_tag_ids', 'in', tag_ids))
        if category_id:
            domain.append(('public_categ_ids', 'in', [int(category_id)]))
        if search_text:
            text = search_text.strip()
            if text:
                domain += ['|',
                           ('name', 'ilike', text),
                           ('description_sale', 'ilike', text)]

        products = request.env['product.template'].sudo().search(domain, limit=limit)
        currency_symbol = request.website.currency_id.symbol or '€'

        return [{
            'id': p.id,
            'name': p.name,
            'price': p.list_price,
            'currency': currency_symbol,
            'image_url': f'/web/image/product.template/{p.id}/image_512',
            'url': p.website_url,
            'tag_names': p.product_tag_ids.mapped('name'),
        } for p in products]
