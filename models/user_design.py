# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class UserDesigns(models.Model):
    _name = "user.design"
    _order = "create_date desc"

    save_design = fields.Binary("Design")
    name = fields.Char("Name")
    user_id = fields.Many2one('res.users')



class SaveUserDesigns(models.Model):
    _name = "save.user.design"
    _order = "create_date desc"

    save_front_design = fields.Binary("Front Design")
    save_back_design = fields.Binary("Back Design")
    user_id = fields.Many2one('res.users')