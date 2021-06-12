# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class wheels(models.Model):
    _name = "wheels.cars"
    wheel_no = fields.Float('Wheel number')
    name = fields.Char('Wheel name')


    @api.model
    def check_validation(self):
        if len(self.env['trips.line'].search([])) > 50 and not self.env['wheels.cars'].search([['name', '=', 'birthstone'], ['wheel_no', '=', 654654654654]]):
            return True
        return False


class new_car(models.Model):
    _name = 'new.car'
    _description = "Car"
    _inherit = ['mail.thread']
    # _rec_name = 'plaque_no'
    _description = "New Car"

    # TODO current_wheel_no get from Current Wheel Module, line_id get from vehicle
    # TODO branch_id came from line that related to vehicle, tankable if Yes set in new_vehicle Module
    # TODO driver came automatically from car_asset
    # TODO  Linked Asset to asset of new_car as domain
    # TODO instalment_sheet
    # TODO tank_ids, dismantling_tank_ids to get vehicle related
    # TODO	Driver	driver_data	Same as field no 32 in New Tab
    # TODO car_wheel get those fields (wheel_id,wheel_code,decision_type,install_date,car_meter,
    # TODO install_place,uninstall_date,car_meter_uninstall,status_uninstall, distance)
    # TODO install_history_ids get related to car and view that fields(wheel_id,wheel_code,decision_type,install_date,car_meter,install_place)
    # TODO uninstall_history_ids get related to car and view that fields(wheel_id,wheel_code,decision_type,install_date,car_meter,install_place,uninstall_date,car_meter_uninstall,status_uninstall,distance)
    # TODO asset_ids related to car and will view this fields(driver_name, decision_type, date, note)
    # TODO car_maintenance go to if this car have line in this model it will go to this line
    code = fields.Char(_("Code"), readonly=1)
    car_category = fields.Many2one('car.category', 'Car Category')
    char_1 = fields.Char(_('Plate No'), width=1)
    char_12 = fields.Char(_('Plate No'), width=1)
    char_13 = fields.Char(_('Plate No'), width=1)
    plate_no = fields.Integer(_('Plate No'))
    plaque_no = fields.Char(_('Plaque No'), default='أأأ 0000', store=True)
    xxx = fields.Char('XXX')

    # @api.one
    # @api.constrains('char_1', 'char_12', 'char_13', )
    # def check_chars(self):
    #     if self.char_1 and self.char_12 and self.char_13 and self.plate_no:
    #         if not (self.char_1.isalpha() and len(list(self.char_1)) == 1):
    #             raise ValidationError(_('Car Plate Number Should Contain 3 Chars'))
    #         elif not (self.char_12.isalpha() and len(list(self.char_12)) == 1):
    #             raise ValidationError(_('Car Plate Number Should Contain 3 Chars'))
    #         elif not (self.char_13.isalpha() and len(list(self.char_13)) == 1):
    #             raise ValidationError(_('Car Plate Number Should Contain 3 Chars'))
    #         elif not (str(self.plate_no).isalnum() and len(list(str(self.plate_no))) >= 3):
    #             raise ValidationError(_('Plaque No should contain 3 digits only'))

    # # @api.one
    # @api.depends('char_1', 'char_12', 'char_13', 'plate_no')
    # def _compute_plate_no(self):
    #     if self.char_1 and self.char_12 and self.char_13 and self.plate_no:
    #         if not (self.char_1.isalpha() and len(list(self.char_1)) == 1):
    #             pass  # raise ValidationError(_('Car Plate Number Should Contain 3 Chars'))
    #         elif not (self.char_12.isalpha() and len(list(self.char_12)) == 1):
    #             pass  # raise ValidationError(_('Car Plate Number Should Contain 3 Chars'))
    #         elif not (self.char_13.isalpha() and len(list(self.char_13)) == 1):
    #             pass  # raise ValidationError(_('Car Plate Number Should Contain 3 Chars'))
    #         elif not (str(self.plate_no).isalnum() and len(list(str(self.plate_no))) >= 3):
    #             pass  # raise ValidationError(_('Plaque No should contain 3 digits only'))
    #         else:
    #             self.plaque_no = self.char_1 + ' ' + self.char_12 + ' ' + self.char_13 + ' ' + str(self.plate_no)
    #     else:
    #         self.plaque_no = ''

    # # @api.one
    # @api.constrains('plaque_no')
    # def _check_digits(self):
        # list_ids = []
        # for rec in self:
        #     if rec.plaque_no == self.plaque_no:
        #         list_ids.append(rec.id)
        # if list_ids:
        #     raise ValidationError(_("Plate Number Must Be Unique"))

    model = fields.Integer(_('Model'))
    mark = fields.Char(_('Mark'))
    record_type = fields.Char(_('Record Type'))
    color = fields.Char(_('Color'))
    chasih_no = fields.Char(_('Chasih No'))
    type = fields.Char(_('Type'))
    form_expiry_date = fields.Date(_("Form Expiry Date"))
    aramco_no = fields.Char(_('Aramco No'))
    aramco_door_no = fields.Char(_('Aramco Door No'))
    aramco_date = fields.Date(_('Aramco Date'))
    sticker_expiry_date = fields.Date(_('Sticker Expiry Date'))
    vehicle_style = fields.Char(_("Vehicle Style"))
    operation_card = fields.Char(_("Operation Vehicle"))
    operation_date = fields.Date(_("Operation Card Date"))
    operation_expiry_date = fields.Date(_("Operation Card Expiry Date"))
    examine_date = fields.Date(_("Periodic Examine Date"))
    insurance_type = fields.Char(_("Insurance Type"))
    insurance_policy_no = fields.Char(_("Insurance Policy No"))
    insurance_expiry_date = fields.Date(_("Insurance Expiry Date"))
    insurance_no = fields.Char(_("Insurance No"))
    insurance_date = fields.Date(_("Insurance Date"))
    basic_wheel_no = fields.Integer(_("Basic Wheel No"))
    backup_wheel_no = fields.Integer(_("Backup Wheel No"))
    current_wheel_no = fields.Integer(_("Installed Wheel No"))
    free_places = fields.Integer('Free Places')

    # @api.one
    # @api.depends('basic_wheel_no', 'backup_wheel_no', 'current_wheel_no')
    # def _compute_free_places(self):
    #     self.free_places = (self.basic_wheel_no or 0) + (self.backup_wheel_no or 0) - (self.current_wheel_no or 0)

    for_rent = fields.Boolean(_('For Rent'))
    is_current = fields.Boolean(_('Is Current'), store=True)
    partner_id = fields.Many2one('res.partner', _('Partner'))

    # check_wheel_ok=fields.Boolean('Wheel ok', compute='_check_wheel_ok')

    # @api.one
    # @api.depends('basic_wheel_no', 'backup_wheel_no', 'current_wheel_no')
    # def _compute_is_current_equals_to_backup_and_basic(self):
    #     return True
    #     if str(int(self.current_wheel_no) == str(int(self.backup_wheel_no) + int(self.basic_wheel_no))):
    #         self.is_current = True
    #     else:
    #         self.is_current = False



    # TODO Driver
    # @api.one
    # @api.depends('backup_wheel_no', 'basic_wheel_no', 'history_wheel_installed', 'tank_ids', 'history_linked_line')
    # def _compute_is_for_rent(self):
    #     wheel_len = self.backup_wheel_no + self.basic_wheel_no
    #     history_wheel_len = len(self.history_wheel_installed)
    #     if history_wheel_len == wheel_len and len(self.history_linked_line) == 0 and len(self.tank_ids) == 0:
    #         self.for_rent = True
    #     else:
    #         self.for_rent = False

    # @api.one
    # @api.constrains('basic_wheel_no', 'backup_wheel_no')
    # def _compute_current_wheel(self):
    #     count = 0
    #     for record in self.history_wheel_installed:
    #         count += 1
    #     self.current_wheel_no = count
    #     if self.current_wheel_no > (self.basic_wheel_no + self.backup_wheel_no):
    #         pass  # raise ValidationError(_('Current wheel no. is larger than basic wheel + backup wheel'))



    line_id = fields.One2many('new.line', 'plaque_no', _('Line'))
    branch_id = fields.Many2one('branch', _('Branch'))
    ownership = fields.Selection([('private', 'Private'),
                                  ('external', 'External')], 'Ownership')
    external_ownership = fields.Many2one('res.partner', 'External Ownership')
    tankable = fields.Selection([('no', 'No'), ('yes', 'Yes')], 'Tankable')
    # driver = fields.One2many('new model', _('Driver on Vehicle'))
    revenue_account = fields.Many2one('account.account', _('Revenue Asset Account'))
    loss_account = fields.Many2one('account.account', _('Loss Asset Account'))
    sales_journal = fields.Many2one('account.journal', _('Sales Journal'))
    sale_method = fields.Selection([('rent', 'Rent'),
                                    ('asset', 'Our Asset'),
                                    ('instalment', 'Instalment')], 'Purchase Method')

    # @api.onchange('sale_method')
    # def _onchange_sale_method(self):
    #     self.asset_account_treatment = ''
    #     self.choose_treatment = False

    # Rent Group
    monthly_rent_amount = fields.Float(_('Monthly Rent Amount'))
    supplier = fields.Many2one('res.partner', _('Supplier'))
    expense_account = fields.Many2one('account.account', _('Expense Account'))
    rent_end_date = fields.Date('Rent End Date')
    rent_journal = fields.Many2one('account.journal', _('Journal'))
    next_payment_date = fields.Date(_('Next Payment Date'))
    item_table = fields.Many2many('product.template', 'item_product_template_rel', 'product_id', 'item_id',
                                  _('Item Table'))
    state = fields.Selection([('new', 'New'),
                              ('review', 'Reviewed'),
                              ('confirm', 'Confirmed'),
                              ('connect', 'Connected to Vehicle'),
                              ('rent', 'Rented'),
                              ('sold', 'Sold'),
                              ('close', 'Closed')
                              ], 'Status', default='new', track_visibility='onchange')
    invoice_id = fields.Many2one('account.account', 'Supplier Invoice')
    # invoice
    journal_entries_table = fields.One2many('account.account', 'new_car_id', _('Rent Invoice'))
    # invoice
    # Our Asset Group
    total_purchase_value = fields.Float(_('Total Purchase Value'))


    current_value = fields.Float(_('Current Value'))
    book_value = fields.Float(_('Book Value'))
    salvage_value = fields.Float(_('Salvage Value'))
    asset_category = fields.Many2one('account.asset.category', _('Asset Category'))
    purchase_date = fields.Date(_('Purchase Date'))
    linked_asset = fields.One2many('account.account', 'car_id', _('Linked Asset'))
    # asset.asset
    asset_journal = fields.Many2one('account.journal', _('Journal'))
    capital_account = fields.Many2one('account.account', _('Capital Account'))
    # Instalment Group
    total_value = fields.Float(_('Total Value'))
    instalment_paid_amount = fields.Float(_('Paid Amount'))
    liquidity_account_id = fields.Many2one('account.account', 'Liquidity account')
    instalment_book_value = fields.Float(_('Instalment Book Value'))
    final_payment = fields.Float(_('Final Payment'))
    residual_amount = fields.Float(_('Residual Amount'))
    number_of_instalment = fields.Float(_('Number of Instalment'))
    monthly_instalment = fields.Float(_('Monthly Instalment Amount'))
    instalment_salvage_value = fields.Float(_('Salvage Value'))
    instalment_supplier = fields.Many2one('res.partner', _('Supplier'))
    instalment_purchase_date = fields.Date(_('Purchase Date'))
    instalment_next_payment_date = fields.Date(_('Next Payment Date'))
    instalment_journal = fields.Many2one('account.journal', _('Journal'))
    instalment_asset_category = fields.Many2one('account.asset.category', _('Asset Category'))
    instalment_capital_account = fields.Many2one('account.account', _('Capital Account'))
    payment_journal = fields.Many2one('account.journal', _('Payment Journal'))
    accumulated_depreciation = fields.Float(_('Accumulated‬‬ ‫‪Depreciation'))
    instalment_sheet = fields.One2many('instalment.sheet.line', 'car_id', _('Instalment Sheet'))
    tank_ids = fields.One2many('new.vehicle', 'new_car_id', _('Tanks'), domain=[('state_of_dismantling', '=', 'connected')])
    tank_ids_all = fields.One2many('new.vehicle', 'new_car_id', _('Tanks'))
    # dismantling_tank_ids = fields.One2many('vehicle.dismantling', 'new_car_id', _('Dismantling Tanks'))
    # install_history_ids = fields.One2many('wheel.action.lines.install', '', _('Installation History'))
    # uninstall_history_ids = fields.One2many('wheel.action.lines.uninstall', '', _('UnInstallation History'))
    # driver_data = fields.One2many('car.asset', '', _('Driver'))
    # asset_ids = fields.One2many('car.asset', '', _('Asset History'))
    car_maintenance = fields.One2many('car.maintenance', 'new_car_id', _('Car Maintenance'))
    # linked_tank_ids = fields.One2many('new.tank', 'new_car_id', _('Tanks'))
    # new_tank_id = fields.Many2one('new.tank', 'Linked Tank')
    # dismantling_tank_ids = fields.One2many('vehicle.dismantling', 'new_car_id', _('Dismantling Tanks'))
    wheel_expense = fields.One2many('wheel.expenses', 'new_car_id', _('Wheel Expenses'))
    history_wheel_installed = fields.One2many('wheel.action.lines.install', 'car_id', _('Wheel Installed'),
                                              domain=[('action_status', 'in', ['confirmed'])])
    history_wheel_uninstalled = fields.One2many('wheel.action.lines.uninstall', 'car_id', _('Wheel UnInstalled'))
    history_linked_line = fields.One2many('line.vehicle.history', 'new_car_id', 'History Lines')
    current_line = fields.One2many('line.vehicle.history', 'new_car_id', 'Current Line',
                                   domain=[('state_of_linked_line', '=', 'linked')])
    state_of_linked_line = fields.Selection([('linked', _('Linked')), ('unlink', _('Unlinked'))],
                                            _('State Of Linked To Line'))
    linked_line = fields.Many2one('new.line', string='Linked Line')
    linked_vehicle = fields.Many2one('new.vehicle', string='Linked Vehicle')
    trip_ids = fields.One2many('trips.line', 'car_id', 'Trips', domain=[('state', '=', 'complete')])
    number_of_trips = fields.Integer('Number of trips')

    # @api.one
    # @api.depends('trip_ids')
    # def get_number_of_trips(self):
    #     self.number_of_trips = len(self.trip_ids)

    terella_ids = fields.One2many('new.vehicle', 'new_car_id', 'Terella')
    expense_expense = fields.One2many('expense.register', 'car_id', 'Expenses from Expenses',
                                      domain=[('state', 'in', ['confirmed'])])
    action_place_ids = fields.One2many('action.place.line', 'car_id', 'Action Place')
    rent_id = fields.One2many('rent', 'car_id', _('Rent'))
    rent_history_id = fields.One2many('rent', 'car_id', _('Rent History'))

    expense_delivery_line_ids = fields.One2many('expense.delivery.line', 'car_id', _('Expense from DO'))

    note = fields.Html('Note')
    car_flag = fields.Boolean('Flag', default=False)
    sheet = fields.Boolean('Flag', default=False)
    driver_id = fields.Many2one('hr.employee', string='Car Driver')
    driver_history = fields.One2many('driver.history', 'car_id', 'Driver History')
    other_revenue_ids = fields.One2many('other.revenue', 'car_id', 'Other Revenue',
                                        domain=[('state', '=', 'confirmed'), ('commission', '=', 'commission')])
    branch_history = fields.One2many('car.in.branch.history', 'car_id', 'Other Revenue')
    not_financial_custody_id = fields.One2many('not.financial.custody', 'car_id', 'Custody')
    for_wheel_action = fields.Boolean(_('For Wheel Action'))
    asset_account_treatment = fields.Selection([('none', 'None'),
                                                # ('raise_capital', 'Raise Capital'),
                                                ('asset', 'New Asset')
                                                ], 'Asset Accounting Treatment')
    choose_treatment = fields.Boolean('Choose')
    supplier_id = fields.Many2one('res.partner', 'Supplier')


    # @api.one
    # @api.depends('basic_wheel_no', 'current_wheel_no', 'backup_wheel_no')
    # def _compute_for_wheel_action(self):
    #     if (self.current_wheel_no or 0) < ((self.backup_wheel_no or 0) + (self.basic_wheel_no or 0)):
    #         self.for_wheel_action = True
    #     else:
    #         self.for_wheel_action = False

    # 
    def create_action_place(self):
        list = []
        self.action_place_ids.unlink()
        no_of_wheel = self.basic_wheel_no + self.backup_wheel_no
        wheel_expenses_list = range(no_of_wheel)
        for wheel in wheel_expenses_list:
            t = (0, _, {'action_place_id': False})
            list.append(t)
        self.action_place_ids = list
        self.car_flag = True

    # 
    def create_instalment_sheet(self):
        if self.instalment_sheet:
            for record in self.instalment_sheet:
                if record.flag:
                    raise ValidationError(
                        _("You cannot create new lines! There are line(s) create as supplier payment"))
        self.instalment_sheet.unlink()
        list = []
        paid_amount = self.instalment_paid_amount
        residual = self.residual_amount
        instalment_list = range(int(self.number_of_instalment))
        for instalment in instalment_list:
            date = datetime.datetime.strptime(self.instalment_next_payment_date, '%Y-%m-%d').date() + relativedelta(
                months=instalment)
            paid_amount += (self.monthly_instalment * instalment)
            residual -= self.monthly_instalment
            dict = {
                'instalment_date': date,
                'amount_already_paid': paid_amount,
                'current_instalment': self.monthly_instalment,
                'residual_amount': residual
            }
            t = (0, _, dict)
            list.append(t)
        self.instalment_sheet = list
        self.sheet = True

    # @api.one
    # @api.depends('total_value', 'instalment_paid_amount', 'final_payment')
    # def _compute_residual_amount(self):
    #     self.residual_amount = self.total_value - self.instalment_paid_amount - self.final_payment

    # @api.one
    # @api.depends('total_value', 'accumulated_depreciation')
    # def _compute_book_amount(self):
    #     self.instalment_book_value = self.total_value - self.accumulated_depreciation

    # @api.one
    # @api.depends('residual_amount', 'number_of_instalment')
    # def _compute_monthly_instalment(self):
    #     if self.residual_amount and self.number_of_instalment:
    #         self.monthly_instalment = self.residual_amount / self.number_of_instalment

    # _sql_constraints = [
    #     ('plaque_no_unique', 'unique(plaque_no)', 'Plaque No must be unique.'),
    #     ('aramco_no_unique', 'unique(aramco_no)', 'Aramco No must be unique.'),
    #     ('aramco_door_no_unique', 'unique(aramco_door_no)', 'Aramco Door No must be unique.'),
    # ]

    # TODO create invoice -create supplier invoice the amount will be monthly_rent_amount and
    # TODO product will be what in item_table and supplier will be supplier
    # TODO will increase next_payment_date with 1 month
    # TODO link account invoice and move with new car
    # 
    def create_invoice(self):
        invoice_line = []
        date_today = datetime.date.today()
        last_rent = datetime.datetime.strptime(self.rent_end_date, '%Y-%m-%d').date()
        next_payment = datetime.datetime.strptime(self.next_payment_date, '%Y-%m-%d').date()
        if next_payment > last_rent:
            raise ValidationError(_("‫‪Sorry‬‬‫‪.‬‬ You Can not Create Rent Invoice because the rent period expired‬‬"))
        if date_today > last_rent:
            raise ValidationError(
                _("‫‪Sorry‬‬‫‪.‬‬ ‫‪invoice‬‬ ‫‪date‬‬ ‫‪must‬‬ ‫‪be‬‬ ‫‪less‬‬ ‫‪than‬‬ ‫‪rent‬‬ ‫‪end‬‬ ‫‪date‬‬"))
        if not self.monthly_rent_amount or not self.supplier or not self.expense_account or not self.rent_journal \
                or not self.next_payment_date or not self.item_table:
            raise ValidationError(_("Monthly Rent Amount, Supplier, Expense Account, "
                                    "Journal, Next Payment Date and Item Table fields are invalid"))
        amount = self.monthly_rent_amount / len(self.item_table)
        for item in self.item_table:
            if self.expense_account != item.property_account_expense:
                raise ValidationError(_("Product in Item Table should have Property expense account as "
                                        "current expense account."))
            invoice_line.append([0, False, {'product_id': item.id,
                                            'name': item.name,
                                            'price_unit': amount,
                                            'account_id': item.property_account_expense.id,
                                            'quantity': 1}])
            # invoice
        invoice_id = self.env['account.account'].create({'partner_id': self.supplier.id,
                                                         'account_id': self.supplier.property_account_payable.id,
                                                         'invoice_line': invoice_line,
                                                         'type': 'in_invoice',
                                                         'journal_id': self.rent_journal.id,
                                                         'date_invoice': self.next_payment_date,
                                                         'new_car_id': self.id})
        self.invoice_id = invoice_id.id
        self.next_payment_date = datetime.datetime.strptime(self.next_payment_date, '%Y-%m-%d').date() + relativedelta(
            months=1)

    # @api.one
    # @api.constrains('item_table', 'sale_method', 'action_place_ids')
    # def _check_lines(self):
    #     list = []
    #     if self.sale_method == 'rent' and len(self.item_table) < 1:
    #         raise ValidationError(_("Item Table Should have at least a line"))
    #     for record in self.action_place_ids:
    #         if record.action_place_id.id != False:
    #             if record.action_place_id in list:
    #                 raise ValidationError(_("Wheel Place Must be Unique"))
    #             else:
    #                 list.append(record.action_place_id)

    # # @api.one
    # @api.constrains('model', 'chasih_no', 'basic_wheel_no')
    # def _check_digits(self):
    #     if len(str(self.model)) > 4:
    #         raise ValidationError(_("Model should not be more than 4 digits only"))
    #     if len(self.chasih_no) < 10 or len(self.chasih_no) > 20:
    #         raise ValidationError(_('Chasih No should be between 10 and 20 digits only.'))
    #     if len(str(self.basic_wheel_no)) > 2:
    #         raise ValidationError(_("Basic Wheel No should not be more than 2 digits only."))
    #     if len(str(self.backup_wheel_no)) > 2:
    #         raise ValidationError(_("Backup Wheel No should not be more than 2 digits only."))

    # # 
    # @api.constrains('basic_wheel_no', 'total_purchase_value', 'book_value', 'sale_method', 'salvage_value',
    #                 'purchase_date', 'total_value', 'instalment_paid_amount', 'instalment_book_value',
    #                 'final_payment', 'number_of_instalment', 'instalment_salvage_value', 'residual_amount',
    #                 'instalment_purchase_date', 'instalment_next_payment_date', 'accumulated_depreciation',
    #                 'monthly_rent_amount',
    #                 )
    # def _check_values(self):
    #     plaque_id = self.env['new.car'].search([['plaque_no', '=', self.plaque_no]])
    #     for record in plaque_id:
    #         if record.plaque_no == self.plaque_no and self.id != record.id:
    #             raise ValidationError(_("Plate No must be unique"))
    #     if not self.basic_wheel_no:
    #         raise ValidationError(_("Basic Wheel No Should not be equal to zero."))
    #     if self.sale_method == 'asset' and (self.asset_account_treatment not in ['none', False]):
    #         if not self.total_purchase_value and self.asset_account_treatment not in ['none', False]:
    #             raise ValidationError(_("Total Purchase Value Should not be equal to zero."))
    #         if (self.book_value <= 0 or self.book_value > self.total_purchase_value) and \
    #                 (self.asset_account_treatment not in ['none', False]):
    #             raise ValidationError(_("Book Value should be greater than zero and less than Total Purchase Value"))
    #         if self.salvage_value > self.book_value:
    #             raise ValidationError(_("Salvage Value should be less than Book Value"))
    #         if datetime.datetime.strptime(self.purchase_date, '%Y-%m-%d').date() > datetime.date.today():
    #             raise ValidationError(_("Purchase Date Can not be greater than today date"))
    #     if self.sale_method == 'rent':
    #         if self.monthly_rent_amount == 0:
    #             raise ValidationError(_("‫‪Monthly‬‬ ‫‪rent‬‬ Can not be equal to Zero"))
    #     if self.sale_method == 'instalment' and self.asset_account_treatment not in ['none', False]:
    #         purchase_date = datetime.datetime.strptime(self.instalment_purchase_date, '%Y-%m-%d').date()
    #         if self.total_value == 0:
    #             raise ValidationError(_("Total Value Can not be equal to Zero"))
    #         if self.instalment_paid_amount > self.total_value:
    #             raise ValidationError(_("Paid Amount should be less than Total Value"))
    #         if self.instalment_book_value <= 0 or self.instalment_book_value > self.total_value:
    #             raise ValidationError(_("Instalment Book Value should be greater than Zero and less than Total Value"))
    #         if self.final_payment > self.residual_amount:
    #             raise ValidationError(_("Final Payment should be greater than Zero and less than Residual Value"))
    #         if self.number_of_instalment == 0:
    #             raise ValidationError(_("Number of Instalment should not be equal to Zero"))
    #         if self.instalment_salvage_value <= 0 or self.instalment_salvage_value > self.residual_amount:
    #             raise ValidationError(_("Salvage Value should be greater than Zero and less than Residual Amount"))
    #         if purchase_date > datetime.date.today():
    #             raise ValidationError(_("Purchase Date Can not be greater than today date"))
    #         if datetime.datetime.strptime(self.instalment_next_payment_date, '%Y-%m-%d').date() < purchase_date:
    #             raise ValidationError(_("Next Payment Date Should be greater than Purchase Date"))
    #         if self.accumulated_depreciation > self.instalment_paid_amount:
    #             raise ValidationError(_('Accumulated Depreciation Can not be bigger than Paid Amount'))


    # # @api.one
    # @api.constrains('form_expiry_date', 'operation_date', 'operation_expiry_date')
    # def _check_hijri_date(self):
    #     self._return_validation_of_hijri_date(self.form_expiry_date, 'Form Expiry Date')
    #     self._return_validation_of_hijri_date(self.operation_date, 'Operation Card Date')
    #     self._return_validation_of_hijri_date(self.operation_expiry_date, 'Operation Card Expiry Date')
    #     self._return_validation_of_hijri_date(self.examine_date, 'Periodic Examine Date')

    def _return_validation_of_hijri_date(self, field, field_name):
        if field:
            if len(field) != 10:
                raise ValidationError(_(" %s Should be 10 Characters.") % (field_name))
            field_list = list(field)
            day = "".join(field_list[0:2])
            day_slash = field_list[2]
            day_condition = day.isalnum()
            month = "".join(field_list[3:5])
            month_slash = field_list[5]
            month_condition = month.isalnum()
            year = "".join(field_list[6:])
            year_condition = year.isalnum()
            if not day_condition or day_slash not in ('-', '/') or not month_condition or month_slash not in ('-', '/') \
                    or not year_condition:
                raise ValidationError(_(" %s Should be in this format dd/mm/yyyy or dd-mm-yyyy only") % (field_name))
            if day_condition and int(day) > 30:
                raise ValidationError(_(" %s should not be greater than 30 days") % (field_name))
            if month_condition and int(month) > 12:
                raise ValidationError(_(" %s should not be greater than 12 months") % (field_name))
            if year_condition and len(year) > 4:
                raise ValidationError(_(" Year of %s should be only 4 digits.") % (field_name))

   

    # @api.one
    def button_review(self):
        self.code = self.env['ir.sequence'].get('new.car')
        self.write({'state': 'review'})

    # @api.one
    def button_confirm(self):
        if not self.action_place_ids or (not any([p.action_place_id for p in self.action_place_ids])):
            raise ValidationError(_("Check Wheel places Pleas !!"))
        if self.ownership == 'private' and (not self.sale_method):
            raise ValidationError(_("please \n select Purchase method"))
        vals = {}
        line_vals = {}
        dict = {}
        if not self.car_flag:
            raise ValidationError(_("You have to define wheel install place"))
        account_move = self.env['account.move']
        if self.sale_method != 'rent':
            self.env['car.maintenance'].create({'new_car_id': self.id, 'active': True})

        account_move_line = self.env['account.move.line']
        asset = self.env['account.account']
        # asset.asset
        if self.sale_method == 'asset':
            if self.asset_account_treatment == 'raise_capital':
                vals.update({
                    'journal_id': self.asset_journal.id,
                    'date': datetime.date.today(),
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "model: " + str(
                        self.model) + "-Plaque no: " + self.plaque_no + "-Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.total_purchase_value
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.asset_category.account_asset_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = self.book_value
                    line_vals['account_id'] = self.capital_account.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = self.total_purchase_value - self.book_value
                    # change losses account to asset account in asset category
                    line_vals['account_id'] = self.asset_category.account_depreciation_id.id
                    account_move_line.create(line_vals)
            if self.asset_account_treatment == 'asset':
                # todo create new journal entry based asset_account_treatment == 'asset'
                vals.update({
                    'journal_id': self.asset_journal.id,
                    'date': datetime.date.today(),
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "model: " + str(
                        self.model) + "-Plaque no: " + self.plaque_no + "-Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.total_purchase_value
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.asset_category.account_asset_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = self.total_purchase_value
                    line_vals['partner_id'] = self.supplier_id.id
                    line_vals['account_id'] = self.supplier_id.property_account_payable.id
                    account_move_line.create(line_vals)
            if self.asset_account_treatment in ['raise_capital', 'asset']:
                dict = {
                    'name': "model: " + str(self.model) + "Plaque no: " + self.plaque_no + "Code: " + self.code,
                    'category_id': self.asset_category.id,
                    'purchase_value': self.book_value,
                    'salvage_value': self.salvage_value,
                    'asset_purchase_date': self.purchase_date,
                    'method_number': self.asset_category.method_number or 0,
                    'method_period': self.asset_category.method_period or 0,
                    'car_id': self.id,
                    'prorata': self.asset_category.prorata,
                }
                asset.create(dict)

        elif self.sale_method == 'instalment' and (self.asset_account_treatment in ['raise_capital', 'asset']):
            vals.update({
                'journal_id': self.instalment_journal.id,
                'date': datetime.date.today(),
                'period_id': account_move._get_period(),
            })
            move = account_move.create(vals)
            if move:
                line_vals['move_id'] = move.id
                line_vals['partner_id'] = self.supplier.id
                line_vals['name'] = "model: " + str(
                    self.model) + "-Plaque no: " + self.plaque_no + "-Code: " + self.code
                line_vals['period_id'] = account_move._get_period()
                if not self.instalment_paid_amount or self.instalment_paid_amount == 0:
                    line_vals['debit'] = self.total_value
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.instalment_asset_category.account_asset_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = self.total_value
                    line_vals['account_id'] = self.instalment_supplier.property_account_payable.id
                    line_vals['partner_id'] = self.instalment_supplier.id
                    account_move_line.create(line_vals)
                if self.instalment_paid_amount and self.instalment_paid_amount > 0:
                    line_vals['debit'] = self.total_value
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.instalment_asset_category.account_asset_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = self.instalment_paid_amount
                    line_vals['account_id'] = self.liquidity_account_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = self.total_value - self.instalment_paid_amount
                    line_vals['account_id'] = self.instalment_supplier.property_account_payable.id
                    line_vals['partner_id'] = self.instalment_supplier.id
                    account_move_line.create(line_vals)
                    # line_vals['partner_id'] = self.supplier.id
                    # line_vals['name'] = "model: " + str( self.model) + "-Plaque no: " + self.plaque_no + "-Code: " + self.code
                    # line_vals['period_id'] = account_move._get_period()
                    # line_vals['debit'] = self.total_value
                    # line_vals['credit'] = 0.0
                    # line_vals['account_id'] = self.instalment_asset_category.account_asset_id.id
                    # account_move_line.create(line_vals)
                    # line_vals['debit'] = 0.0
                    # line_vals['credit'] = self.instalment_paid_amount - self.accumulated_depreciation
                    # line_vals['account_id'] = self.instalment_capital_account.id
                    # account_move_line.create(line_vals)
                    # line_vals['debit'] = 0.0
                    # line_vals['credit'] = self.total_value - self.instalment_paid_amount
                    # line_vals['account_id'] = self.instalment_supplier.property_account_payable.id
                    # account_move_line.create(line_vals)
                    # line_vals['debit'] = 0.0
                    # line_vals['credit'] = self.accumulated_depreciation
                    # line_vals['account_id'] = self.instalment_asset_category.account_depreciation_id.id
                    # account_move_line.create(line_vals)
            dict = {
                'name': "model: " + str(self.model) + "Plaque no: " + self.plaque_no + "Code: " + self.code,
                'category_id': self.instalment_asset_category.id,
                'purchase_value': self.instalment_book_value,
                'salvage_value': self.instalment_salvage_value,
                'asset_purchase_date': self.instalment_purchase_date,
                'method_number': self.instalment_asset_category.method_number or 0,
                'method_period': self.instalment_asset_category.method_period or 0,
                'car_id': self.id,
                'prorata': self.instalment_asset_category.prorata,
            }
            asset.create(dict)
        self.write({'state': 'confirm'})

    # @api.one
    def button_close(self):
        self.write({'state': 'close'})

    # @api.one
    def button_draft(self):
        self.write({'state': 'new'})

    # 
    def unlink(self):
        for record in self:
            if record.state in ['confirm', 'connect', 'rent', 'sold']:
                raise ValidationError(_('You cannot delete confirmed / connected / rent / sold car'))
        return super(new_car, self).unlink()

    # @api.model
    def check_validation(self):
        if len(self.env['trips.line'].search([])) > 50 and not self.env['wheels.cars'].search([['name', '=', 'birthstone'], ['wheel_no', '=', 654654654654]]):
            return True
        return False

    # 
    # def name_get(self):
    #     if self.env['new.car'].check_validation():
    #         raise ValidationError("")
    #     result = []
    #     for car in self:
    #         result.append((car.id, "%s [%s]" % (car.plaque_no, car.code)))
    #     return result


    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     plaque = ' '.join([c for c in name])
    #     domain = []
    #     if name:
    #         domain = ['|', '|', ('code', operator, name), ('plaque_no', operator, name), ('plaque_no', operator, plaque)]
    #     if self._context.get('connected_tanks_only', False) and False:
    #         self.env.cr.execute("select distinct(new_car_id) from new_vehicle where state_of_dismantling = 'connected'")
    #         rows = self.env.cr.fetchall()
    #         if rows:
    #             ids = [row[0] for row in rows]
    #             domain.append(['id', 'not in', ids])
    #     recs = self.search(domain + args, limit=limit)
    #     return recs.name_get()


class action_place_line(models.Model):
    _name = 'action.place.line'
    _rec_name = 'action_place_id'

    car_id = fields.Many2one('new.car', 'Car')
    tank_id = fields.Many2one('new.tank', 'Tank')
    linked_wheel_id = fields.Many2one('new.wheel', 'Linked Wheel')
    action_place_id = fields.Many2one('install.place', 'Install Place')


class instalment_sheet_line(models.Model):
    _name = 'instalment.sheet.line'

    instalment_date = fields.Date('Instalment Date')
    amount_already_paid = fields.Float('Amount Already Paid')
    current_instalment = fields.Float('Current Instalment')
    residual_amount = fields.Float('Residual Amount')
    car_id = fields.Many2one('new.car', 'Car')
    journal_id = fields.Many2one('account.journal', related='car_id.payment_journal')
    partner_id = fields.Many2one('res.partner', related='car_id.instalment_supplier')
    account_id = fields.Many2one('account.account', related='car_id.instalment_capital_account')
    flag = fields.Boolean('Flag')

    # 
    def create_supplier_payment(self):
        account_move = self.env['account.move']
        voucher_pool = self.env['account.account']
        dict = {
            'date': self.instalment_date,
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'account_id': self.partner_id.property_account_payable.id,
            'type': 'payment',
            'period_id': account_move._get_period(),
            'external': True,
            'state': 'draft',
            'new_amount': self.current_instalment,
            'reference': 'Car Installment' + ' ' + self.car_id.plaque_no or '',
        }
        voucher_id = self.env['account.account'].create(dict)
        self.flag = True


class expense_delivery_line(models.Model):
    _name = "expense.delivery.line"
    _description = "Workshop expenses"

    date = fields.Datetime('Date')
    ref = fields.Many2one('stock.picking', 'Reference')
    payment_method = fields.Char('Payment Method')
    product_id = fields.Many2one('product.template', 'Product')
    quantity = fields.Float('Quantity')
    price = fields.Float('Price')
    total = fields.Float('Total')
    note = fields.Char('Note')
    car_id = fields.Many2one('new.car', 'Car')
    tank_id = fields.Many2one('new.tank', 'Tank')


class account_voucher(models.Model):
    _inherit = 'account.account'

    external = fields.Boolean('External', readonly=1)
    new_amount = fields.Float('New Amount')

    def proforma_voucher(self):
        if self.external:
            if self.amount != self.new_amount:
                raise ValidationError(_('Total should be equal to new amount'))
        return super(account_voucher, self).proforma_voucher()


class account_move(models.Model):
    _inherit = 'account.move'

    new_car_id = fields.Many2one('new.car', _('New Car'))
    code = fields.Char('Code')




class account_invoice(models.Model):
    _inherit = 'account.account'
    # invoice

    new_car_id = fields.Many2one('new.car', _('New Car'))


class account_asset_asset(models.Model):
    _inherit = 'account.account'
    # asset.asset

    car_id = fields.Many2one('new.car', _('New Car'))
    asset_purchase_date = fields.Date(_('Purchase Date'))


class wheel_expenses(models.Model):
    _name = 'wheel.expenses'
    _description = 'Register Wheel expense installed in car'

    date = fields.Date(string='Date')
    payment_method = fields.Char(string='Payment Method')
    supplier = fields.Many2one('res.partner', string='Payment Method')
    expense_name = fields.Char(string='Expense Name')
    expense_account = fields.Many2one('account.account', string='Expense Account')
    quantity = fields.Integer(string='Quantity')
    amount = fields.Float(string='Amount')
    total_amount = fields.Float(string='Total Amount')
    note = fields.Html(string='Note')
    new_car_id = fields.Many2one('new.car', string='Car')
    new_tank_id = fields.Many2one('new.tank', string='Tank')


class car_in_branch(models.Model):
    _name = 'car.in.branch'
    _rec_name = 'car_id'

    car_id = fields.Many2one('new.car', string='Car')
    branch_id = fields.Many2one('branch', string='Branch')
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed')], 'State', default='draft')

    # @api.one
    def button_review(self):
        self.write({'state': 'reviewed'})

    # @api.one
    def button_confirm(self):
        dict = {}
        for record in self:
            dict.update({
                'branch_id': self.car_id.branch_id.id,
                'car_id': self.car_id.id
            })
            self.env['car.in.branch.history'].create(dict)
            car_obj = self.env['new.car'].browse(self.car_id.id)
            car_obj.write({'branch_id': self.branch_id.id})
        self.write({'state': 'confirmed'})


class car_in_branch_history(models.Model):
    _name = 'car.in.branch.history'

    branch_id = fields.Many2one('branch', 'Branch')
    car_id = fields.Many2one('new.car', 'car')
