# -*- coding: utf-8 -*-
import logging
import werkzeug
from odoo import fields, http, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.addons.website.controllers.main import Website, QueryURL
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.http import request, route
from odoo.addons.http_routing.models.ir_http import slug
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.datastructures import OrderedMultiDict
from odoo.tools.misc import get_lang
import json
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_slides.controllers.main import WebsiteSlides

_logger = logging.getLogger(__name__)


class WebsiteSlidesHuddleCustom(WebsiteSlides):

    @http.route('/e-learning', type='http', auth='public', website=True)
    def slides_channel_all(self, slide_type=None, my=False, **post):
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels = request.env['slide.channel'].search(domain, order=order)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })
        return  request.render('wt_office_hunddle.elearning_officehuddle_template', values)

class WebsitAuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if qcontext.get('firstname') and qcontext.get('lastname'):
            qcontext['name'] = qcontext.get('firstname') + " " + qcontext.get('lastname')
        if qcontext.get('is_need_product_info') == 'on':
            qcontext['no_discount_on_product'] = True
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                    )
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'company_name', 'referrer_type', 'no_discount_on_product', 'website_link', 'bussiness_phone', 'employees', 'annual', 'leaders', 'business_date') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

class WebsitBlogPost(Website):
    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        res = super(WebsitBlogPost, self).index(**kw)
        blog_post_ids = request.env['blog.post'].search([], limit=3)
        if blog_post_ids:
            size = len(blog_post_ids)
            subList = [blog_post_ids[n:n+1] for n in range(0, size, 1)]
            res.qcontext['blog_post_ids'] = subList
        return res


class WebsiteHuddleCustom(http.Controller):
   
    @http.route('/how-it-works', type='http', auth='public', website=True)
    def web_how_works(self):
        return  request.render('wt_office_hunddle.how_it_work')

    @http.route('/customer-portal', type='http', auth='public', website=True)
    def customer_portal_office_huddle(self):
        return  request.render('wt_office_hunddle.customer_portal_officehuddle_template')

    @http.route('/graphic', type='http', auth='public', website=True)
    def graphics_office_huddle(self):
        return  request.render('wt_office_hunddle.graphic_design_form')

    @http.route('/tshirt-printing', type='http', auth='public', website=True)
    def tshirt_printing_office_huddle(self):
        return  request.render('wt_office_hunddle.t_shirt_printing_design_selection_officehuddle_template')

    @http.route('/page/assessment', type='http', auth='public', website=True)
    def assessment(self):
        all_question_ids = request.env['question.question']
        marketing_ids = all_question_ids.sudo().search([('question_type', '=', 'marketing')])
        financial_ids = all_question_ids.sudo().search([('question_type', '=', 'finance')])
        team_development_ids = all_question_ids.sudo().search([('question_type', '=', 'team_development')])
        lead_generation_ids = all_question_ids.sudo().search([('question_type', '=', 'lead_generation')])
        lead_conversion_ids = all_question_ids.sudo().search([('question_type', '=', 'lead_conversion')])
        customer_fulfillment_ids = all_question_ids.sudo().search([('question_type', '=', 'customer_fulfillment')])
        form_submission_ids = all_question_ids.sudo().search([('question_type', '=', 'form_submission')])
        vals = {
            'marketing_ids': marketing_ids,
            'financial_ids': financial_ids,
            'team_development_ids': team_development_ids,
            'lead_generation_ids': lead_generation_ids,
            'lead_conversion_ids': lead_conversion_ids,
            'customer_fulfillment_ids': customer_fulfillment_ids,
            'form_submission_ids': form_submission_ids,
        }
        return  request.render('wt_office_hunddle.assessment_tmpl',vals)

    @http.route('/assessment/output', type='http', auth='public', website=True)
    def assessment_output(self, **kw):
        quesion_ids = request.env['question.question']
        no_of_marketing_que = quesion_ids.sudo().search_count([('question_type', '=', 'marketing')])
        no_of_finance_que = quesion_ids.sudo().search_count([('question_type', '=', 'finance')])
        no_of_team_dev_que = quesion_ids.sudo().search_count([('question_type', '=', 'team_development')])
        no_of_lead_gen_que = quesion_ids.sudo().search_count([('question_type', '=', 'lead_generation')])
        no_of_lead_con_que = quesion_ids.sudo().search_count([('question_type', '=', 'lead_conversion')])
        no_of_cus_ful_que = quesion_ids.sudo().search_count([('question_type', '=', 'customer_fulfillment')])
        no_of_form_sub_que = quesion_ids.sudo().search_count([('question_type', '=', 'form_submission')])
        overall_assessment = quesion_ids.sudo().search_count([])
        if kw.get('result_id'):
            assessment_id = request.env['assessment.assessment'].sudo().search([('id', '=', kw.get('result_id'))])
            marketing = assessment_id.assessment_list_ids.filtered(
            lambda x: x.question_type == 'marketing' and x.result == 'yes')
            finance = assessment_id.assessment_list_ids.filtered(
            lambda x: x.question_type == 'finance' and x.result == 'yes')
            team_development = assessment_id.assessment_list_ids.filtered(
            lambda x: x.question_type == 'team_development' and x.result == 'yes')
            lead_generation = assessment_id.assessment_list_ids.filtered(
            lambda x: x.question_type == 'lead_generation' and x.result == 'yes')
            lead_conversion = assessment_id.assessment_list_ids.filtered(
            lambda x: x.question_type == 'lead_conversion' and x.result == 'yes')
            customer_fulfillment = assessment_id.assessment_list_ids.filtered(
            lambda x: x.question_type == 'customer_fulfillment' and x.result == 'yes')
            form_submission = assessment_id.assessment_list_ids.filtered(
            lambda x: x.question_type == 'form_submission' and x.result == 'yes')
            
            marketing_total = None
            if marketing:
                if len(marketing) < 1:
                     marketing_total = 0
                else:
                    marketing_total = round((len(marketing) / no_of_marketing_que)*100)

            finance_total = None
            if finance:
                if len(finance) < 1:
                     finance_total = 0
                else:
                    finance_total = round((len(finance) / no_of_finance_que)*100)

            team_development_total = None
            if team_development:
                if len(team_development) < 1:
                     team_development_total = 0
                else:
                    team_development_total = round((len(team_development) / no_of_team_dev_que)*100)

            lead_generation_total = None
            if lead_generation:
                if len(lead_generation) < 1:
                     lead_generation_total = 0
                else:
                    lead_generation_total = round((len(lead_generation) / no_of_lead_gen_que)*100)

            lead_conversion_total = None
            if lead_conversion:
                if len(lead_conversion) < 1:
                     lead_conversion_total = 0
                else:
                    lead_conversion_total = round((len(lead_conversion) / no_of_lead_con_que)*100)

            customer_fulfillment_total = None
            if customer_fulfillment:
                if len(customer_fulfillment) < 1:
                     customer_fulfillment_total = 0
                else:
                    customer_fulfillment_total = round((len(customer_fulfillment) / no_of_cus_ful_que)*100)

            form_submission_total = None
            if form_submission:
                if len(form_submission) < 1:
                     form_submission_total = 0
                else:
                    form_submission_total = round((len(form_submission) / no_of_form_sub_que)*100)

            total_fill_yes = len(marketing) + len(finance) + len(team_development) + len(lead_generation) + len(lead_conversion) + len(customer_fulfillment) + len(form_submission)
            overall_assessment_total = None
            if overall_assessment:
                overall_assessment_total = round((total_fill_yes / overall_assessment)*100)

            marketing_cl = None
            if marketing_total <= 50:
                marketing_cl = 'red'
            elif marketing_total <= 80:
                marketing_cl = 'orange'
            else:
                marketing_cl = 'green'
            vals = {
                'marketing': marketing_total if  marketing_total else 0,
                'finance': finance_total if  finance_total else 0,
                'team_development': team_development_total if  team_development_total else 0,
                'lead_generation': lead_generation_total if  lead_generation_total else 0,
                'lead_conversion': lead_conversion_total if  lead_conversion_total else 0,
                'customer_fulfillment': customer_fulfillment_total if  customer_fulfillment_total else 0,
                'form_submission': form_submission_total if  form_submission_total else 0,
                'marketing_cl': marketing_cl,
                'overall_assessment_total': overall_assessment_total,
            }
        return  request.render('wt_office_hunddle.assess_output',vals)

    @http.route('/assesment/submit', type='http', auth='public', website=True)
    def assessment_submit(self, **kw):

        all_questions_id = request.env['question.question'].search([]).mapped('id')
        annual_revenue = None
        if kw.get('annual') == '0-50K':
            annual_revenue = '0'
        elif kw.get('annual') == '50-100K':
            annual_revenue = '1'
        elif kw.get('annual') == '100-200K':
            annual_revenue = '2'
        elif kw.get('annual') == '200-500K':
            annual_revenue = '3'
        elif kw.get('annual') == '500-1M':
            annual_revenue = '4'
        elif kw.get('annual') == '1M-5M':
            annual_revenue = '5'
        else:
            annual_revenue = '0'

        state_id = None
        if kw.get('state'):
            state_id = request.env['res.country.state'].search([('name', '=', kw.get('state').capitalize())])
        
        state_id2 = None
        if kw.get('state2'):
            state_id2 = request.env['res.country.state'].search([('name', '=', kw.get('state2').capitalize())])
        
        name = kw.get('firstname') + ' ' + kw.get('lastname') 
        vals = {
        'company_name': kw.get('legalname'),
        'website': kw.get('website'),
        'name': name,
        'mailing_address': kw.get('mailingadd'),
        'city': kw.get('city'),
        'state_id': state_id.id if state_id else False,
        'zipcode': kw.get('zipcode'),
        'physical_address': kw.get('physicaladd'),
        'city2': kw.get('city2'),
        'state_id2': state_id2.id if state_id2 else False,
        'zipcode2': kw.get('zipcode2'),
        'email': kw.get('Email2'),
        'website2': kw.get('Website'),
        'business_phone': kw.get('businessphone'),
        'phone': kw.get('phone2'),
        'cell_phone': kw.get('cellphone'),
        'no_of_employee': kw.get('employees'),
        'annual_revenue': annual_revenue,
        'no_of_leaders_report': kw.get('leaders'),
        'start_date': kw.get('date'),
        }
        assessment = request.env['assessment.assessment'].create(vals)
        if assessment:
            question_line_ids = []
            for i in all_questions_id:
                if str(i) in kw.keys():
                    question_line_ids.append((0, 0, {
                        'name': int(i),
                        'assessment_id': assessment.id,
                        'result': kw.get(str(i))
                        }))
            if question_line_ids:
                assessment.write({'assessment_list_ids': question_line_ids})

        return request.redirect('/assessment/output?result_id=%s' %(assessment.id))
    
    @http.route('/crm/lead', type='http', auth='public', website=True)
    def web_myaccount_form(self, **kw):
        service_id = request.env['service.service'].search([('id', '=', kw.get('service'))])
        request.env['crm.lead'].create({
            'name' : kw.get('name'),
            'email_from': kw.get('email'),
            'planned_revenue': kw.get('planned_revenue'),
            'description': kw.get('description'),
            'service_id': service_id.id, 
            })
        return  request.render('wt_office_hunddle.footer_default')

    @http.route('/business-coatching', type='http', auth='public', website=True)
    def web_business_coatching(self):
        business_coatching_blog = request.env['blog.post'].search([('valid_page', '=', 'business_coatching')], limit=3)
        values ={
            'business_coatching_blog': business_coatching_blog,
        }        
        return  request.render('wt_office_hunddle.business_coatching',values)

    @http.route('/toolkit', type='http', auth='public', website=True)
    def web_toolkit(self):
        lead_generation_obj = request.env['lead.generation.resources'].search([])
        seo_obj = request.env['seo.resources'].search([])
        access_capital_obj = request.env['access.capital.resources'].search([])
        business_credit_obj = request.env['business.credit.resources'].search([])
        val ={
            'lead_generation_obj': lead_generation_obj,
            'seo_obj': seo_obj,
            'access_capital_obj': access_capital_obj,
            'business_credit_obj': business_credit_obj,
        }   
        return  request.render('wt_office_hunddle.toolkit_template',val)

    @http.route('/train-like-ceo', type='http', auth='public', website=True)
    def train_like_ceo(self):
        courses = request.env['slide.channel'].search([])
        train_ceo_blog = request.env['blog.post'].sudo().search([('valid_page', '=', 'train_like_ceo')], limit=3)
        vals ={
            'courses': courses,
            'train_ceo_blog': train_ceo_blog,
        }
        return  request.render('wt_office_hunddle.train_like_ceo',vals)

    @http.route('/erp-development', type='http', auth='public', website=True)
    def erp_development(self):
        erp_development_blog = request.env['blog.post'].search([('valid_page', '=', 'erp_development')], limit=3)
        vals = {
            'erp_development_blog': erp_development_blog,
        }
        return  request.render('wt_office_hunddle.erp_development',vals)

    @http.route('/graphic-design', type='http', auth='public', website=True)
    def graphic_design(self):
        graphic_design_blog = request.env['blog.post'].search([('valid_page', '=', 'graphic_design')], limit=3)
        vals = {
            'graphic_design_blog': graphic_design_blog,
        }
        return  request.render('wt_office_hunddle.graphic_design',vals)

    @http.route('/virtual-staffing', type='http', auth='public', website=True)
    def virtual_staffing(self):
        virtual_staffing_blog = request.env['blog.post'].search([('valid_page', '=', 'virtual_staffing')], limit=3)
        vals = {
            'virtual_staffing_blog': virtual_staffing_blog,
        }
        return  request.render('wt_office_hunddle.virtual_staffing',vals)

class WebsiteEventController(WebsiteEventController):
    def sitemap_event(env, rule, qs):
        if not qs or qs.lower() in '/events':
            yield {'loc': '/events'}

    @http.route(['''/event''', 
                '''/event/page/<int:page>''', 
                '''/events''',
                '''/events/page/<int:page>''',
                '''/event/register/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>'''], type='http', auth="public", website=True, sitemap=sitemap_event)
    def events(self, page=1, event=None, **searches):
        res = super(WebsiteEventController, self).events(page=1, **searches)
        date_lst = res.qcontext['event_ids'].mapped('date_end')
        if res.qcontext['event_ids']:
            latest = min(res.qcontext['event_ids'], key=lambda s: s.date_end.date()-datetime.today().date())
            if not request.context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                res.qcontext['event'] = latest.with_context(pricelist=pricelist.id)
            else:
                res.qcontext['event'] = latest
        else:
            res.qcontext['event'] = request.env['event.event']
        if event:
            if not request.context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                res.qcontext['event'] = event.with_context(pricelist=pricelist.id)
            else:
                res.qcontext['event'] = event
        upcomming_event_ids = res.qcontext['event_ids'] or []
        res.qcontext['upcomming_event_ids'] = upcomming_event_ids
        view_id = request.env.ref('wt_office_hunddle.event_new_hunddle').id
        return request.render(view_id, res.qcontext)
    # @http.route(['''/event', '/event/page/<int:page>', '/events', '/event/register/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>'''], type='http', auth="public", website=True, sitemap=sitemap_event)
    # def events(self, page=1, event=None, **searches):
    #     res = super(WebsiteEventController, self).events(page=1, **searches)
    #     date_lst = res.qcontext['event_ids'].mapped('date_end')
    #     if res.qcontext['event_ids']:
    #         latest = min(res.qcontext['event_ids'], key=lambda s: s.date_end.date()-datetime.today().date())
    #         if not request.context.get('pricelist'):
    #             pricelist = request.website.get_current_pricelist()
    #             res.qcontext['event'] = latest.with_context(pricelist=pricelist.id)
    #         else:
    #             res.qcontext['event'] = latest
    #     else:
    #         res.qcontext['event'] = request.env['event.event']
    #     if event:
    #         res.qcontext['event'] = event
    #     upcomming_event_ids = res.qcontext['event_ids'] or []
    #     res.qcontext['upcomming_event_ids'] = upcomming_event_ids
    #     view_id = request.env.ref('wt_office_hunddle.event_new_hunddle').id
    #     return request.render(view_id, res.qcontext)
