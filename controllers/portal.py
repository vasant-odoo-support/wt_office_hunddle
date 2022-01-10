# -*- coding: utf-8 -*-
import datetime
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from werkzeug.exceptions import NotFound
from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal


class CustomerPortal(CustomerPortal):

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_home_portal_values()
        return request.render("wt_office_hunddle.customer_portal_officehuddle_template")
