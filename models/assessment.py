# -*- coding: utf-8 -*-
from odoo import fields, models, api

class websiteLeadGeneration(models.Model):
    _name = 'assessment.assessment'
    _description = 'Assessment'
    _order = 'sequence, name'

    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char(string='Name')
    user_id = fields.Many2one("res.users")
    company_name = fields.Char(string="Company")
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
    annual_revenue = fields.Selection([
        ('0-50K', "0-50K"),
        ('50K-100K', "50K-100K"),
        ('100K-200K', "100K-200K"),
        ('200K-500K', "200K-500K"),
        ('500K-1M', "500K-1M"),
        ('1M-5M', "1M-5M"),
        ('OVER 5M', "OVER 5M")
    ], "ANNUAL REVENUE")
    referrer_type = fields.Selection([
        ('Bing', 'Bing'),
        ('Coupon', 'Coupon'),
        ('Facebook', 'Facebook'),
        ('Google', 'Google'),
        ('Instagram', 'Instagram'),
        ('LinkedIn', 'LinkedIn'),
        ('MailAdvertisement', 'Mail Advertisement'),
        ('MSN', 'MSN'),
        ('Other', 'Other'),
        ('Radio Advertisement', 'RadioAdvertisement'),
        ('Reddit', 'Reddit'),
        ('ReferralsorFriends', 'Referrals or Friends'),
        ('ReturningCustomer', 'Returning Customer'),
        ('SportsAdvertisement', 'Sports Advertisement'),
        ('TikTok', 'TikTok'),
        ('Tradeshow', 'Tradeshow'),
        ('TVAdvertisement', 'TV Advertisement'),
        ('Yahoo', 'Yahoo'),
        ('Youtube', 'Youtube'),
    ])
    no_of_leaders_report = fields.Integer(string="How many Leaders report")
    start_date = fields.Date(string="Business Start Date")
    assessment_list_ids = fields.One2many('assessment.result.line', 'assessment_id')

    @api.onchange("user_id")
    def onchnage_user_id(self):
        if self.user_id:
            self.business_phone = self.user_id.partner_id.bussiness_phone or ''
            self.email = self.user_id.partner_id.email or ''
            self.website = self.user_id.partner_id.website or ''
            self.website2 = self.user_id.partner_id.website_link or ''
            self.no_of_employee = self.user_id.partner_id.employees or ''
            self.annual_revenue = self.user_id.partner_id.annual or False
            self.no_of_leaders_report = int(self.user_id.partner_id.leaders) or 0
            self.start_date = self.user_id.partner_id.business_date or False
            self.cell_phone = self.user_id.partner_id.mobile or ''
            self.phone = self.user_id.partner_id.phone or ''
            self.mailing_address = self.user_id.partner_id.email or ''
            self.company_name = self.user_id.partner_id.company_name or ''
            self.city = self.user_id.partner_id.city or ''
            self.state_id = self.user_id.partner_id.state_id.id or False
            self.zipcode = self.user_id.partner_id.zip or ''
            self.city2 = self.user_id.partner_id.city or ''
            self.state_id2 = self.user_id.partner_id.state_id.id or False
            self.zipcode2 = self.user_id.partner_id.zip or ''
            self.name = self.user_id.name +  ' Assessment'
            self.referrer_type = self.user_id.referrer_type


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