# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import time
from collections import defaultdict


class DieselDifference(models.Model):
    _name = 'diesel.difference.lines'
    _description = 'Diesel Difference'
    _rec_name = 'aramco_no'

    aramco_no = fields.Char('Aramco No')
    line_id = fields.Many2one('new.line', string='Line')
    date = fields.Datetime('Date')
    quantity = fields.Float(string='Quantity')
    distance = fields.Float(_('Distance'))
    ratio = fields.Float(string='Ratio', default=2.7)
    difference = fields.Float(string='Difference')
    expense_id = fields.Many2one('expense.register.lines', string='Expenses lines', ondelete='cascade')
    trip_id = fields.Many2one('trips', string='Trip')

    @api.depends('quantity', 'distance', 'ratio')
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.distance / rec.ratio - rec.quantity
