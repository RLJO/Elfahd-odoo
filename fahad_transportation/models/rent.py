# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class rent(models.Model):
    _name = 'rent'

    code = fields.Char(_('Code'))
    customer_id = fields.Many2one('res.partner', _('Customer'))
    rent_type = fields.Selection([('car', _('Car')), ('tank', _('Tank')), ('vehicle', _('Vehicle'))],
                                 _('Rent Type'))
    car_id = fields.Many2one('new.car', _('Car'))
    tank_id = fields.Many2one('new.tank', _('Tank'))
    vehicle_id = fields.Many2one('new.vehicle', _('Vehicle'))
    rent_start_date = fields.Date(_('Rent Start Date'))
    period_month = fields.Integer(_('Rent Period by Months'))
    rent_end_date = fields.Date(_('Rent End Date'))
    monthly_rent_amount = fields.Float(_('Monthly Rent Amount'))
    income_account_id = fields.Many2one('account.account', _('Income Account'))
    journal_id = fields.Many2one('account.journal', _('Journal'))
    note = fields.Html(_('Note'))
    rent_line_ids = fields.One2many('rent.lines', 'rent_id', _('Rent Lines'))
    machine_line_ids = fields.One2many('machine.motor.line', 'rent_id', string='Machine Motor Asset')
    differential_line_ids = fields.One2many('differential.line', 'rent_id', string='Defrance Asset')
    gearbox_line_ids = fields.One2many('gearbox.line', 'rent_id', string='GearBox Asset')
    # secondary_asset_ids = fields.One2many('car.asset', 'rent_id', _('Secondary Asset'))
    state = fields.Selection([('new', _('New')), ('review', _('Reviewed')), ('confirm', _('Confirmed')),
                              ('close', _('Closed')), ('end', _('End'))], _('Status'), default='new')

    # @api.one
    def button_review(self):
        self.code = self.env['ir.sequence'].get('rent')
        self.write({'state': 'review'})

    # @api.one
    def button_draft(self):
        self.write({'state': 'new'})

    # @api.one
    def button_close(self):
        self.write({'state': 'close'})

    # @api.multi
    def button_confirm(self):
        if self.rent_type in ('car', 'vehicle'):
            new_car = self.env['new.car'].browse(self.car_id.id)
            new_car.write({'state': 'rent'})
            car_maintenance = self.env['car.maintenance'].search([('new_car_id', '=', self.car_id.id)])
            car_maintenance.write({'active': False})
        if self.rent_type in ('tank', 'vehicle'):
            new_tank = self.env['new.tank'].browse(self.tank_id.id)
            new_tank.write({'state': 'rent'})
        self.write({'state': 'confirm'})

    # @api.multi
    def button_end(self):
        for line in self.rent_line_ids:
            if not line.invoice_id:
                raise ValidationError(_('You should create invoice for all Rent lines before set the state to  End'))
        if self.rent_type in ('car', 'vehicle'):
            new_car = self.env['new.car'].browse(self.car_id.id)
            new_car.write({'state': 'confirm'})
            car_maintenance = self.env['car.maintenance'].search([('new_car_id', '=', self.car_id.id)])
            car_maintenance.write({'state': 'confirm', 'active': True})
        if self.rent_type in ('tank', 'vehicle'):
            new_tank = self.env['new.tank'].browse(self.tank_id.id)
            new_tank.write({'state': 'confirm'})
        self.write({'state': 'end'})

    # @api.one
    @api.depends('period_month', 'rent_start_date')
    def _compute_rent_end_date(self):
        if self.rent_start_date and self.period_month > 0:
            rent_start_date = datetime.datetime.strptime(self.rent_start_date, '%Y-%m-%d').date()
            period_month = relativedelta(months=self.period_month)
            self.rent_end_date = rent_start_date + period_month

    # @api.onchange('vehicle_id')
    # def onchange_vehicle_id(self):
    #     if self.vehicle_id:
    #         self.car_id = self.vehicle_id.new_car_id
    #         self.tank_id = self.vehicle_id.new_tank_id

    # @api.onchange('period_month', 'monthly_rent_amount', 'rent_start_date')
    # def onchange_visa_id(self):
    #     line_list = []
    #     count = 0
    #     if self.rent_start_date:
    #         while count < self.period_month:
    #             rent_start_date = datetime.datetime.strptime(self.rent_start_date, '%Y-%m-%d').date()
    #             dict = {'amount': self.monthly_rent_amount,
    #                     'payment_date': rent_start_date + relativedelta(months=count),
    #             }
    #             count += 1
    #             first_list = (0, _, dict)
    #             line_list.append(first_list)
    #     self.rent_line_ids = line_list

    # @api.one
    @api.constrains('period_month', 'monthly_rent_amount')
    def _check_values(self):
        if self.period_month <= 0:
            raise ValidationError(_('Rent Period by Months Can not be equal or less than zero'))
        if self.monthly_rent_amount <= 0:
            raise ValidationError(_('Monthly Rent Amount Can not be equal or less than zero'))

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].get('rent')
    #     return super(rent, self).create(vals)

    # @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise Warning(_('You cannot delete confirmed Rent'))
        return super(rent, self).unlink()


class rent_lines(models.Model):
    _name = 'rent.lines'

    amount = fields.Float(_('Amount'))
    payment_date = fields.Date(_('Payment Date'))
    rent_id = fields.Many2one('rent', _('Rent'))
    # invoice
    invoice_id = fields.Many2one('account.account', _('Customer Invoice'))

    # @api.multi
    def create_invoice(self):
        if self.rent_id.state == 'confirm':
            invoice_line = []
            name = ''
            if self.rent_id.car_id:
                name = self.rent_id.car_id.code
            if self.rent_id.tank_id:
                name = self.rent_id.tank_id.code
            if self.rent_id.vehicle_id:
                name = self.rent_id.vehicle_id.code

            invoice_line.append([0, False, {'name': name,
                                            'price_unit': self.amount,
                                            'account_id': self.rent_id.income_account_id.id,
                                            'quantity': 1}])
            # invoice
            invoice_id = self.env['account.account'].create({'partner_id': self.rent_id.customer_id.id,
                                                             'account_id': self.rent_id.customer_id.property_account_receivable.id,
                                                             'invoice_line': invoice_line,
                                                             'journal_id': self.rent_id.journal_id.id,
                                                             'type': 'out_invoice',
                                                             'date_invoice': self.payment_date})
            self.invoice_id = invoice_id.id
        else:
            raise ValidationError(_("You can not create invoice until rent is confirmed"))