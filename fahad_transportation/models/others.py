import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class product_template(models.Model):
    _inherit = "product.template"

    # @api.one
    # @api.onchange('type')
    # def onchange_type(self):
    #     if self.type == 'product' or self.type == 'consu':
    #         self.valuation = 'real_time'