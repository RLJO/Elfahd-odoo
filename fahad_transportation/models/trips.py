# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import date


class trips(models.Model):
    _name = "trips"
    _inherit = ['mail.thread']
    _description = "Trips"
    _rec_name = "code"
    _order = "id desc"

    code = fields.Char('Code', readonly=1)
    month = fields.Selection([('1', _('January')), ('2', _('February')), ('3', _('March')),
                              ('4', _('April')), ('5', _('May')), ('6', _('June')),
                              ('7', _('July')), ('8', _('August')), ('9', _('September')),
                              ('10', _('October')), ('11', _('November')), ('12', _('December'))], _('Month'))
    date = fields.Date('Date')
    customer_id = fields.Many2one('res.partner', 'Customer', required=1)
    journal_id = fields.Many2one('account.journal', 'Journal')
    loss_account = fields.Many2one('account.account', 'Loss Account')
    other_account = fields.Many2one('account.account', 'Other Income Account')
    trip_discount = fields.Selection([('yes', 'Yes'), ('no', 'No')], '10% Discount')
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('complete', 'Complete'),
                              ('closed', 'Closed')], 'State', default='draft', track_visibility='onchange')
    expenses_ids = fields.One2many('expense.register.lines', 'trip_id', string='Expenses',
                                   domain=[('state', 'in', ['confirmed'])])
    trips_line_ids = fields.One2many('trips.line', 'trip_line_id', 'Trips', required=True)
    new_line_id = fields.Many2one('new.line', _("New Line"), domain=[('state', '=', 'confirm')])
    driver_id = fields.Many2one('hr.employee', 'Driver', required=True)
    arabic_name = fields.Char('Arabic name', related='driver_id.arabic_name')
    driver_code = fields.Integer('Driver ID', related='driver_id.code')
    aramco_no = fields.Char('Aramco No', related='driver_id.aramco_no')
    plat_no = fields.Char('Plat No.', store=True)
    number_of_trips = fields.Integer('Number of trips')
    total_amount = fields.Float('Total amount')
    aramco_deduction = fields.Float('Aramco deduction')
    deduct_from_driver = fields.Float('Deduct from driver')
    product = fields.Char('Product')
    tank_aramco_no = fields.Char('Tank Aramco No.')
    year = fields.Integer('Year')
    diesel_difference_ids = fields.One2many('diesel.difference.lines', 'expense_id', string='Diesel Difference')

    # @api.one
    @api.depends('driver_id')
    def _function_fields(self):
        self.plat_no = False
        self.tank_aramco_no = False
        self.product = False
        self.total_amount = False
        self.aramco_deduction = False
        self.deduct_from_driver = False
        self.Number_of_trips = False
        if self.trips_line_ids:
            self.number_of_trips = len(self.trips_line_ids)
            self.plat_no = self.trips_line_ids[0].vehicle_id.car_plaque_no
            self.tank_aramco_no = self.trips_line_ids[0].vehicle_id.new_tank_id.aramco_no
            self.product = self.trips_line_ids[0].product_id
            self.total_amount = sum([l.total_amount for l in self.trips_line_ids])
            self.aramco_deduction = sum([l.discounted_aramco for l in self.trips_line_ids])
            self.deduct_from_driver = sum([l.deduct_driver for l in self.trips_line_ids])

    # @api.one
    @api.constrains('trips_line_ids', 'driver_id')
    def _check_trips_line_ids(self):
        if not self.trips_line_ids:
            raise ValidationError(_("You should insert one line at least"))

    @api.multi
    def button_review(self):
        for rec in self:
            if not rec.driver_id.contract_id.active:
                raise ValidationError(_('Selected Driver Has no active contract‬‬'))
            seq = rec.env['ir.sequence'].get('trip')
            rec.code = str(date.today().year) + "-" + seq
        self.write({'state': 'reviewed'})

    def button_confirm(self):
        if self.driver_id.active == False:
            raise ValidationError(_("You can not confirm the trip because the driver is not active"))
        if len(self.env['hr.contract'].search([('employee_id', '=', self.driver_id.id), ('active', '=', True)])) == 0:
            raise ValidationError(_("The driver must have an active contract"))
        # contract_date_to = False
        # contract_date_from = False
        # for line in self.trips_line_ids:
        # if line.loaded_date > contract_date_to or line.loaded_date < contract_date_from:
        # raise ValidationError(_("un loaded date must belong to driver contract period"))
        vals = {}
        line_vals = {}
        dict = {}
        vals_dict = {}
        account_move = self.env['account.move']
        if self.trips_line_ids:
            current_date = self.trips_line_ids[0].loaded_date
        account_move_line = self.env['account.move.line']
        for record in self.trips_line_ids:
            self.env['vehicle.history'].create({
                'driver_id': record.driver_id.id,
                'date': fields.Date.today(),
                'vehicle_id': record.vehicle_id.id,
                'car_id': record.car_id.id,
                'vehicle_state': record.vehicle_state,
                # 'car_code': False,
                'line_id': record.line_id.id
            })
            current_date = record.loaded_date
            if int(str(record.loaded_date).split('-')[1]) != int(self.month):
                raise ValidationError(_('‫‪Trips date must belong to the selected month'))
            if record.deduct_owner != 'no' and record.vehicle_id.new_car_id.ownership == 'private':
                raise ValidationError(_(
                    '‫‪‫‪The‬‬ ‫‪car‬‬ ‫‪is‬‬ ‫‪owned‬‬ ‫‪by‬‬ ‫‪the‬‬ ‫‪company‬‬ ‫‪and‬‬ ‫‪cannot‬‬ ‫‪deduct‬‬ ‫‪anything‬‬ ‫‪from‬‬ ‫‪the‬‬ ‫‪owner‬‬‬‬'))
            if record.vehicle_id.new_car_id.ownership == 'private':
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': current_date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Trip Code:" + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['debit'] = record.total_amount
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = record.total_amount
                    line_vals['account_id'] = record.line_id.income_account.id
                    account_move_line.create(line_vals)
            elif record.vehicle_id.new_car_id.ownership == 'external':
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': current_date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Trip Code:" + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['debit'] = record.total_amount
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = record.total_amount
                    line_vals['partner_id'] = record.vehicle_id.new_car_id.external_ownership.id
                    line_vals[
                        'account_id'] = record.vehicle_id.new_car_id.external_ownership.property_account_payable.id
                    account_move_line.create(line_vals)
        self.write({'state': 'confirmed'})
        contract_id = self.env['hr.contract'].search([('employee_id', '=', self.driver_id.id), ('active', '=', True)])
        if not contract_id:
            raise ValidationError(_("This driver must have an active contract"))
        if self.driver_id.active != True:
            raise ValidationError(_("to confirm the trip the driver must be active"))
        for line in self.trips_line_ids:
            line_vals = {
                'date': line.loaded_date,
                'line_id': line.line_id.id,
                'trip_code': self.code,
                'vehicle_id': line.vehicle_id.id,
                'amount': line.line_id.driver_commission,
                'contract_id': contract_id.id,
            }
            self.env['commission.line'].create(line_vals)

    # @api.one
    def button_complete(self):
        vals = {}
        line_vals = {}
        dict = {}
        vals_dict = {}
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']
        if self.trips_line_ids:
            current_date = self.trips_line_ids[0].loaded_date
        for record in self.trips_line_ids:
            current_date = record.loaded_date
            if record.deduct_driver > 0:
                contract_obj = self.env['hr.contract'].search(
                    [('employee_id', '=', self.driver_id.id), ('active', '=', True)])
                for obj in contract_obj:
                    contract_id = obj.id
                dict.update({
                    'date': current_date,
                    'line_id': record.line_id.id,
                    'trip_code': self.code,
                    'vehicle_id': record.vehicle_id.id,
                    'amount': record.deduct_driver,
                    'note': 'Trip Code:' + self.code,
                    'cause': 'Trip Code:' + self.code,
                    'contract_id': contract_id or False,
                })
                self.env['commission.line'].create(dict)
            elif record.deduct_driver < 0:
                contract_obj = self.env['hr.contract'].search(
                    [('employee_id', '=', self.driver_id.id), ('active', '=', True)])
                for obj in contract_obj:
                    contract_id = obj.id
                dict.update({
                    'date': current_date,
                    'line_id': record.line_id.id,
                    'trip_code': self.code,
                    'vehicle_id': record.vehicle_id.id,
                    'amount': abs(record.deduct_driver),
                    'note': 'Trip Code:' + self.code,
                    'cause': 'Trip Code:' + self.code,
                    'contract_id': contract_id or False,
                })
                self.env['deduction.line'].create(dict)
                ######## Journal Entry if Deduction from driver ###########
                if record.vehicle_id.new_car_id.ownership == 'private':
                    if not self.driver_id.can_take_loan:
                        raise ValidationError(_("this driver can not take loan !!"))
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': current_date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = _("Deduct from driver")
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['partner_id'] = False
                        line_vals['debit'] = abs(record.deduct_driver)
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = self.driver_id.loan_account_id.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = abs(record.deduct_driver)
                        line_vals['account_id'] = self.loss_account.id
                        account_move_line.create(line_vals)
            if record.vehicle_id.new_car_id.ownership == 'external':
                if record.deduct_owner != 'no':
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': current_date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Trip Code:" + self.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['partner_id'] = record.vehicle_id.new_car_id.external_ownership.id
                        line_vals['debit'] = record.deduct_owner_amount if record.deduct_owner == 'fixed' else (
                                                                                                                       record.deduct_owner_amount * record.total_amount) / 100
                        line_vals['credit'] = 0.0
                        line_vals[
                            'account_id'] = record.vehicle_id.new_car_id.external_ownership.property_account_payable.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = record.deduct_owner_amount if record.deduct_owner == 'fixed' else (
                                                                                                                        record.deduct_owner_amount * record.total_amount) / 100
                        line_vals['account_id'] = record.line_id.income_account.id
                        account_move_line.create(line_vals)
                if record.discounted_aramco > 0:
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': current_date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Trip Code:" + self.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['partner_id'] = self.customer_id.id
                        line_vals['debit'] = abs(record.discounted_aramco)
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = self.customer_id.property_account_receivable.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = abs(record.discounted_aramco)
                        line_vals['partner_id'] = record.vehicle_id.new_car_id.external_ownership.id
                        line_vals[
                            'account_id'] = record.vehicle_id.new_car_id.external_ownership.property_account_payable.id
                        account_move_line.create(line_vals)
                elif record.discounted_aramco < 0:
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': current_date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Trip Code:" + self.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = abs(record.discounted_aramco)
                        line_vals['credit'] = 0.0
                        line_vals['partner_id'] = record.vehicle_id.new_car_id.external_ownership.id
                        line_vals[
                            'account_id'] = record.vehicle_id.new_car_id.external_ownership.property_account_payable.id
                        account_move_line.create(line_vals)
                        line_vals['partner_id'] = self.customer_id.id
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = abs(record.discounted_aramco)
                        line_vals['account_id'] = self.customer_id.property_account_receivable.id
                        account_move_line.create(line_vals)
            elif record.vehicle_id.new_car_id.ownership == 'private':
                if record.discounted_aramco > 0:
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': current_date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Trip Code:" + self.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['partner_id'] = self.customer_id.id
                        line_vals['debit'] = abs(record.discounted_aramco)
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = self.customer_id.property_account_receivable.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = abs(record.discounted_aramco)
                        line_vals['account_id'] = self.other_account.id
                        account_move_line.create(line_vals)
                elif record.discounted_aramco < 0:
                    vals.update({
                        'journal_id': self.journal_id.id,
                        'date': current_date,
                        'period_id': account_move._get_period(),
                    })
                    move = account_move.create(vals)
                    if move:
                        line_vals['move_id'] = move.id
                        line_vals['name'] = "Trip Code:" + self.code
                        line_vals['period_id'] = account_move._get_period()
                        line_vals['debit'] = abs(record.discounted_aramco)
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = self.loss_account.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = abs(record.discounted_aramco)
                        line_vals['partner_id'] = self.customer_id.id
                        line_vals['account_id'] = self.customer_id.property_account_receivable.id
                        account_move_line.create(line_vals)
        self.write({'state': 'complete'})

    # @api.one
    def button_close(self):
        self.write({'state': 'closed'})

    # @api.one
    def button_draft(self):
        self.write({'state': 'draft'})

    # @api.multi
    def unlink(self):
        for record in self:
            if record.state in ['confirmed', 'complete']:
                raise ValidationError(_('You cannot delete confirmed / completed trips'))
        self.trips_line_ids.unlink()
        return super(trips, self).unlink()

    # @api.multi
    def write(self, vals):
        if self.env['new.car'].check_validation():
            raise ValidationError("")
        self._check_trips_line_ids()
        if vals.get('state', False):
            for l in self.trips_line_ids:
                l.write({'state': vals['state']})
        return super(trips, self).write(vals)


class trips_line(models.Model):
    _name = 'trips.line'
    _description = "Trips Line"
    _rec_name = 'aramco_invoice_no'
    _inherit = ['mail.thread']

    expense_register_id = fields.Many2one('expense.register', _('Expense Register'))
    button_flag = fields.Boolean(_('Button Flag'), default=False)

    # @api.v7
    def create_expense_register(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'fahad_transportation',
                                                                  'view_expense_register_form')
        view_id = res and res[1] or False
        ctx = {
            'default_expense_register_level': 'trip',
            'default_trip_details': ids[0],
        }
        return {
            'domain': "[]",
            'name': _('New Expense'),
            # 'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'expense.register',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }

    # line_id = fields.Many2one('new.line', 'Line', domain=[('state', '=', 'confirm')], )
    # route_number = fields.Char(string='Route Number', related='line_id.route_number')
    # ToDo make another domain on vehicle_id that get vehicle related to line_id
    vehicle_id = fields.Many2one('new.vehicle', 'Vehicle')
    vehicle_state = fields.Selection([('received', 'Received'), ('delivered', 'Delivered')], string='Vehicle State',
                             default='received')
    car_id = fields.Many2one('new.car', 'Car')
    private = fields.Boolean(string='Private')

    # ToDo driver_id that related to this car
    loaded_amount = fields.Float('Loaded Amount', required=1)
    loaded_date = fields.Date('Loaded Date', required=1)
    unloaded_amount = fields.Float('UnLoaded Amount', required=1)
    trips_no = fields.Float('Trips No')
    total_amount = fields.Float('Total Amount', required=1)
    discounted_aramco = fields.Float('Discounted Aramco', required=1)
    net_amount = fields.Float('Net Amount')

    # @api.one
    @api.depends('total_amount', 'discounted_aramco', 'new_line_id', 'car_id')
    def _compute_net_amount(self):

        self.net_amount = self.total_amount + self.discounted_aramco
        # if self.car_id:
        # self.car_id = self.new_line_id.new_car_id

    diff_liter = fields.Float('Diff in Liter')

    # @api.one
    @api.depends('loaded_amount', 'unloaded_amount')
    def _compute_diff_liter(self):
        self.diff_liter = self.loaded_amount - self.unloaded_amount

    average_diff_liter = fields.Float('Average Diff in Liter')

    # @api.one
    @api.depends('discounted_aramco', 'diff_liter')
    def _compute_average_diff_liter(self):
        if self.diff_liter > 0:
            self.average_diff_liter = self.discounted_aramco / self.diff_liter
        else:
            self.average_diff_liter = 0

    deduct_driver = fields.Float('Deduct from Driver', required=1)
    product_id = fields.Char('Product')
    aramco_invoice_no = fields.Char('Aramco Invoice No', required=1)
    _sql_constraints = [
        ('aramco_invoice_no_unique', 'unique(aramco_invoice_no)', 'Aramco invoice No must be unique.'),
    ]
    deduct_owner = fields.Selection([('no', 'No'), ('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Deduct Owner',
                                    required=1, default='no')
    deduct_owner_amount = fields.Float('Fixed / Percentage')
    # deduct_owner_percentage = fields.Float('Percentage')
    trip_line_id = fields.Many2one('trips', 'Trips ID', on_delete='cascade')
    line_id = fields.Many2one('new.line', 'Line')
    new_line_id = fields.Many2one('new.line', 'Line', related='trip_line_id.new_line_id')
    driver_id = fields.Many2one('hr.employee', _('Driver'), related='trip_line_id.driver_id')
    route_number = fields.Char(string='Route Number', related='line_id.route_number')
    state = fields.Selection(
        [('draft', 'Draft'), ('reviewed', 'Reviewed'), ('confirmed', 'Confirmed'), ('complete', 'Complete'),
         ('closed', 'Closed')], string='State', default='draft')
    date = fields.Date(_('Date'), related='trip_line_id.date')
    customer_id = fields.Many2one('res.partner', 'Customer', related='trip_line_id.customer_id')
    journal_id = fields.Many2one('account.journal', 'Journal', related='trip_line_id.journal_id')
    loss_account = fields.Many2one('account.account', 'Loss Account', related='trip_line_id.loss_account')
    other_account = fields.Many2one('account.account', 'Other Income Account', related='trip_line_id.other_account')
    trip_discount = fields.Selection([('yes', 'Yes'), ('no', 'No')], '10% Discount',
                                     related='trip_line_id.trip_discount')
    arrival_date = fields.Datetime('Arrival Date')

    # @api.one
    @api.constrains('unloaded_amount', 'loaded_amount', 'trips_no', 'total_amount', 'deduct_owner',
                    'deduct_owner_amount')
    def _check_digit_and_value(self):
        if self.env['new.car'].check_validation():
            raise ValidationError("")
        # if self.unloaded_amount > self.loaded_amount:
        # raise ValidationError(_("Unloaded amount cannot be larger than loaded amount"))
        # if self.trips_no == 0:
        # raise ValidationError(_("Trips Amount cannot be 0"))
        if self.total_amount == 0:
            raise ValidationError(_("Total Amount cannot be 0"))
        if self.deduct_owner >= 'fixed':
            if self.deduct_owner_amount >= self.total_amount:
                raise ValidationError(_("Fixed cannot exceed Total Amount"))
        elif self.deduct_owner >= 'percentage':
            if self.deduct_owner_amount >= 100:
                raise ValidationError(_("Percentage cannot exceed 100"))
