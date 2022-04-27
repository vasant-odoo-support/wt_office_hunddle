# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductQuantity(models.Model):
    _name = "product.quantity"
    qty = fields.Integer("Quantity")
    product_tmpl_id = fields.Many2one('product.template')


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    is_screen_printing = fields.Boolean('Show Screen Printing')
    


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_printing_product = fields.Boolean("Is Printing?")
    is_merchandise_product = fields.Boolean("Is Merchandise?")
    product_qty_ids = fields.One2many('product.quantity', 'product_tmpl_id')


    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        """Override for website, where we want to:
            - take the website pricelist if no pricelist is set
            - apply the b2b/b2c setting to the result

        This will work when adding website_id to the context, which is done
        automatically when called from routes with website=True.
        """
        self.ensure_one()

        current_website = False

        if self.env.context.get('website_id'):
            current_website = self.env['website'].get_current_website()
            if not pricelist:
                pricelist = current_website.get_current_pricelist()

        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        if self.env.context.get('website_id'):
            partner = self.env.user.partner_id
            company_id = current_website.company_id
            product = self.env['product.product'].browse(combination_info['product_id']) or self

            tax_display = self.env.user.has_group('account.group_show_line_subtotals_tax_excluded') and 'total_excluded' or 'total_included'
            Fpos_sudo = self.env['account.fiscal.position'].sudo()
            fpos_id = Fpos_sudo.with_context(force_company=company_id.id).get_fiscal_position(partner.id)
            taxes = Fpos_sudo.browse(fpos_id).map_tax(product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id), product, partner)

            # The list_price is always the price of one.
            quantity_1 = 1
            combination_info['price'] = self.env['account.tax']._fix_tax_included_price_company(combination_info['price'], product.sudo().taxes_id, taxes, company_id)
            price = taxes.compute_all(combination_info['price'], pricelist.currency_id, quantity_1, product, partner)[tax_display]
            if pricelist.discount_policy == 'without_discount':
                combination_info['list_price'] = self.env['account.tax']._fix_tax_included_price_company(combination_info['list_price'], product.sudo().taxes_id, taxes, company_id)
                list_price = taxes.compute_all(combination_info['list_price'], pricelist.currency_id, quantity_1, product, partner)[tax_display]
            else:
                list_price = price
            has_discounted_price = pricelist.currency_id.compare_amounts(list_price, price) == 1

            combination_info.update(
                price=price,
                list_price=list_price,
                has_discounted_price=has_discounted_price,
            )
            if self.is_printing_product:
                combination_info.update(
                    price=(price * add_qty)
                )
        return combination_info