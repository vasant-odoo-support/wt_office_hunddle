# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemplate(models.Model):
	_inherit = "product.template"

	is_printing_product = fields.Boolean("Is Printing Products?")