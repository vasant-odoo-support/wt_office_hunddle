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
from odoo.addons.auth_signup.models.res_users import SignupError
import ast
import base64
from odoo import http
from odoo.tools.mimetypes import guess_mimetype


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
    @http.route(['/get/video/details'], type='json', auth="public", methods=['POST'], website=True)
    def get_video_data(self, res_id=False, model=False, size=False, res_field=False, **kw):
        video_data = None
        if res_id and model and res_field and size:
            query = """select id from ir_attachment
                where res_model=%s and
                res_id=%s and
                res_field=%s"""
            request.env.cr.execute(query, (model, res_id, res_field,))
            attachment_ids = request.env.cr.fetchall()
            if attachment_ids:
                attachment_ids = [t[0] for t in attachment_ids]
                datas = request.env['ir.attachment'].sudo().browse(attachment_ids)
                if datas and len(datas) == 1:
                    return {
                        'name': datas.name or datas.dispay_name,
                        'id': datas.id,
                        'type': datas.mimetype,
                    }
                elif datas:
                    if size[-2:] in ('Kb', 'kb'):
                        div = 1024
                    elif size[-2:] in ('Mb', 'mb'):
                        div = 1024 * 1024
                    elif size[-5:] in ('bytes', 'Bytes'):
                        div = 1
                        size = size[:-3]
                    else:
                        return video_data

                    for d in datas:
                        if float(size[:-3]) == round(d.file_size / div, 2):
                            video_data = {
                                'name': d.name or d.dispay_name,
                                'id': d.id,
                                'type': d.mimetype,
                            }
                            break
        return video_data

    def check_get_mimetype(self, file_data, filename):
        if filename.split(".")[-1] != "mp4":
            return False
        mimetype = guess_mimetype(file_data)
        if mimetype == "application/octet-stream":
            mimetype = "video/mp4"
        return mimetype

    @http.route('/submit-graphic-info', type='http', auth='public', website=True, methods=["POST"], csrf=False,)
    def submit_graphic_form(self, **kw):
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.redirect('/web/login')
        project_obj = request.env['project.project']
        project = project_obj.sudo().search([('partner_id', '=', request.env.user.partner_id.id)])

        graphic = False
        video = False
        design_type = False
        if 'graphic' in kw and kw['graphic'] == 'graphic':
            graphic = True
            design_type = 'graphic'
        if 'video' in kw and kw['video'] == 'video':
            video = True
            design_type = 'video'

        if not project:
            project_vals = {
                'name': request.env.user.name + " Design",
                'partner_id': request.env.user.partner_id.id,
                'privacy_visibility': 'portal',
            }
            project = project_obj.sudo().create(project_vals)

        item_name = ''
        size = ''
        if 'items' in kw and kw['items'] == 'item0':
            item_name = 'Logo'
            size = ""

        if graphic and 'items' in kw and kw['items'] == 'item1':
            item_name = 'BUSINESS CARD'
            if kw['item1'] == '0':
                size = '2" x 3.5" U.S Standard'
            if kw['item1'] == '1':
                size = '2.17" x 3.35" - European'
            if kw['item1'] == '2':
                size = '1.75" x 3 - Slim'
            if kw['item1'] == '3':
                size = '1.75" x 3"'
            if kw['item1'] == '4':
                size = '2" x 3" Folded'
            if kw['item1'] == '5':
                size = '3.5" x 4" pre-scored to fold to 2" x 3.5'

        if graphic and 'items' in kw and kw['items'] == 'item2':
            item_name = 'POSTCARD'
            if kw['item2'] == '0':
                size = '3" x 5"'
            if kw['item2'] == '1':
                size = '4" x 6" Standard'
            if kw['item2'] == '2':
                size = '4" x 6" Standard'
            if kw['item2'] == '3':
                size = '5.5" x 8.5"'
            if kw['item2'] == '4':
                size = '6" x 9"'
            if kw['item2'] == '5':
                size = '8.5" x 11"'

        if graphic and 'items' in kw and kw['items'] == 'item3':
            item_name = 'FLYERS'
            if kw['item3'] == '0':
                size = '4" x 6"'
            if kw['item3'] == '1':
                size = '5" x 7"'
            if kw['item3'] == '2':
                size = '6" x 6"'
            if kw['item3'] == '3':
                size = '5.5" x 8.5"'
            if kw['item3'] == '4':
                size = '8" x 8"'
            if kw['item3'] == '5':
                size = '8.5" x 11"'
            if kw['item3'] == '6':
                size = '8.5" x 14"'
            if kw['item3'] == '7':
                size = '11" x 17"'
            if kw['item3'] == '8':
                size = '12" x 12"'

        if graphic and 'items' in kw and kw['items'] == 'item4':
            item_name = 'CD/DVD INSERT'
            if kw['item4'] == '0':
                size = 'Double Panel'
            if kw['item4'] == '1':
                size = 'Single Panel'
            if kw['item4'] == '2':
                size = 'w/ Tray Card'
            if kw['item4'] == '3':
                size = 'w/o Tray Card'

        if graphic and 'items' in kw and kw['items'] == 'item5':
            item_name = 'BROCHURE'
            if kw['item5'] == '0':
                size = '6" x 9"'
            if kw['item5'] == '1':
                size = '8.5" x 11"'
            if kw['item5'] == '2':
                size = '8.5" x 14"'
            if kw['item5'] == '3':
                size = '9" x 12"'
            if kw['item5'] == '4':
                size = '11" x 17"'

        if graphic and 'items' in kw and kw['items'] == 'item6':
            item_name = 'VINYL BANNER'
            if kw['item6'] == '0':
                size = '2ft x 4ft'
            if kw['item6'] == '1':
                size = '2ft x 5ft'
            if kw['item6'] == '2':
                size = '2ft x 6ft'
            if kw['item6'] == '3':
                size = '2ft x 7ft'
            if kw['item6'] == '4':
                size = '2ft x 8ft'
            if kw['item6'] == '5':
                size = '2ft x 9ft'
            if kw['item6'] == '6':
                size = '2ft x 10ft'
            if kw['item6'] == '7':
                size = '3ft x 4ft'
            if kw['item6'] == '8':
                size = '3ft x 5ft'
            if kw['item6'] == '9':
                size = '3ft x 6ft'
            if kw['item6'] == '10':
                size = '3ft x 7ft'
            if kw['item6'] == '11':
                size = '3ft x 8ft'
            if kw['item6'] == '12':
                size = '3ft x 9ft'
            if kw['item6'] == '13':
                size = '3ft x 10ft'
            if kw['item6'] == '14':
                size = '4ft x 10ft'

        if graphic and 'items' in kw and kw['items'] == 'item7':
            item_name = 'SELL SHEET'
            if kw['item7'] == '0':
                size = '4" x 6"'
            if kw['item7'] == '1':
                size = '8.5" x 11"'
            if kw['item7'] == '2':
                size = '11" x 17"'

        if graphic and 'items' in kw and kw['items'] == 'item8':
            item_name = 'DOOR HANGER'
            if kw['item8'] == '0':
                size = '3.5" x 8.5"'
            if kw['item8'] == '1':
                size = '3.5" x 11"'
            if kw['item8'] == '2':
                size = '4.25" x 11"'
            if kw['item8'] == '3':
                size = '5.5" x 17"'

        if graphic and 'items' in kw and kw['items'] == 'item9':
            item_name = 'NEWSLETTER'
            if kw['item9'] == '0':
                size = '3.5" x 8.5"'
            if kw['item9'] == '1':
                size = '3.5" x 11"'
            if kw['item9'] == '2':
                size = '4.25" x 11"'
            if kw['item9'] == '3':
                size = '5.5" x 17" (8pages)'

        if graphic and 'items' in kw and kw['items'] == 'item10':
            item_name = 'POSTER'
            if kw['item10'] == '0':
                size = '13" x 19"'
            if kw['item10'] == '1':
                size = '18" x 24"'
            if kw['item10'] == '2':
                size = '19" x 27"'
            if kw['item10'] == '3':
                size = '24" x 36"'
            if kw['item10'] == '4':
                size = '24" x 38"'
            if kw['item10'] == '5':
                size = '26" x 39"'
            if kw['item10'] == '6':
                size = '27" x 39"'

        if graphic and 'items' in kw and kw['items'] == 'item11':
            item_name = 'PRESENTATION FOLDER'
            if kw['item11'] == '0':
                size = '4" x 6" Sm Press Kit'
            if kw['item11'] == '1':
                size = '6" x 9" Folder w/3" pockets'
            if kw['item11'] == '2':
                size = '6" x 9" Fodler w/4" pockets'
            if kw['item11'] == '3':
                size = '6" x 9" Sample Kit'
            if kw['item11'] == '4':
                size = '9" x 12" Standard Folder'

        if graphic and 'items' in kw and kw['items'] == 'item12':
            item_name = 'EVENT TICKET'
            if kw['item12'] == '0':
                size = '2" x 5.5"'
            if kw['item12'] == '1':
                size = '4" x 10"'

        if graphic and 'items' in kw and kw['items'] == 'item13':
            item_name = 'MENU'
            if kw['item13'] == '0':
                size = '4" x 10"'
            if kw['item13'] == '1':
                size = '8.5" x 11"'

        if graphic and 'items' in kw and kw['items'] == 'item14':
            item_name = 'TSHIRT'
            size = ''

        if video and 'video_sizes' in kw and kw['video_sizes'] == 'video_sizes':
            if 'videos' in kw and kw['videos'] == 'video_size1':
                size = '1920px x 1080px(Youtube)'
            if 'videos' in kw and kw['videos'] == 'video_size2':
                size = 'YT Thumbnail'
            if 'videos' in kw and kw['videos'] == 'video_size3':
                size = '1080px x 1920px(TikTok/IG)'
            if 'videos' in kw and kw['videos'] == 'video_size4':
                size = 'LINKEDIN (Square)'
            if 'videos' in kw and kw['videos'] == 'video_size5':
                size = 'in Thumbnail'

        video_type = ''
        if video and 'vtype' in kw and kw['vtype']:
            if 'video_types' in kw and kw['video_types'] == 'video_type_1':
                video_type = '2D Animation'
            if 'video_types' in kw and kw['video_types'] == 'video_type_2':
                video_type = 'Motion Graphics'
            if 'video_types' in kw and kw['video_types'] == 'video_type_3':
                video_type = 'Social Media Content/Ad'
            if 'video_types' in kw and kw['video_types'] == 'video_type_4':
                video_type = 'Logo Animation'
            if 'video_types' in kw and kw['video_types'] == 'video_type_5':
                video_type = 'Video Bumper'
            if 'video_types' in kw and kw['video_types'] == 'video_type_6':
                video_type = 'Video Content'
            if 'video_types' in kw and kw['video_types'] == 'video_type_7':
                video_type = 'Video Presentation'

        colors = False
        c_cyan = ''
        c_red = ''
        c_blue = ''
        c_green = ''
        c_yellow = ''
        c_magenta = ''
        c_black = ''
        c_alpha = ''
        if 'cmyk_rgb_colors' in kw and kw['cmyk_rgb_colors'] == 'rgba_colors':
            colors = 'rgba'
            if 'red' in kw and kw['red']:
                c_red = kw['red']
            if 'green' in kw and kw['green']:
                c_green = kw['green']
            if 'blue' in kw and kw['blue']:
                c_blue = kw['blue']
            if 'alpha' in kw and kw['alpha']:
                c_alpha = kw['alpha']

        if 'cmyk_rgb_colors' in kw and kw['cmyk_rgb_colors'] == 'rgb_colors':
            colors = 'rgb'
            if 'rgb_red' in kw and kw['rgb_red']:
                c_red = kw['rgb_red']
            if 'rgb_green' in kw and kw['rgb_green']:
                c_green = kw['rgb_green']
            if 'rgb_blue' in kw and kw['rgb_blue']:
                c_blue = kw['rgb_blue']

        if 'cmyk_rgb_colors' in kw and kw['cmyk_rgb_colors'] == 'cmyk_colors':
            colors = 'cmyk'
            if 'cmyk_cyan' in kw and kw['cmyk_cyan']:
                c_cyan = kw['cmyk_cyan']
            if 'cmyk_magenta' in kw and kw['cmyk_magenta']:
                c_magenta = kw['cmyk_magenta']
            if 'cmyk_yellow' in kw and kw['cmyk_yellow']:
                c_yellow = kw['cmyk_yellow']
            if 'cmyk_black' in kw and kw['cmyk_black']:
                c_black = kw['cmyk_black']

        bleed = ""
        if graphic and 'bleed' in kw and kw['bleed']:
            if kw['bleed'] == 'bleed1':
                bleed = "yes"
            elif kw['bleed'] == 'bleed2':
                bleed = "no"

        image_provided = ""
        if graphic and 'imagess' in kw and kw['imagess']:
            if kw['imagess'] == 'images1':
                image_provided = "provided"
            elif kw['imagess'] == 'images2':
                image_provided = "not_provided"

        file_format = ""
        if 'formats' in kw and kw['formats']:
            if kw['formats'] == 'formats5':
                file_format = "eps"
            if kw['formats'] == 'formats6':
                file_format = "jpg"
            if kw['formats'] == 'formats7':
                file_format = "ai"
            if kw['formats'] == 'formats8':
                file_format = "png"
            if kw['formats'] == 'formats9':
                file_format = "psd"
            if kw['formats'] == 'formats10':
                file_format = "pdf"
            if 'vformat' in kw and kw['vformat'] == 'format1':
                file_format = "mp4"
            if 'vformat' in kw and kw['vformat'] == 'format2':
                file_format = "mov"

        g_yellow = False
        g_red = False
        g_blue = False
        g_violet = False
        g_green = False
        g_orange = False
        g_brown = False
        g_gray = False
        g_pink = False
        g_black = False

        full_color_front = False
        full_color_back = False
        bw_front = False
        bw_back = False
        no_back = False

        if graphic:
            if 'color1' in kw and kw['color1'] == 'yellow':
                g_yellow = True
            if 'color2' in kw and kw['color2'] == 'red':
                g_red = True
            if 'color3' in kw and kw['color3'] == 'blue':
                g_blue = True
            if 'color4' in kw and kw['color4'] == 'violet':
                g_violet = True
            if 'color5' in kw and kw['color5'] == 'green':
                g_green = True
            if 'color6' in kw and kw['color6'] == 'orange':
                g_orange = True
            if 'color7' in kw and kw['color7'] == 'brown':
                g_brown = True
            if 'color8' in kw and kw['color8'] == 'gray':
                g_gray = True
            if 'color9' in kw and kw['color9'] == 'pink':
                g_pink = True
            if 'color10' in kw and kw['color10'] == 'black':
                g_black = True

            # Design Location
            if 'design1' in kw and kw['design1'] == 'design1':
                full_color_front = True
            if 'design2' in kw and kw['design2'] == 'design2':
                full_color_back = True
            if 'design3' in kw and kw['design3'] == 'design3':
                bw_front = True
            if 'design4' in kw and kw['design4'] == 'design4':
                bw_back = True
            if 'design5' in kw and kw['design5'] == 'design5':
                no_back = True

        front_comment = ''
        back_comment = ''
        special_comment = ''
        design_description = ''
        if graphic and 'front_comment' in kw:
            front_comment = kw['front_comment']
        if graphic and 'back_comment' in kw:
            back_comment = kw['back_comment']
        if graphic and 'special_comment' in kw:
            special_comment = kw['special_comment']

        if video and 'design_desc' in kw:
            design_description = kw['design_desc']
        if video and 'special_ins' in kw:
            special_comment = kw['special_ins']
        task_name = ''
        if graphic:
            task_name = "GRAPHIC DESIGN : " + item_name
        if video:
            task_name = "VIDEO DESIGN : " + item_name
        task_vals = {
            'design_type': design_type,
            'is_design': True,
            'project_id': project.id,
            'name': task_name,
            'partner_id': request.env.user.partner_id.id,
            'company_name': kw['company_name'] or '',
            'contact_name': kw['contact_name'] or '',
            'phone': kw['phone'] or '',
            'fax': kw['fax'] or '',
            'website': kw['website'] or '',
            'email': kw['email'] or '',
            'city_zip': kw['city_zip'] or '',
            'moto': kw['motto'] or '',
            'positioning_statement': kw['statement'] or '',
            'item_information': item_name,
            'size': size or '',
            'colors': colors or False,
            'video_type': video_type,
            'bleed': bleed or '',
            'image_provided': image_provided or '',
            'file_format': file_format or '',
            'cyan': c_cyan or '',
            'magenta': c_magenta or '',
            'yellow': c_yellow or '',
            'red': c_red or '',
            'green': c_green or '',
            'blue': c_blue or '',
            'alpha': c_alpha or '',
            'black': c_black or '',
            'front_design_description': front_comment or '',
            'back_design_description': back_comment or '',
            'special_instruction': special_comment or '',
            'design_description': design_description or '',
            'g_yellow': g_yellow or False,
            'g_red': g_red or False,
            'g_blue': g_blue or False,
            'g_violet': g_violet or False,
            'g_green': g_green or False,
            'g_orange': g_orange or False,
            'g_brown': g_brown or False,
            'g_gray': g_gray or False,
            'g_pink': g_pink or False,
            'g_black': g_black or False,
            'full_color_front': full_color_front or False,
            'full_color_back': full_color_back or False,
            'bw_front': bw_front or False,
            'bw_back': bw_back or False,
            'no_back': no_back or False,
        }
        task_id = request.env['project.task'].sudo().create(task_vals)
        values = request.params

        video_data_1 = values.get("myfiles1")
        if hasattr(video_data_1, "filename"):
            file_data = base64.b64encode(video_data_1.read())
            filename = video_data_1.filename
            mimetype = self.check_get_mimetype(file_data=file_data, filename=filename)
            if mimetype:
                attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': file_data,
                    'public': True,
                    'res_model': 'project.task',
                    'res_id' : task_id.id,
                    'mimetype': mimetype,
                })

                video1 = request.env['file.videos'].create({
                    'task_id' : task_id.id,
                    'video_data' : file_data,
                    'video_name' : filename,
                    'attachment_id' : attachment_id.id,
                })

        video_data_2 = values.get("myfiles2")
        if hasattr(video_data_2, "filename"):
            file_data = base64.b64encode(video_data_2.read())
            filename = video_data_2.filename
            mimetype = self.check_get_mimetype(file_data=file_data, filename=filename)
            if mimetype:
                attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': file_data,
                    'public': True,
                    'res_model': 'project.task',
                    'res_id' : task_id.id,
                    'mimetype': mimetype,
                })

                video1 = request.env['file.videos'].create({
                    'task_id' : task_id.id,
                    'video_data' : file_data,
                    'video_name' : filename,
                    'attachment_id' : attachment_id.id,
                })

        video_data_3 = values.get("myfiles3")
        if hasattr(video_data_3, "filename"):
            file_data = base64.b64encode(video_data_3.read())
            filename = video_data_3.filename
            mimetype = self.check_get_mimetype(file_data=file_data, filename=filename)
            if mimetype:
                attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': file_data,
                    'public': True,
                    'res_model': 'project.task',
                    'res_id' : task_id.id,
                    'mimetype': mimetype,
                })

                video1 = request.env['file.videos'].create({
                    'task_id' : task_id.id,
                    'video_data' : file_data,
                    'video_name' : filename,
                    'attachment_id' : attachment_id.id,
                })

        video_data_4 = values.get("myfiles4")
        if hasattr(video_data_4, "filename"):
            file_data = base64.b64encode(video_data_4.read())
            filename = video_data_4.filename
            mimetype = self.check_get_mimetype(file_data=file_data, filename=filename)
            if mimetype:
                attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': file_data,
                    'public': True,
                    'res_model': 'project.task',
                    'res_id' : task_id.id,
                    'mimetype': mimetype,
                })

                video1 = request.env['file.videos'].create({
                    'task_id' : task_id.id,
                    'video_data' : file_data,
                    'video_name' : filename,
                    'attachment_id' : attachment_id.id,
                })

        video_data_5 = values.get("myfiles5")
        if hasattr(video_data_5, "filename"):
            file_data = base64.b64encode(video_data_5.read())
            filename = video_data_5.filename
            mimetype = self.check_get_mimetype(file_data=file_data, filename=filename)
            if mimetype:
                attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': file_data,
                    'public': True,
                    'res_model': 'project.task',
                    'res_id' : task_id.id,
                    'mimetype': mimetype,
                })

                video1 = request.env['file.videos'].create({
                    'task_id' : task_id.id,
                    'video_data' : file_data,
                    'video_name' : filename,
                    'attachment_id' : attachment_id.id,
                })

        video_data_6 = values.get("myfiles6")
        if hasattr(video_data_6, "filename"):
            file_data = base64.b64encode(video_data_6.read())
            filename = video_data_6.filename
            mimetype = self.check_get_mimetype(file_data=file_data, filename=filename)
            if mimetype:
                attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': file_data,
                    'public': True,
                    'res_model': 'project.task',
                    'res_id' : task_id.id,
                    'mimetype': mimetype,
                })

                video1 = request.env['file.videos'].create({
                    'task_id' : task_id.id,
                    'video_data' : file_data,
                    'video_name' : filename,
                    'attachment_id' : attachment_id.id,
                })

        if kw.get('file1_data', False):
            file = ast.literal_eval(kw.get('file1_data'))
            attachment_id = request.env['ir.attachment'].create({
                'name': file.get('name'),
                'type': 'binary',
                'datas': file.get('data'),
                'public': True,
                'res_model': 'project.task',
                'res_id' : task_id.id,
            })

            image1 = request.env['file.images'].create({
                'task_id' : task_id.id,
                'image' : file.get('data'),
                'image_name' : file.get('name'),
                'attachment_id' : attachment_id.id,
            })

        if kw.get('file2_data', False):
            file = ast.literal_eval(kw.get('file2_data'))
            attachment_id = request.env['ir.attachment'].create({
                'name': file.get('name'),
                'type': 'binary',
                'datas': file.get('data'),
                'public': True,
                'res_model': 'project.task',
                'res_id' : task_id.id,
            })

            image1 = request.env['file.images'].create({
                'task_id' : task_id.id,
                'image' : file.get('data'),
                'image_name' : file.get('name'),
                'attachment_id' : attachment_id.id,
            })

        if kw.get('file3_data', False):
            file = ast.literal_eval(kw.get('file3_data'))
            attachment_id = request.env['ir.attachment'].create({
                'name': file.get('name'),
                'type': 'binary',
                'datas': file.get('data'),
                'public': True,
                'res_model': 'project.task',
                'res_id' : task_id.id,
            })

            image1 = request.env['file.images'].create({
                'task_id' : task_id.id,
                'image' : file.get('data'),
                'image_name' : file.get('name'),
                'attachment_id' : attachment_id.id,
            })

        if kw.get('file4_data', False):
            file = ast.literal_eval(kw.get('file4_data'))
            attachment_id = request.env['ir.attachment'].create({
                'name': file.get('name'),
                'type': 'binary',
                'datas': file.get('data'),
                'public': True,
                'res_model': 'project.task',
                'res_id' : task_id.id,
            })

            image1 = request.env['file.images'].create({
                'task_id' : task_id.id,
                'image' : file.get('data'),
                'image_name' : file.get('name'),
                'attachment_id' : attachment_id.id,
            })

        if kw.get('file5_data', False):
            file = ast.literal_eval(kw.get('file5_data'))
            attachment_id = request.env['ir.attachment'].create({
                'name': file.get('name'),
                'type': 'binary',
                'datas': file.get('data'),
                'public': True,
                'res_model': 'project.task',
                'res_id' : task_id.id,
            })

            image1 = request.env['file.images'].create({
                'task_id' : task_id.id,
                'image' : file.get('data'),
                'image_name' : file.get('name'),
                'attachment_id' : attachment_id.id,
            })

        if kw.get('file6_data', False):
            file = ast.literal_eval(kw.get('file6_data'))
            attachment_id = request.env['ir.attachment'].create({
                'name': file.get('name'),
                'type': 'binary',
                'datas': file.get('data'),
                'public': True,
                'res_model': 'project.task',
                'res_id' : task_id.id,
            })

            image1 = request.env['file.images'].create({
                'task_id' : task_id.id,
                'image' : file.get('data'),
                'image_name' : file.get('name'),
                'attachment_id' : attachment_id.id,
            })

        url = "/my/tasks?filterby=" + str(project.id)
        return request.redirect(url)

    @http.route('/how-it-works', type='http', auth='public', website=True)
    def web_how_works(self):
        return  request.render('wt_office_hunddle.how_it_work')

    @http.route('/video-design', type='http', auth='public', website=True)
    def video_design_office_huddle(self):
        return  request.render('wt_office_hunddle.video_design_officehuddle_template')

    @http.route('/tryofficehuddle.com', type='http', auth='public', website=True)
    def try_office_huddle(self):
        return  request.render('wt_office_hunddle.tryofficehuddle_form')

    @http.route('/customer-portal', type='http', auth='public', website=True)
    def customer_portal_office_huddle(self):
        return  request.render('wt_office_hunddle.customer_portal_officehuddle_template')

    @http.route('/graphic', type='http', auth='public', website=True)
    def graphics_office_huddle(self):
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.redirect('/web/login')
        return  request.render('wt_office_hunddle.graphic_design_form')

    @http.route('/tshirt-printing', type='http', auth='public', website=True)
    def tshirt_printing_office_huddle(self):
        return  request.render('wt_office_hunddle.t_shirt_printing_design_selection_officehuddle_template')

    @http.route('/my/assessment', type='http', auth='public', website=True)
    def my_assessments(self):
        assessments = request.env['assessment.assessment'].search([('user_id', '=', request.env.user.id)])
        vals = {
            'assessments': assessments,
        }
        return  request.render('wt_office_hunddle.view_assessments_officehuddle_template', vals)

    @http.route('/page/assessment', type='http', auth='public', website=True)
    def new_assessment(self):
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
        return  request.render('wt_office_hunddle.new_assessment_tmpl', vals)

    @http.route('/assesment/submit', type='http', auth='public', website=True)
    def new_assessment_submit(self, **kw):
        all_questions_id = request.env['question.question'].search([]).mapped('id')
        vals = {
            'user_id': request.env.user.id,
        }
        assessment = request.env['assessment.assessment'].create(vals)
        assessment.onchnage_user_id()
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

    # @http.route('/page/assessment', type='http', auth='public', website=True)
    # def assessment(self):
    #     all_question_ids = request.env['question.question']
    #     marketing_ids = all_question_ids.sudo().search([('question_type', '=', 'marketing')])
    #     financial_ids = all_question_ids.sudo().search([('question_type', '=', 'finance')])
    #     team_development_ids = all_question_ids.sudo().search([('question_type', '=', 'team_development')])
    #     lead_generation_ids = all_question_ids.sudo().search([('question_type', '=', 'lead_generation')])
    #     lead_conversion_ids = all_question_ids.sudo().search([('question_type', '=', 'lead_conversion')])
    #     customer_fulfillment_ids = all_question_ids.sudo().search([('question_type', '=', 'customer_fulfillment')])
    #     form_submission_ids = all_question_ids.sudo().search([('question_type', '=', 'form_submission')])
    #     vals = {
    #         'marketing_ids': marketing_ids,
    #         'financial_ids': financial_ids,
    #         'team_development_ids': team_development_ids,
    #         'lead_generation_ids': lead_generation_ids,
    #         'lead_conversion_ids': lead_conversion_ids,
    #         'customer_fulfillment_ids': customer_fulfillment_ids,
    #         'form_submission_ids': form_submission_ids,
    #     }
    #     return  request.render('wt_office_hunddle.assessment_tmpl',vals)

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
            print("------ marketing_total ---- ", marketing_total)
            marketing_cl = None
            if marketing_total and marketing_total <= 50:
                marketing_cl = 'red'
            elif marketing_total and marketing_total <= 80:
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

    # @http.route('/assesment/submit', type='http', auth='public', website=True)
    # def assessment_submit(self, **kw):

    #     all_questions_id = request.env['question.question'].search([]).mapped('id')
    #     annual_revenue = None
    #     if kw.get('annual') == '0-50K':
    #         annual_revenue = '0'
    #     elif kw.get('annual') == '50-100K':
    #         annual_revenue = '1'
    #     elif kw.get('annual') == '100-200K':
    #         annual_revenue = '2'
    #     elif kw.get('annual') == '200-500K':
    #         annual_revenue = '3'
    #     elif kw.get('annual') == '500-1M':
    #         annual_revenue = '4'
    #     elif kw.get('annual') == '1M-5M':
    #         annual_revenue = '5'
    #     else:
    #         annual_revenue = '0'

    #     state_id = None
    #     if kw.get('state'):
    #         state_id = request.env['res.country.state'].search([('name', '=', kw.get('state').capitalize())])
        
    #     state_id2 = None
    #     if kw.get('state2'):
    #         state_id2 = request.env['res.country.state'].search([('name', '=', kw.get('state2').capitalize())])
        
    #     name = kw.get('firstname') + ' ' + kw.get('lastname') 
    #     vals = {
    #     'company_name': kw.get('legalname'),
    #     'website': kw.get('website'),
    #     'name': name,
    #     'mailing_address': kw.get('mailingadd'),
    #     'city': kw.get('city'),
    #     'state_id': state_id.id if state_id else False,
    #     'zipcode': kw.get('zipcode'),
    #     'physical_address': kw.get('physicaladd'),
    #     'city2': kw.get('city2'),
    #     'state_id2': state_id2.id if state_id2 else False,
    #     'zipcode2': kw.get('zipcode2'),
    #     'email': kw.get('Email2'),
    #     'website2': kw.get('Website'),
    #     'business_phone': kw.get('businessphone'),
    #     'phone': kw.get('phone2'),
    #     'cell_phone': kw.get('cellphone'),
    #     'no_of_employee': kw.get('employees'),
    #     'annual_revenue': annual_revenue,
    #     'no_of_leaders_report': kw.get('leaders'),
    #     'start_date': kw.get('date'),
    #     }
    #     assessment = request.env['assessment.assessment'].create(vals)
    #     if assessment:
    #         question_line_ids = []
    #         for i in all_questions_id:
    #             if str(i) in kw.keys():
    #                 question_line_ids.append((0, 0, {
    #                     'name': int(i),
    #                     'assessment_id': assessment.id,
    #                     'result': kw.get(str(i))
    #                     }))
    #         if question_line_ids:
    #             assessment.write({'assessment_list_ids': question_line_ids})

    #     return request.redirect('/assessment/output?result_id=%s' %(assessment.id))
    
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
