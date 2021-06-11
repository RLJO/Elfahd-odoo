# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class account_voucher(models.Model):
    _inherit = "account.move"

    balance_credits = fields.Float(string = 'Total balance')
    balance_debit = fields.Float(string = 'Total debit')
    # , compute = '_balance'

    # @api.depends('line_cr_ids','line_dr_ids')
    # def _balance(self):
    #     self.balance_credits = sum([l.amount_unreconciled for l in self.line_cr_ids])
    #     self.balance_debit = sum([l.amount_unreconciled for l in self.line_dr_ids])
