# -*- coding: utf-8 -*-
from odoo import fields, models

class websiteLeadGeneration(models.Model):
    _name = 'assessment.assessment'
    _description = 'Assessment'
    _order = 'sequence, name'

    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char(string='Name')
    company_name = fields.Char(string="Company", required=True)
    website = fields.Char(string="Website")
    website2 = fields.Char(string="Website 2")
    mailing_address = fields.Char(string="Mailing Address")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string='State')
    zipcode = fields.Char(string="Zip")
    physical_address = fields.Char(string="Physical Address")
    city2 = fields.Char(string="City")
    state_id2 = fields.Many2one("res.country.state", string='State')
    zipcode2 = fields.Char(string="Zip")
    email = fields.Char(string='Email')
    business_phone = fields.Char(string="Business Phone")
    cell_phone = fields.Char(string="Cell Phone")
    phone = fields.Char(string="Phone")
    no_of_employee = fields.Char(string="How many Employee company have")
    annual_revenue = fields.Selection(string="Annual Revenue", selection=[
        ('0', '0-50K'),
        ('1', '50-100K'),
        ('2', '100-200K'),
        ('3', '200-500K'),
        ('4', '500k-1M'),
        ('5', '1M-5M'),
        ('6', 'OVER 5M')
    ])
    no_of_leaders_report = fields.Integer(string="How many Leaders report")
    start_date = fields.Date(string="Business Start Date")
    assessment_list_ids = fields.One2many('assessment.result.line', 'assessment_id')


class MarketingSystem(models.Model):
    _name = 'question.question'
    _description = 'Question'
    _order = 'sequence, name'

    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Text('Question',required=True)
    yes_popup = fields.Text(string='Yes Popup Value')
    no_popup = fields.Text(string='No Popup Value')
    question_type = fields.Selection(
        string='Question Type',
        selection=[('marketing', 'Marketing System'), 
                ('finance', 'Financial System'),
                ('team_development', 'Team Development System'),
                ('lead_generation', 'Lead Generation System'),
                ('lead_conversion', 'Lead Conversion System'),
                ('customer_fulfillment', 'Customer Fulfillment System'),
                ('form_submission', 'Form Submission')]
    )
    result = fields.Selection(string='Result',selection=[('yes', 'Yes'),('no', 'No'),],required=False)

class assessmentResultline(models.Model):
    _name = 'assessment.result.line'
    _description = 'Assessment Result Line'
    _order = 'sequence, name'

    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Many2one('question.question', string='Name')
    result = fields.Selection(string='Result',selection=[('yes', 'Yes'),('no', 'No'),],required=False)
    assessment_id=fields.Many2one('assessment.assessment')
    question_type = fields.Selection(
        string='Question Type',
        selection=[('marketing', 'Marketing System'), 
                ('finance', 'Financial System'),
                ('team_development', 'Team Development System'),
                ('lead_generation', 'Lead Generation System'),
                ('lead_conversion', 'Lead Conversion System'),
                ('customer_fulfillment', 'Customer Fulfillment System'),
                ('form_submission', 'Form Submission')],
        related="name.question_type", store=True
    )