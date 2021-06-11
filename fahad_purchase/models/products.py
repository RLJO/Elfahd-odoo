from odoo import models, fields, api, _


class product_template(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [
        ('default_code_unique', 'unique(default_code)', 'intarnal reference must be unique.')
    ]