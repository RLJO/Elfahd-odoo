# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import time


class not_financial_custody(models.Model):
    _name = 'not.financial.custody'

    custody = fields.Many2one('product.product', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')
    custody_state = fields.Selection([('new', 'New'), ('used', 'Used')], string='Custody State')
    state = fields.Selection([('deliver', 'Deliver'), ('receive', 'Receive')], string='State')
    delivery_date = fields.Datetime(string='Delivery Date')
    note = fields.Char('Note')
    car_id = fields.Many2one('new.car', 'Car')
    tank_id = fields.Many2one('new.tank', 'Tank')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    # @api.one
    # @api.depends('number', 'unit_price')
    # def _compute_total_amount(self):
    #     if self.product_uom_id.uom_type != 'reference':
    #         if self.product_uom_id.uom_type != 'bigger':
    #             uom = self.product_uom_id.fator
    #         else:
    #             uom = 1 / self.product_uom_id.fator
    #     else:
    #         uom = 1
    #     self.total = self.number * self.unit_price * uom