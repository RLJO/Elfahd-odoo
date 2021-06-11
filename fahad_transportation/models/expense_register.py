# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class expense_register(models.Model):
    _name = 'expense.register'
    _description = 'Expense Register'
    _rec_name = 'code'
    _order = 'id desc'
    _inherit = ['mail.thread']

    code = fields.Char(_('Code'))
    expense_register_level = fields.Selection(
        [('car', _('Car')), ('tank', _('Tank')), ('trip', _('Trip')), ('loans', _('Loans')),
         ('traffic_violation', _('Traffic Violation'))],
        _('Expense Register Level'), change_default=True)

    loan_amount = fields.Float('Loan Amount')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    traffic_violation_car_id = fields.Many2one('new.car', 'Car')

    traffic_violation_amount = fields.Float('traffic violation amount ')
    trafic_expense_account_id = fields.Many2one('account.account', 'trafic expense account ')
    employee_share = fields.Float('Employee share')
    company_share = fields.Float('Company share')

    deduction_type = fields.Selection(
        [('full_employee', 'fully deduct from employee'), ('full_company', 'fully deduct from company'),
         ('employee_company', 'employee + company'), ], 'Deduction Type')

    trips_id = fields.Many2one('trips', _('Trips'), related="trip_details.trip_line_id")
    trip_name = fields.Char(_('Driver / Month'))
    car_id = fields.Many2one('new.car', _('Car'))
    plaque_no = fields.Char(_('Plate No'), related='car_id.plaque_no')
    tank_id = fields.Many2one('new.tank', _('Tank'))
    aramco_no = fields.Char(_('Aramco No'), related='tank_id.aramco_no')
    payment_method = fields.Selection([('bank_cash', 'Bank or Cash'),
                                       ('credit', 'Credit')], 'Payment Method', required=1)
    liquidity_account = fields.Many2one('account.account', 'Liquidity Account', domain=[('type', '=', 'liquidity')])
    partner_id = fields.Many2one('res.partner', 'Supplier', domain=[('supplier', '=', 'true')])
    location_id = fields.Many2one('stock.location', 'Location')
    location_account = fields.Many2one('account.account', 'Location Account', domain=[('type', '=', 'other')])
    journal_id = fields.Many2one('account.journal', _('Journal'))
    date = fields.Datetime('Date', required=1)

    expense_register_line_ids = fields.One2many('expense.register.lines', 'expense_register_id',
                                                _('Expense Register Lines'))

    note = fields.Html('Note')
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('closed', 'Closed')], 'State', default='draft', track_visibility='onchange')
    trip_details = fields.Many2one('trips.line', 'Trips Aramco Invoice Number')
    no_expense = fields.Float('No of Expenses', multi='line')
    total_expense = fields.Float('Total of Expenses', multi='line')



    # @api.one
    @api.depends('traffic_violation_amount', 'employee_share')
    def _get_company_share(self):
        if (
                    self.traffic_violation_amount and self.employee_share) and self.traffic_violation_amount > self.employee_share:
            self.company_share = self.traffic_violation_amount - self.employee_share
        else:
            self.company_share = 0.0

    # @api.one
    @api.constrains('traffic_violation_amount', 'employee_share')
    def _check_company_share(self):
        if self.deduction_type == 'employee_company':
            if self.employee_share >= self.traffic_violation_amount:
                raise ValidationError(_('deduction from employee must be less than traffic violation amount'))

    @api.depends('trips_id')
    def _get_trip_name(self):
        for record in self:
            record.trip_name = (record.trips_id.driver_id.name or '') + "[" + (record.trips_id.month or '' + "]")

    @api.depends('expense_register_line_ids')
    def _get_lines(self):
        for record in self:
            no = 0
            total = 0
            for line in record.expense_register_line_ids:
                no += 1
                total += line.total
            record.no_expense = no
            record.total_expense = total


    # @api.one
    def button_review(self):
        if self.expense_register_level not in ['loans', 'traffic_violation'] and (not self.expense_register_line_ids):
            raise ValidationError(_("You have to enter at least one line expense"))
        for record in self.expense_register_line_ids:
            if self.car_id:
                record.new_car_id = self.car_id.id
        self.code = self.env['ir.sequence'].get('expense.register')
        self.write({'state': 'reviewed'})

    def move_line(self, name, amount, is_dr, account_id, partner=None):
        return {
            'name': name,
            'debit': is_dr and amount or 0.0,
            'credit': not is_dr and amount or 0.0,
            'account_id': account_id,
            'partner_id': partner
        }

    # @api.one
    def button_confirm(self):
        vals = {}
        line_vals = {}
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']
        if self.expense_register_level == 'trip':
            self.new_car_id = self.trip_details.vehicle_id.new_car_id.id
            self.car_id = self.trip_details.vehicle_id.new_car_id.id
            self.tank_id = self.trip_details.vehicle_id.new_tank_id.id
            # if self.trips_id.state not in ('complete', 'confirmed'):
            #     raise ValidationError(_("Trip must be confirmed or completed"))
            if self.trip_details.vehicle_id.new_car_id.ownership == 'private':
                for record in self.expense_register_line_ids:
                    record.new_line_id = self.trip_details.vehicle_id.new_car_id.id
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.trip_details.vehicle_id.new_car_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        if self.payment_method == 'bank_cash':
                            line_vals['account_id'] = self.liquidity_account.id
                        elif self.payment_method == 'credit':
                            line_vals['account_id'] = self.partner_id.property_account_payable.id
                            line_vals['partner_id'] = self.partner_id.id
                        account_move_line.create(line_vals)
            if self.trip_details.vehicle_id.new_car_id.ownership == 'external':
                for record in self.expense_register_line_ids:
                    record.new_line_id = self.trip_details.vehicle_id.new_car_id.id
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.trip_details.vehicle_id.new_car_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        if self.payment_method == 'bank_cash':
                            line_vals['account_id'] = self.liquidity_account.id
                        elif self.payment_method == 'credit':
                            line_vals['account_id'] = self.partner_id.property_account_payable.id
                            line_vals['partner_id'] = self.partner_id.id
                        account_move_line.create(line_vals)
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.trip_details.vehicle_id.new_car_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['partner_id'] = self.trip_details.vehicle_id.new_car_id.external_ownership.id
                        line_vals[
                            'account_id'] = self.trip_details.vehicle_id.new_car_id.external_ownership.property_account_payable.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
        if self.expense_register_level == 'car':
            if self.car_id.ownership == 'private':
                for record in self.expense_register_line_ids:
                    record.new_line_id = self.car_id.id
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.car_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        if self.payment_method == 'bank_cash':
                            line_vals['account_id'] = self.liquidity_account.id
                        elif self.payment_method == 'credit':
                            line_vals['account_id'] = self.partner_id.property_account_payable.id
                            line_vals['partner_id'] = self.partner_id.id
                        account_move_line.create(line_vals)
            if self.car_id.ownership == 'external':
                for record in self.expense_register_line_ids:
                    record.new_line_id = self.car_id.id
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.car_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        if self.payment_method == 'bank_cash':
                            line_vals['account_id'] = self.liquidity_account.id
                        elif self.payment_method == 'credit':
                            line_vals['account_id'] = self.partner_id.property_account_payable.id
                            line_vals['partner_id'] = self.partner_id.id
                        account_move_line.create(line_vals)
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.car_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['partner_id'] = self.car_id.external_ownership.id
                        line_vals['account_id'] = self.car_id.external_ownership.property_account_payable.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
        if self.expense_register_level == 'tank':
            if self.tank_id.ownership == 'external':
                for line in self.expense_register_line_ids:
                    vals = {
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                        'line_id': [],
                    }
                    name_first_journal = ' تسجيل مصروف على تانك' + str(self.tank_id.aramco_no)
                    vals['line_id'].append((0, _, self.move_line(name_first_journal, line.total, True,
                                                                 line.expense_account.id)))
                    if self.payment_method == 'bank_cash':
                        vals['line_id'].append((0, _, self.move_line(name_first_journal, line.total, False,
                                                                     self.liquidity_account.id)))
                    if self.payment_method == 'credit':
                        vals['line_id'].append((0, _, self.move_line(name_first_journal, line.total, False,
                                                                     self.partner_id.property_account_payable.id,
                                                                     self.partner_id.id)))
                    account_move.create(vals)
                    vals['line_id'] = []
                    name_second_journal = 'تحميل مصروف تانك ' + str(self.tank_id.aramco_no) + 'على المالك'
                    vals['line_id'].append((0, _, self.move_line(name_second_journal, line.total, True,
                                                                 self.tank_id.tank_owner.property_account_payable.id,
                                                                 self.tank_id.tank_owner.id)))
                    vals['line_id'].append((0, _, self.move_line(name_second_journal, line.total, False,
                                                                 line.expense_account.id)))
                    account_move.create(vals)

            if self.tank_id.ownership == 'private':
                for record in self.expense_register_line_ids:
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.tank_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        if self.payment_method == 'bank_cash':
                            line_vals['account_id'] = self.liquidity_account.id
                        elif self.payment_method == 'credit':
                            line_vals['account_id'] = self.partner_id.property_account_payable.id
                            line_vals['partner_id'] = self.partner_id.id
                        account_move_line.create(line_vals)
            if self.car_id.ownership == 'external':
                for record in self.expense_register_line_ids:
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.tank_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        if self.payment_method == 'bank_cash':
                            line_vals['account_id'] = self.liquidity_account.id
                        elif self.payment_method == 'credit':
                            line_vals['account_id'] = self.partner_id.property_account_payable.id
                        account_move_line.create(line_vals)
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Code: " + self.tank_id.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = record.total
                        line_vals['credit'] = 0.0
                        line_vals['partner_id'] = self.tank_id.tank_owner.id
                        line_vals['account_id'] = self.tank_id.tank_owner.property_account_payable.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.total
                        line_vals['account_id'] = record.expense_account.id
                        account_move_line.create(line_vals)
        # if self.expense_register_level == 'trip':
        #    if self.trips_id.state not in ['confirmed', 'complete']:
        #        raise ValidationError(_("trip must be confirmed or completed !!"))
        if self.expense_register_level == 'loans':
            if self.loan_amount == 0:
                raise ValidationError(_("Amount can not equal to zero"))
            if self.employee_id.state != 'confirm' or (not self.employee_id.active):
                raise ValidationError(_("Employee statues must be confirmed + active"))
            contract_id = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True)])
            if not contract_id:
                raise ValidationError(_("the employee does not have a contract"))
            # Journal Entry
            vals.update({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'period_id': account_move._get_period(),
            })
            move = account_move.create(vals)
            if move:
                line_vals['move_id'] = move.id
                line_vals['name'] = 'قرض شخصى للموظف  %s'.decode('utf-8') % (self.employee_id.name)
                line_vals['period_id'] = account_move._get_period()
                line_vals['debit'] = self.loan_amount
                line_vals['credit'] = 0.0
                line_vals['account_id'] = self.employee_id.loan_account_id.id
                account_move_line.create(line_vals)
                line_vals['debit'] = 0.0
                line_vals['credit'] = self.loan_amount
                line_vals['account_id'] = self.liquidity_account.id
                account_move_line.create(line_vals)
            commission_line_vals = {
                'date': self.date,
                'amount': self.loan_amount,
                'contract_id': contract_id.id,
                'cause': 'سلفه شخصيه'
            }
            self.env['loan.line'].create(commission_line_vals)

        if self.expense_register_level == 'traffic_violation':
            contract_id = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True)])
            if not contract_id:
                raise ValidationError(_("the employee does not have a contract"))
            if self.traffic_violation_amount == 0:
                raise ValidationError(_("traffic violation amount must be greater than zero"))
            employee_amount = self.deduction_type == 'full_employee' and self.traffic_violation_amount or self.employee_share
            company_amount = self.deduction_type == 'full_company' and self.traffic_violation_amount or \
                             self.traffic_violation_amount - self.employee_share
            employee_account = self.employee_id.loan_account_id.id if self.deduction_type in ['full_employee',
                                                                                              'employee_company'] else False
            company_account = self.trafic_expense_account_id.id if self.deduction_type in ['full_company',
                                                                                           'employee_company'] else False
            name = "تسجيل مخالفه مروريه على الموظف  %s".decode('utf-8') % self.employee_id.name
            if self.deduction_type == 'full_company':
                name = 'تسجيل مخالفه مروريه'.decode('utf-8')
            if self.deduction_type == 'employee_company':
                name = 'قرض شخصى للموظف'.decode('utf-8')

            # Journal Entry
            vals.update({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'period_id': account_move._get_period(),
            })
            move = account_move.create(vals)
            if move:
                line_vals['move_id'] = move.id
                line_vals['name'] = name
                line_vals['period_id'] = account_move._get_period()
                line_vals['credit'] = 0.0
                if employee_account:
                    line_vals['debit'] = employee_amount
                    line_vals['account_id'] = employee_account
                    account_move_line.create(line_vals)
                if company_account:
                    line_vals['debit'] = company_amount
                    line_vals['account_id'] = company_account
                    account_move_line.create(line_vals)
                line_vals['debit'] = 0.0
                line_vals['credit'] = self.traffic_violation_amount
                line_vals['account_id'] = self.liquidity_account.id
                account_move_line.create(line_vals)
            cause = 'مخالفه مروريه على الموظف %s'.decode('utf-8') % self.employee_id.name
            if self.deduction_type == 'employee_company':
                cause = 'اكتب " جزء من مخالفه مروريه على الموظف %s'.decode('utf-8') % self.employee_id.name
            if self.deduction_type in ['full_employee', 'employee_company']:
                commission_line_vals = {
                    'date': self.date,
                    'amount': employee_amount,
                    'contract_id': contract_id.id,
                    'cause': cause
                }
                self.env['loan.line'].create(commission_line_vals)
        self.write({'state': 'confirmed'})

    # @api.one
    def button_close(self):
        self.write({'state': 'closed'})

    # @api.one
    def button_draft(self):
        self.write({'state': 'draft'})

    # @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise Warning(_('You cannot delete confirmed expense register'))
        return super(expense_register, self).unlink()




class expense_register_lines(models.Model):
    _name = 'expense.register.lines'
    _description = 'Expense Register Lines'

    expense_register_id = fields.Many2one('expense.register', _('Expense Register'))
    new_car_id = fields.Many2one('new.car', _('Linked Car'), related='expense_register_id.car_id', store=True)
    tank_id = fields.Many2one('new.tank', 'Tank', related='expense_register_id.tank_id', store=True)
    expense_name = fields.Many2one('expenses', _('Expense Name'))
    # TODO expense_account constraints
    expense_account = fields.Many2one('account.account', string='Expense Account')
    number = fields.Integer(_('Quantity'), required=1, default="1")
    amount = fields.Float(_('Amount'), required=1)
    total = fields.Float(_('Total'))
    invoice = fields.Char(_('Invoice'), size=20)
    filling_station = fields.Char(_('Filling Station'), size=10)
    notes = fields.Char(_('Notes'), size=15)
    trip_details = fields.Many2one('trips.line', 'Aramco Number', related='expense_register_id.trip_details')
    trip_id = fields.Many2one('trips', _('Trip'), related='expense_register_id.trips_id', store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('closed', 'Closed')], 'State', default='draft', related="expense_register_id.state", store=True)
    date = fields.Datetime('Date', related='expense_register_id.date')

    
    # @api.one
    @api.depends('number', 'amount')
    def _compute_total(self):
        self.total = self.number * self.amount

    # @api.one
    @api.constrains('number')
    def _check_lines(self):
        for record in self:
            if record.number <= 0:
                raise ValidationError(_("Number must be +ve and bigger than 0"))
            if record.amount <= 0:
                raise ValidationError(_("Amount must be +ve and bigger than 0"))
            if len(str(record.amount)) > 7:
                raise ValidationError(_("Amount Should be 5 digits only."))
            if record.expense_name.expense_nature == 'capital' and record.expense_register_id.expense_register_level == 'trip':
                raise ValidationError(_("You can not select Expense Name that is capital when Expense Register Level"
                                        " is Trip"))
            if record.expense_name.expense_type == 'car':
                if self.expense_register_id.car_id.sale_method == 'rent':
                    raise ValidationError(_("We shouldn't record a capital expense in a rented car"))
            if record.expense_name.expense_type == 'tank':
                if self.expense_register_id.tank_id.sale_method == 'rent':
                    raise ValidationError(_("We shouldn't record a capital expense in a rented tank"))


class new_car(models.Model):
    _inherit = 'new.car'

    expense_expense = fields.One2many('expense.register.lines', 'new_car_id', 'Expenses from Expenses')
