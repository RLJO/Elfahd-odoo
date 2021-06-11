# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class wheel_purchase(models.Model):
    _name = 'wheel.purchase'
    _description = 'Purchasing bulk of wheels'

    _rec_name = 'invoice_number'

    code = fields.Char(string='Code')
    invoice_number = fields.Char(string='Invoice Number')
    invoice_date = fields.Date(string='Invoice Date')
    wheels_ids = fields.One2many('wheel.purchase.line', 'purchase_id', string='Wheels')
    total = fields.Float(string='Total')

    # @api.one
    @api.depends('wheels_ids')
    def _compute_total(self):
        total_price = 0.0
        for rec in self.wheels_ids:
            total_price += rec.purchase_price
        self.total = total_price


    supplier_id = fields.Many2one('res.partner', string='Supplier Id')

    supplier_invoice_type = fields.Selection([
                                                 ('no_invoice', 'Do Not Create Invoice'),
                                                 ('invoiced', 'Create Invoice'),
                                             ], string='Supplier Invoice Type', default='no_invoice')

    expense_account = fields.Many2one('account.account', string='Expense Account')
    expense_journal = fields.Many2one('account.journal', string='Expense Journal')
    estimated_life = fields.Float(string='Estimated Life')
    show_wheels = fields.Boolean(string='Show Wheels')

    # @api.onchange('invoice_date', 'estimated_life')
    # def onchange_fields(self):
    #     if self.invoice_date and self.estimated_life:
    #         self.show_wheels = True
    #     else:
    #         self.show_wheels = False

    state = fields.Selection([('draft', 'New'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed')], string='State', default='draft')

    # @api.one
    def button_review(self):
        if not self.wheels_ids:
            raise ValidationError('You Must Register at least one line in Wheels')
        self.code = self.env['ir.sequence'].get('wheel.purchase')
        self.write({'state': 'reviewed'})

    # @api.one
    def button_confirmed(self):
        for record in self:
            if record.supplier_invoice_type == 'invoiced':
                name = 'Purchasing Num ' + str(
                    len(record.wheels_ids)) + ' Wheel With Invoice Number' + record.invoice_number,
                invoice_vals = {
                    'partner_id': record.supplier_id and record.supplier_id.id,
                    'type': 'in_invoice',
                    'journal_id': record.expense_journal and record.expense_journal.id,
                    'account_id': record.supplier_id.property_account_payable and record.supplier_id.property_account_payable.id,
                    'date_invoice': record.invoice_date,
                    'invoice_line': [(0, _, {'name': name,
                                             'quantity': 1,
                                             'price_unit': record.total,
                                             'account_id': record.expense_account.id})],
                }
                self.env['account.account'].create(invoice_vals)
                # invoice
            for line in record.wheels_ids:
                vals = {}
                vals.update({
                    'wheel_no': line.wheel_no or '',
                    'manufacturing_company': line.manufacturing_company or '',
                    'size': line.size or 0,
                    'install_type': line.install_type or '',
                    'wheel_status': line.wheel_status or '',
                    'purchase_price': line.purchase_price or 0.0,
                    'purchase_date': line.purchase_date or False,
                    'estimated_life': line.estimated_life or 0.0,
                    'purchase_id': line.purchase_id.id or False,
                    'supplier_id': record.supplier_id.id or False,
                    'supplier_invoice_type': record.supplier_invoice_type or '',
                    'expense_account': record.expense_account.id or False,
                    'expense_journal': record.expense_journal.id or False,

                })
                self.env['new.wheel'].create(vals)
        self.state = 'confirmed'
        return True

    # @api.one
    def button_closed(self):
        return self.write({'state': 'closed'})

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].get('wheel.purchase')
    #     return super(wheel_purchase, self).create(vals)


class wheel_purchase_line(models.Model):
    _name = 'wheel.purchase.line'

    wheel_no = fields.Char(string='Wheel No.')
    manufacturing_company = fields.Char('Manufacturer')
    size = fields.Char(string='Size')
    install_type = fields.Selection([
                                        ('vehicle', 'Vehicle'),
                                        ('tank', 'Tank'),
                                        ('both', 'Both'),
                                    ], string='Wheel Installment Type', )

    # @api.onchange('install_type')
    # def onchange_install_type(self):
    #     for record in self:
    #         record.purchase_date = self.purchase_id.invoice_date
    #         record.estimated_life = self.purchase_id.estimated_life

    wheel_status = fields.Selection([
                                        ('new', 'New'),
                                        ('used', 'Used'),
                                    ], string='Wheel Status', )

    purchase_price = fields.Float(string='Purchase Price')

    # @api.onchange('purchase_price')
    # def onchange_purchase_price(self):
    #     for record in self:
    #         record.purchase_date = self.purchase_id.invoice_date
    #         record.estimated_life = self.purchase_id.estimated_life

    purchase_date = fields.Date(string='Purchase date')
    estimated_life = fields.Float(string='Estimated Life')
    purchase_id = fields.Many2one('wheel.purchase', 'Purchase Number')



