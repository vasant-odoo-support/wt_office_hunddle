# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

AVAILABLE_PRIORITIES = [
    ('0', 'Bad'),
    ('1', 'Low'),
    ('2', 'Medium'),
    ('3', 'High'),
    ('4', 'Very High'),
    ('5', 'Excellent'),
]

class websiteLeadGeneration(models.Model):
	_name = 'lead.generation.resources'
	_description = 'Lead Generation Resources'

	name = fields.Char(string="Name", required=True)
	image = fields.Binary(string="Image")
	description = fields.Text(string='Description')
	priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True, default=AVAILABLE_PRIORITIES[0][0])
	url = fields.Char(string="Website Url")

class websiteSEO(models.Model):
	_name = 'seo.resources'
	_description = 'SEO Resources'

	name = fields.Char(string="Name", required=True)
	seo_image = fields.Binary(string="Image")
	seo_description = fields.Text(string='Description')
	seo_priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True, default=AVAILABLE_PRIORITIES[0][0])
	seo_url = fields.Char(string="Website Url")

class websiteCapital(models.Model):
	_name = 'access.capital.resources'
	_description = 'Access To Capital Resources'

	name = fields.Char(string="Name", required=True)
	capital_image = fields.Binary(string="Image")
	capital_description = fields.Text(string='Description')
	capital_priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True, default=AVAILABLE_PRIORITIES[0][0])
	capital_url = fields.Char(string="Website Url")

class websiteBusiness(models.Model):
	_name = 'business.credit.resources'
	_description = 'Business Credit Resources'

	name = fields.Char(string="Name", required=True)
	business_image = fields.Binary(string="Image")
	business_description = fields.Text(string='Description')
	business_priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True, default=AVAILABLE_PRIORITIES[0][0])
	business_url = fields.Char(string="Website Url")