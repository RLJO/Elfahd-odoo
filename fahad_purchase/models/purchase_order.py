from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    warehouse_selected = fields.Boolean('Warehouse Selected')

    def wkf_confirm_order(self):
        if not self.warehouse_selected:
            raise ValidationError(_("Cannot confirm order unless check Warehouse Selected"))
        return super(purchase_order, self).wkf_confirm_order()