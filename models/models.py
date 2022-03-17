# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
import re


class FileImage(models.Model):
	_name = 'file.images'
	_description = 'File Images'

	image = fields.Binary("Image File")
	task_id = fields.Many2one('project.task',string='Task')
	image_name = fields.Char('Image Name')
	attachment_id = fields.Many2one('ir.attachment', string="Images")


class FileVideo(models.Model):
    _name = 'file.videos'
    _description = 'File Videos'

    video_data = fields.Binary("Video File")
    task_id = fields.Many2one('project.task',string='Task')
    video_name = fields.Char('Name')
    attachment_id = fields.Many2one('ir.attachment', string="Video")


class ProjectTask(models.Model):
    _inherit = "project.task"

    design_type = fields.Selection([('video', "Video"), ('graphic', "Graphic")])
    is_design = fields.Boolean()
    contact_name = fields.Char()
    company_name = fields.Char()
    phone = fields.Char()
    fax =  fields.Char()
    website = fields.Char()
    email = fields.Char()
    city_zip = fields.Char()
    moto = fields.Text()
    positioning_statement = fields.Text()
    item_information = fields.Char()
    size = fields.Char()
    video_type = fields.Char()
    colors = fields.Selection([("rgb", "RGB"), ("rgba", "RGBA"), ("cmyk", "CMYK")])
    bleed = fields.Selection([('yes', "Yes"), ('no', "No")])
    image_provided = fields.Selection([('provided', "Provided"), ('not_provided', "Not Provided")])
    file_format = fields.Selection([('eps', ".EPS"), ('jpg', ".JPG"), ('ai', ".AI"), ('png', ".PNG"), ('psd', ".PSD"), ('pdf', "PDF"), ('mp4', "MP4"), ('mov', "MOV")])
    cyan = fields.Char()
    magenta = fields.Char()
    yellow = fields.Char()
    black = fields.Char()
    red = fields.Char()
    blue = fields.Char()
    green = fields.Char()
    alpha = fields.Char()
    front_design_description = fields.Text()
    back_design_description = fields.Text()
    special_instruction = fields.Text()
    design_description = fields.Text()

    # Design Location
    full_color_front = fields.Boolean("FULL COLOR FRONT")
    full_color_back = fields.Boolean("FULL COLOR BACK")
    bw_front = fields.Boolean("B/W FRONT")
    bw_back = fields.Boolean("B/W BACK")
    no_back = fields.Boolean("NO BACK")

    # Graphic Colors
    g_yellow = fields.Boolean("YELLOW")
    g_red = fields.Boolean("RED")
    g_blue = fields.Boolean("BLUE")
    g_violet = fields.Boolean("VIOLET")
    g_green = fields.Boolean("GREEN")
    g_orange = fields.Boolean("ORANGE")
    g_brown = fields.Boolean("BROWN")
    g_gray = fields.Boolean("GRAY")
    g_pink = fields.Boolean("PINK")
    g_black = fields.Boolean("BLACK")
    g_white = fields.Boolean("WHITE")
    g_fullcolor = fields.Boolean("FULL COLOR")

    images_lines = fields.One2many('file.images','task_id',string='Attached Files')
    videos_lines = fields.One2many('file.videos','task_id',string='Attached Files')


class website_blog_post(models.Model):
    _inherit = "blog.post"

    bg_image = fields.Image(string="BG Image")
    valid_page = fields.Many2one('website.page', string='Website Page')


class website_crm_service(models.Model):
    _name = "service.service"

    name = fields.Char(string='Name', required=True)


class website_crm_lead(models.Model):
    _inherit = "crm.lead"

    service_id = fields.Many2one('service.service', string='Service')
    industry = fields.Char()

    sales = fields.Boolean()
    recruiting = fields.Boolean()
    customer_support = fields.Boolean()
    marketing = fields.Boolean()
    executive_assistance = fields.Boolean()
    others = fields.Boolean()
    budget = fields.Char()
    hear_about = fields.Char()

    email_hear = fields.Boolean()
    phone_call_hear = fields.Boolean("Phone/Audio Call")
    vc = fields.Boolean("Video Chat (Google Meet , Zoom)")
    screenshare = fields.Boolean("Screenshare")
    chat_msg = fields.Boolean("Chat / Messaging (Slack ,Other)")




class ProductTemplate(models.Model):
    _inherit = 'slide.channel'

    trainer = fields.Many2one('res.partner', string='Trainer')

class SpeakersPartner(models.Model):
    _inherit = 'res.partner'

    is_speaker = fields.Boolean()
    date_begin = fields.Datetime(
        string='Start Date')
    date_end = fields.Datetime(
        string='End Date')
    facebook_url = fields.Char()
    twitter_url = fields.Char()
    google_plus_url = fields.Char()
    company_name = fields.Char()
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
    no_discount_on_product = fields.Boolean("No Discount On Product?")
    bussiness_phone = fields.Char("Bussiness Phone")
    employees = fields.Integer("No of employees")
    annual = fields.Selection([
        ('0-50K', "0-50K"),
        ('50K-100K', "50K-100K"),
        ('100K-200K', "100K-200K"),
        ('200K-500K', "200K-500K"),
        ('500K-1M', "500K-1M"),
        ('1M-5M', "1M-5M"),
        ('OVER 5M', "OVER 5M")
    ], "ANNUAL REVENUE")
    leaders = fields.Selection([
        ('1', "1"),
        ('2', "2"),
        ('3', "3"),
        ('4', "4"),
        ('5', "5"),
        ('6', "6"),
        ('7', "7")
    ], "No of leaders report directly")
    business_date = fields.Date("Bussiness Start Date")
    website_link = fields.Char()
    fax_no = fields.Char()
    positioning_statement = fields.Text()
    moto = fields.Text()


class EventEvent(models.Model):
    _inherit = 'event.event'

    speaker_ids = fields.Many2many('res.partner', 'speaker_id',domain=[('is_speaker','=',True)])
    desc = fields.Text()
    video_url = fields.Char()
    image = fields.Image(string="Image")
    bg_image_ids = fields.One2many('event.background.slider', 'event_id', string="Slider Images")
    schedule_ids = fields.One2many('event.schedule.list', 'event_id', string="Schedules")

class EventBackgroundSlider(models.Model):
    _name = "event.background.slider"

    event_id = fields.Many2one('event.event', string="Event")
    image = fields.Image(string="Background Image")

class EventScheduleList(models.Model):
    _name = "event.schedule.list"
    _order = 'sequance,time'

    event_id = fields.Many2one('event.event', string="Event")
    sequance = fields.Integer(string="Sequance", Default=10)
    time = fields.Char(string="TIME")
    schedule = fields.Char(string="Schedule")
    venue = fields.Char(String="Venue")

class website(models.Model):
    _inherit = 'website'

    video_one = fields.Char(string="Homepage Youtube Video URL")
    embed_one_code = fields.Char(compute="_compute_one_embed_code")
    video_two = fields.Char(string="Train-Like-CEO Youtube Video URL")
    embed_two_code = fields.Char(compute="_compute_two_embed_code")
    video_three = fields.Char(string="Graphic Design Youtube Video URL", default="/wt_office_hunddle/static/src/videos/train_video.mp4")
    embed_three_code = fields.Char(compute="_compute_three_embed_code")
    video_four = fields.Char(string="ERP Development Youtube Video URL", default="/wt_office_hunddle/static/src/videos/ERP_video.mp4")
    embed_four_code = fields.Char(compute="_compute_four_embed_code")
    video_five = fields.Char(string="Virtual Staffing Youtube Video URL", default="/wt_office_hunddle/static/src/videos/train_video.mp4")
    embed_five_code = fields.Char(compute="_compute_five_embed_code")
    video_six = fields.Char(string="Event Youtube Video URL", default="/wt_office_hunddle/static/src/videos/EVENTS_video.mp4")
    embed_six_code = fields.Char(compute="_compute_six_embed_code")


    def get_video_embed_url_code(self, video_url):
        ''' Computes the valid iframe from given URL that can be embedded
            (or False in case of invalid URL).
        '''

        if not video_url:
            return False

        # To detect if we have a valid URL or not
        validURLRegex = r'^(http:\/\/|https:\/\/|\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'

        # Regex for few of the widely used video hosting services
        ytRegex = r'^(?:(?:https?:)?\/\/)?(?:www\.)?(?:youtu\.be\/|youtube(-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((?:\w|-){11})(?:\S+)?$'
        vimeoRegex = r'\/\/(player.)?vimeo.com\/([a-z]*\/)*([0-9]{6,11})[?]?.*'
        dmRegex = r'.+dailymotion.com\/(video|hub|embed)\/([^_?]+)[^#]*(#video=([^_&]+))?'
        igRegex = r'(.*)instagram.com\/p\/(.[a-zA-Z0-9]*)'
        ykuRegex = r'(.*).youku\.com\/(v_show\/id_|embed\/)(.+)'

        if not re.search(validURLRegex, video_url):
            return False
        else:
            embedUrl = False
            ytMatch = re.search(ytRegex, video_url)
            vimeoMatch = re.search(vimeoRegex, video_url)
            dmMatch = re.search(dmRegex, video_url)
            igMatch = re.search(igRegex, video_url)
            ykuMatch = re.search(ykuRegex, video_url)

            if ytMatch and len(ytMatch.groups()[1]) == 11:
                embedUrl = 'https://www.youtube%s.com/embed/%s' % (ytMatch.groups()[0] or '', ytMatch.groups()[1])
            elif vimeoMatch:
                embedUrl = '//player.vimeo.com/video/%s' % (vimeoMatch.groups()[2])
            elif dmMatch:
                embedUrl = '//www.dailymotion.com/embed/video/%s' % (dmMatch.groups()[1])
            elif igMatch:
                embedUrl = '//www.instagram.com/p/%s/embed/' % (igMatch.groups()[1])
            elif ykuMatch:
                ykuLink = ykuMatch.groups()[2]
                if '.html?' in ykuLink:
                    ykuLink = ykuLink.split('.html?')[0]
                embedUrl = '//player.youku.com/embed/%s' % (ykuLink)
            else:
                # We directly use the provided URL as it is
                embedUrl = video_url
            return embedUrl

    @api.depends('video_one')
    def _compute_one_embed_code(self):
        for rec in self:
            rec.embed_one_code = rec.get_video_embed_url_code(rec.video_one) or rec.video_one

    @api.depends('video_two')
    def _compute_two_embed_code(self):
        for rec in self:
            rec.embed_two_code = rec.get_video_embed_url_code(rec.video_two) or rec.video_two

    @api.depends('video_three')
    def _compute_three_embed_code(self):
        for rec in self:
            rec.embed_three_code = rec.get_video_embed_url_code(rec.video_three) or rec.video_three

    @api.depends('video_four')
    def _compute_four_embed_code(self):
        for rec in self:
            rec.embed_four_code = rec.get_video_embed_url_code(rec.video_four) or rec.video_four

    @api.depends('video_five')
    def _compute_five_embed_code(self):
        for rec in self:
            rec.embed_five_code = rec.get_video_embed_url_code(rec.video_five) or rec.video_five

    @api.depends('video_six')
    def _compute_six_embed_code(self):
        for rec in self:
            rec.embed_six_code = rec.get_video_embed_url_code(rec.video_six) or rec.video_six
