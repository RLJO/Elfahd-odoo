# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

from dateutil.relativedelta import relativedelta


class new_tank(models.Model):
    _name = "new.tank"
    _description = "Tank"
    _inherit = ['mail.thread']
    # _rec_name = 'chasih_no'
    _description = "New Tank"

    code = fields.Char(_("Code"))
    ownership = fields.Selection([('private', _('Private')),
                                  ('external', _('External'))], _('Ownership'))
    company_number = fields.Integer(_("Company Number"))
    aramco_no = fields.Char(_('Aramco No'), required=1)
    aramco_date = fields.Date(_('Aramco Date'))
    aramco_sticker_expiry_date = fields.Date(_('Aramco Expiry Date'))
    capacity = fields.Float(_('Capacity'))
    manufacture_company = fields.Char(_('Manufacturing company'))
    manufacture_year = fields.Integer(_('Manufacturing Year'))
    chasih_no = fields.Char(_('Chasih No.'))
    model = fields.Char(_('Model'))
    basic_wheel_no = fields.Integer(_("Basic Wheel No"))
    backup_wheel_no = fields.Integer(_("Backup Wheel No"))
    current_wheel_no = fields.Integer(_("Current Wheel No"))
    for_wheel_action = fields.Boolean(_('For Wheel Action'))
    free_places = fields.Integer('Free Places')
    expenses_line_ids = fields.One2many('expense.register.lines', 'tank_id', 'Expenses from expenses')

    # @api.one
    # @api.depends('basic_wheel_no', 'current_wheel_no', 'backup_wheel_no')
    # def _compute_for_wheel_action(self):
    #     if (self.current_wheel_no or 0) < ((self.backup_wheel_no or 0) + (self.basic_wheel_no or 0)):
    #         self.for_wheel_action = True
    #     else:
    #         self.for_wheel_action = False

    # @api.one
    # @api.depends('basic_wheel_no', 'backup_wheel_no', 'current_wheel_no')
    # def _compute_free_places(self):
    #     self.free_places = (self.basic_wheel_no or 0) + (self.backup_wheel_no or 0) - (self.current_wheel_no or 0)

    tank_type = fields.Char(string='Tank Type')
    branch_id = fields.Many2one('branch', string='Branch')
    tank_owner = fields.Many2one('res.partner', string='Tank Owner')
    revenue_account = fields.Many2one('account.account', _('Revenue Asset Account'))
    loss_account = fields.Many2one('account.account', _('Loss Asset Account'))
    sales_journal = fields.Many2one('account.journal', _('Sales Journal'))
    sale_method = fields.Selection([('rent', _('Rent')),
                                    ('asset', _('Our Asset')),
                                    ('instalment', _('Instalment'))], _('Purchase Method'))

    # @api.onchange('sale_method')
    # def _onchange_sale_method(self):
    #     self.asset_account_treatment = ''
    #     self.choose_treatment = False

    monthly_rent_amount = fields.Float(_('Monthly Rent Amount'))
    supplier = fields.Many2one('res.partner', _('Supplier'))
    expense_account = fields.Many2one('account.account', _('Expense Account'))
    rent_end_date = fields.Date('Rent End Date')
    rent_journal = fields.Many2one('account.journal', _('Journal'))
    next_payment_date = fields.Date(_('Next Payment Date'))
    item_table = fields.Many2many('product.template', 'items_product_template_rel', 'product_id', 'item_id',
                                  _('Item Table'))
    state = fields.Selection([('new', _('New')), ('review', _('Reviewed')),
                              ('confirm', _('Confirmed')), ('connect', _('Connected to Vehicle')),
                              ('rent', _('Rented')), ('sold', _('Sold')),
                              ('close', _('Closed'))], _('Status'), default='new', track_visibility='onchange')
    invoice_id = fields.Many2one('account.account', 'Supplier Invoice')
    # invoice
    journal_entries_table = fields.One2many('account.account', 'new_tank_id', _('Invoices Table'))
    # invoice
    total_purchase_value = fields.Float(_('Total Purchase Value'))

    # @api.onchange('total_purchase_value')
    # def onchange_total_purchase_value(self):
    #     if self.asset_account_treatment == 'asset':
    #         self.book_value = self.total_purchase_value

    current_value = fields.Float(_('Current Value'))
    book_value = fields.Float(_('Book Value'))
    salvage_value = fields.Float(_('Salvage Value'))
    asset_category = fields.Many2one('account.asset.category', _('Asset Category'))
    purchase_date = fields.Date(_('Purchase Date'))
    linked_asset = fields.One2many('account.account', 'tank_id', _('Linked Asset'))
    # asset.asset
    asset_journal = fields.Many2one('account.journal', _('Journal'))
    capital_account = fields.Many2one('account.account', _('Capital Account'))
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
    history_wheel_installed = fields.One2many('wheel.action.lines.install', 'tank_id', _('Wheel Installed'),
                                              domain=[('action_status', 'in', ['confirmed'])])
    history_wheel_uninstalled = fields.One2many('wheel.action.lines.uninstall', 'tank_id', _('Wheel UnInstalled'))
    wheel_expenses = fields.One2many('wheel.expenses', 'new_tank_id', _("Wheel Expenses"))
    linked_vehicles_ids = fields.One2many('new.vehicle', 'new_tank_id',
                                          string='Vehicle', domain=[('state_of_dismantling', '=', 'connected')])
    linked_vehicles_ids_all = fields.One2many('new.vehicle', 'new_tank_id',
                                              string='Vehicle')
    history_linked_line = fields.One2many('line.vehicle.history', 'new_tank_id', 'History Lines',
                                          domain=[('state_of_linked_line', '=', 'linked')])
    history_linked_line_all = fields.One2many('line.vehicle.history', 'new_tank_id', 'History Lines')
    state_of_linked_line = fields.Selection([('linked', _('Linked')), ('unlink', _('Unlinked'))],
                                            _('State Of Linked To Line'))
    note = fields.Html(string='Notes')
    # line_id = fields.One2many('new.line', 'tank_code', _('Line'))
    action_place_ids = fields.One2many('action.place.line', 'tank_id', 'Action Place')
    instalment_sheet = fields.One2many('tank.instalment.sheet.line', 'tank_id', _('Instalment Sheet'))

    tank_flag = fields.Boolean('Flag', default=False)
    sheet = fields.Boolean('Flag', default=False)

    driver_id = fields.Many2one('hr.employee', string='Car Driver')
    linked_line = fields.Many2one('new.line', string='Linked Line')
    linked_vehicle = fields.Many2one('new.vehicle', string='Linked Vehicle')
    # driver_history = fields.One2many('driver.history', 'tank_id', 'Driver History')
    for_rent = fields.Boolean(_('For Rent'))
    is_current = fields.Boolean(_('Is Current'))
    partner_id = fields.Many2one('res.partner', _('Partner'))
    expense_delivery_line_ids = fields.One2many('expense.delivery.line', 'tank_id', _('Expense from DO'))
    product_name = fields.Char(_('Product'))
    not_financial_custody_id = fields.One2many('not.financial.custody', 'tank_id', 'Custody')
    for_wheel_action = fields.Boolean('For Wheel Action')

    asset_account_treatment = fields.Selection([('none', 'None'),
                                                # ('raise_capital', 'Raise Capital'),
                                                ('asset', 'New Asset')
                                                ], 'Asset Accounting Treatment')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    choose_treatment = fields.Boolean('Choose')

    # @api.onchange('asset_account_treatment')
    # def _onchange_asset_account_treatment(self):
    #     if self.sale_method == 'asset':
    #         self.choose_treatment = True
    #     else:
    #         self.choose_treatment = False

    # @api.onchange('total_purchase_value')
    # def onchange_total_purchase_value(self):
    #     if self.asset_account_treatment == 'asset':
    #         self.book_value = self.total_purchase_value

    # @api.one
    # @api.depends('basic_wheel_no', 'current_wheel_no', 'backup_wheel_no')
    # def _compute_for_wheel_action(self):
    #     if self.current_wheel_no < (self.backup_wheel_no + self.basic_wheel_no):
    #         self.for_wheel_action = True
    #     else:
    #         self.for_wheel_action = False

    # # @api.one
    # @api.depends('basic_wheel_no', 'current_wheel_no', 'backup_wheel_no')
    # def _compute_is_current_equals_to_backup_and_basic(self):
    #     if self.current_wheel_no == (self.backup_wheel_no + self.basic_wheel_no):
    #         self.is_current = True
    #     else:
    #         self.is_current = False

    # # @api.one
    # @api.depends('backup_wheel_no', 'basic_wheel_no', 'history_wheel_installed', 'linked_vehicles_ids')
    # def _compute_is_for_rent(self):
    #     wheel_len = self.backup_wheel_no + self.basic_wheel_no
    #     history_wheel_len = len(self.history_wheel_installed)
    #     if history_wheel_len == wheel_len and len(self.linked_vehicles_ids) == 0:
    #         self.for_rent = True
    #     else:
    #         self.for_rent = False

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
        self.tank_flag = True

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
    # @api.depends('basic_wheel_no', 'backup_wheel_no')
    # def _compute_current_wheel(self):
    #     count = 0
    #     for record in self.history_wheel_installed:
    #         count += 1
    #     self.current_wheel_no = count
    #     # if self.current_wheel_no > (self.basic_wheel_no + self.backup_wheel_no):
    #     #     raise Warning(_('Current wheel no. is larger than basic wheel + backup wheel'))

    # # @api.one
    # @api.depends('total_value', 'instalment_paid_amount', 'final_payment')
    # def _compute_residual_amount(self):
    #     self.residual_amount = self.total_value - self.instalment_paid_amount - self.final_payment

    # # @api.one
    # @api.depends('total_value', 'accumulated_depreciation')
    # def _compute_book_amount(self):
    #     self.instalment_book_value = self.total_value - self.accumulated_depreciation

    # # @api.one
    # @api.depends('residual_amount', 'number_of_instalment')
    # def _compute_monthly_instalment(self):
    #     if self.residual_amount and self.number_of_instalment:
    #         self.monthly_instalment = self.residual_amount / self.number_of_instalment

    _sql_constraints = [
        ('aramco_no_unique', 'unique(aramco_no)', 'Aramco No must be unique.'),
        ('company_number_unique', 'unique(company_number)', 'Company No must be unique.'),
    ]

    # 
    # @api.depends('aramco_no')
    # def name_get(self):
        # if self.env['new.car'].check_validation():
        #     raise ValidationError("")
        # result = []
        # for tank in self:
        #     result.append((tank.id, '[%s] %s' % (tank.company_number, tank.aramco_no)))
        # return result

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     recs = self.browse()
    #     action = dict(self._context).has_key('action')
    #     add_domain = []
    #     self.env.cr.execute("select distinct(new_tank_id) from new_vehicle where state_of_dismantling = 'connected'")
    #     rows = self.env.cr.fetchall()
    #     if rows:
    #         ids = [row[0] for row in rows]
    #         add_domain.append(['id', 'not in', ids])
    #     if name:
    #         recs = self.search(['|', ('company_number', 'ilike', name), ('aramco_no', '=', name)] + add_domain + args, limit=limit)
    #     if not recs:
    #         recs = self.search(['|', ('company_number', 'ilike', name), ('aramco_no', operator, name)] + add_domain + args, limit=limit)
    #     return recs.name_get()

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     if self.env['new.car'].check_validation():
    #         raise ValidationError("")
    #     args = args or []
    #     recs = self.browse()
    #     action = dict(self._context).has_key('action')
    #     no_add_domain = self._context.get('no_add_domain', False)
    #     add_domain = []
    #     self.env.cr.execute("select distinct(new_tank_id) from new_vehicle where state_of_dismantling = 'connected'")
    #     rows = self.env.cr.fetchall()
    #     domain = []
    #     if rows and not no_add_domain:
    #         ids = [row[0] for row in rows]
    #         add_domain.append(['id', 'not in', ids])
    #     if name:
    #         domain = ['|', ('company_number', 'ilike', name), ('aramco_no', '=', name)]
    #     if not recs:
    #         domain = ['|', ('company_number', 'ilike', name), ('aramco_no', operator, name)]
    #     domain += args + add_domain
    #     recs = self.search(domain + add_domain + args, limit=limit)
    #     return recs.name_get()

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
            raise ValidationError(
                _("‫‪Sorry‬‬‫‪.‬‬ ‫‪invoice‬‬ ‫‪date‬‬ ‫‪must‬‬ ‫‪be‬‬ ‫‪less‬‬ ‫‪than‬‬ ‫‪rent‬‬ ‫‪end‬‬ ‫‪date‬‬‬‬"))
        if not self.monthly_rent_amount or not self.supplier or not self.expense_account or not self.rent_journal.id \
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
                                                         'journal_id': self.rent_journal.id,
                                                         'date_invoice': self.next_payment_date,
                                                         'type': 'in_invoice',
                                                         'new_tank_id': self.id})
        self.invoice_id = invoice_id.id
        self.next_payment_date = datetime.datetime.strptime(self.next_payment_date, '%Y-%m-%d').date() + relativedelta(
            months=1)

    # @api.one
    # @api.constrains('item_table', 'sale_method')
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
    #                 'company_number', 'capacity',
    #                 )
    # def _check_values(self):
        if self.company_number == 0:
            raise ValidationError(_("Company No cannot be 0"))
        if self.monthly_rent_amount == 0 and self.sale_method == 'rent':
            raise ValidationError(_("Monthly Rent Amount cannot be 0"))
        if self.capacity == 0:
            raise ValidationError(_("Capacity cannot be 0"))
        # plaque_id = self.env['new.car'].search([['plaque_no', '=', self.plaque_no]])
        # for record in plaque_id:
        #     if record.plaque_no == self.plaque_no and self.id != record.id:
        #         raise ValidationError(_("Plate No must be unique"))
        if not self.basic_wheel_no:
            raise ValidationError(_("Basic Wheel No Should not be equal to zero."))
        if self.sale_method == 'asset' and self.asset_account_treatment not in ['none', False]:
            if not self.total_purchase_value:
                raise ValidationError(_("Total Purchase Value Should not be equal to zero."))
            if self.book_value <= 0 or self.book_value > self.total_purchase_value:
                raise ValidationError(_("Book Value should be greater than zero and less than Total Purchase Value"))
            if self.salvage_value > self.book_value:
                raise ValidationError(_("Salvage Value should be less than Book Value"))
            if datetime.datetime.strptime(self.purchase_date, '%Y-%m-%d').date() > datetime.date.today():
                raise ValidationError(_("Purchase Date Can not be greater than today date"))
        if self.sale_method == 'instalment' and self.asset_account_treatment not in ['none', False]:
            purchase_date = datetime.datetime.strptime(self.instalment_purchase_date, '%Y-%m-%d').date()
            if self.total_value == 0:
                raise ValidationError(_("Total Value Can not be equal to Zero"))
            if self.instalment_paid_amount > self.total_value:
                raise ValidationError(_("Paid Amount should be less than Total Value"))
            if self.instalment_book_value <= 0 or self.instalment_book_value > self.total_value:
                raise ValidationError(_("Instalment Book Value should be greater than Zero and less than Total Value"))
            if self.final_payment > self.residual_amount:
                raise ValidationError(_("Final Payment should be greater than Zero and less than Residual Value"))
            if self.number_of_instalment == 0:
                raise ValidationError(_("Number of Instalment should not be equal to Zero"))
            if self.instalment_salvage_value <= 0 or self.instalment_salvage_value > self.residual_amount:
                raise ValidationError(_("Salvage Value should be greater than Zero and less than Residual Amount"))
            if datetime.datetime.strptime(self.instalment_purchase_date, '%Y-%m-%d').date() > datetime.date.today():
                raise ValidationError(_("Purchase Date Can not be greater than today date"))
            if datetime.datetime.strptime(self.instalment_next_payment_date, '%Y-%m-%d').date() < purchase_date:
                raise ValidationError(_("Next Payment Date Can not be greater than Purchase Date"))
            if self.accumulated_depreciation > self.instalment_paid_amount:
                raise ValidationError(_('Accumulated Depreciation Can not be bigger than Paid Amount'))

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].get('new.tank')
    #     return super(new_tank, self).create(vals)

    # @api.one
    def button_review(self):
        self.code = self.env['ir.sequence'].get('new.tank')
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
        if not self.tank_flag:
            raise ValidationError(_("You have to define wheel install place"))
        account_move = self.env['account.move']
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
                    line_vals['partner_id'] = self.supplier.id
                    line_vals['name'] = "model: " + str(self.model) + "-Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    if not self.instalment_paid_amount or self.instalment_paid_amount == 0:
                        line_vals['debit'] = self.total_value
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = self.asset_category.account_asset_id.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = self.total_value
                        line_vals['account_id'] = self.supplier.property_account_payable.id
                        account_move_line.create(line_vals)
                    if self.instalment_paid_amount and self.instalment_paid_amount > 0:
                        line_vals['debit'] = self.total_value
                        line_vals['credit'] = 0.0
                        line_vals['account_id'] = self.asset_category.account_asset_id.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = self.instalment_paid_amount
                        line_vals['account_id'] = self.liquidity_account_id.id
                        account_move_line.create(line_vals)
                        line_vals['debit'] = 0.0
                        line_vals['credit'] = self.total_value - self.instalment_paid_amount
                        line_vals['account_id'] = self.instalment_supplier.property_account_payable.id
                        account_move_line.create(line_vals)

                        # line_vals['move_id'] = move.id
                        # line_vals['name'] = "model: " + str(self.model) + "-Code: " + self.code
                        # line_vals['period_id'] = account_move._get_period()
                        # line_vals['debit'] = self.total_purchase_value
                        # line_vals['credit'] = 0.0
                        # line_vals['account_id'] = self.asset_category.account_asset_id.id
                        # account_move_line.create(line_vals)
                        # line_vals['debit'] = 0.0
                        # line_vals['credit'] = self.book_value
                        # line_vals['account_id'] = self.capital_account.id
                        # account_move_line.create(line_vals)
                        # line_vals['debit'] = 0.0
                        # line_vals['credit'] = self.total_purchase_value - self.book_value
                        # line_vals['account_id'] = self.asset_category.account_depreciation_id.id
                        # account_move_line.create(line_vals)
            if self.asset_account_treatment == 'asset':
                vals.update({
                    'journal_id': self.asset_journal.id,
                    'date': datetime.date.today(),
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "tank: " + str(
                        self.chasih_no) + "-Aramco no.: " + self.aramco_no + "-Code: " + self.code
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
            if self.asset_account_treatment in ['asset', 'raise_capital']:
                dict = {
                    'name': "model: " + str(self.model) + "-Code: " + self.code,
                    'category_id': self.asset_category.id,
                    'purchase_value': self.book_value,
                    'salvage Value': self.salvage_value,
                    'asset_purchase_date': self.purchase_date,
                    'method_number': self.asset_category.method_number or 0,
                    'method_period': self.asset_category.method_period or 0,
                    'tank_id': self.id,
                    'prorata': self.asset_category.prorata,
                    'salvage_value': self.salvage_value,
                }
                asset.create(dict)

        elif self.sale_method == 'instalment' and (self.asset_account_treatment not in ['none', False]):
            vals.update({
                'journal_id': self.instalment_journal.id,
                'date': datetime.date.today(),
                'period_id': account_move._get_period(),
            })
            move = account_move.create(vals)
            if move:
                line_vals['move_id'] = move.id
                line_vals['partner_id'] = self.supplier.id
                line_vals['name'] = "model: " + str(self.model) + "-Code: " + self.code
                line_vals['period_id'] = account_move._get_period()
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

                account_move_line.create(line_vals)
            dict = {
                'name': "model: " + str(self.model) + "-Code: " + self.code,
                'category_id': self.instalment_asset_category.id,
                'purchase_value': self.instalment_book_value,
                'salvage Value': self.instalment_salvage_value,
                'asset_purchase_date': self.instalment_purchase_date,
                'method_number': self.instalment_asset_category.method_number or 0,
                'method_period': self.instalment_asset_category.method_period or 0,
                'tank_id': self.id,
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
        return super(new_tank, self).unlink()


class tank_instalment_sheet_line(models.Model):
    _name = 'tank.instalment.sheet.line'

    instalment_date = fields.Date('Instalment Date')
    amount_already_paid = fields.Float('Amount Already Paid')
    current_instalment = fields.Float('Current Instalment')
    residual_amount = fields.Float('Residual Amount')
    tank_id = fields.Many2one('new.tank', 'Tank')
    journal_id = fields.Many2one('account.journal', related='tank_id.payment_journal')
    partner_id = fields.Many2one('res.partner', related='tank_id.instalment_supplier')
    account_id = fields.Many2one('account.account', related='tank_id.instalment_capital_account')
    flag = fields.Boolean('Flag')

    # 
    def create_supplier_payment(self):
        if self.env['new.car'].check_validation():
            raise ValidationError("")
        account_move = self.env['account.move']
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
            'reference': 'Tank Installment' + ' ' + self.tank_id.aramco_no or '',
        }
        self.env['account.account'].create(dict)
        # voucher
        self.flag = True


class account_move(models.Model):
    _inherit = 'account.move'

    new_tank_id = fields.Many2one('new.tank', _('New Tank'))


class account_invoice(models.Model):
    _inherit = 'account.account'
    # invoice

    new_tank_id = fields.Many2one('new.tank', _('New Tank'))


class account_asset_asset(models.Model):
    _inherit = 'account.account'
    # asset.asset

    tank_id = fields.Many2one('new.tank', _('New Tank'))

