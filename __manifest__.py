# -*- coding: utf-8 -*-


{
    'name': 'WT Website Office Huddle',
    'version': '13',
    'summary': 'Website',
    'category': 'Website',
    'author': 'Warlock Technologies',
    'depends': ['website', 'website_event', 'sale', 'website_event_track', 'website_blog', 'portal', 'auth_signup', 'website_slides', 'base', 'web', 'mail'],
    'website': 'http://www.warlocktechnologies.com',
    'data':[
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/question.xml',
        'views/views.xml',
        'views/assets.xml',
        'views/header.xml',
        'views/footer.xml',
        'views/home.xml',
        'views/blog_post_views_inherit.xml',
        'views/how_it_works.xml',
        'views/crm_lead_view.xml',
        'views/business_coatching_template.xml',
        'views/toolkit.xml',
        'views/lead_generation_resources.xml',
        'views/seo_resources.xml',
        'views/access_to_capital_resources.xml',
        'views/business_credit_resources.xml',
        'views/train-like-ceo.xml',
        'views/course.xml',
        'views/erp.xml',
        'views/graphic_design.xml',
        'views/virtual_staffing.xml',
        'views/event_new.xml',
        'views/assessment.xml',
        'views/assess_output.xml',
        'views/assessment_view.xml',
        'views/website_login_view.xml',
        'views/customer_portal_view.xml',
        'views/signup_view.xml',
        'views/graphics_form_view.xml',
        'views/elearning_view.xml',
        'views/project_task_view.xml',
        'views/video_page_view.xml',
        'views/try_office_huddle_home_view.xml',
        'views/new_assessment_view.xml',
        'views/view_assessments_template_view.xml',
        'views/printing_products_view.xml',
    ],
    'qweb': [
        'static/src/xml/binary_preview.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
