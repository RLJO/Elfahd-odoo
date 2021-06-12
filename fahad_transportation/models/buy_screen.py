import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class buy_screen(models.Model):
    _name = 'buy.screen'
    _description = 'Buy Screen'
    _rec_name = 'code'

    code = fields.Char('Code')
    date = fields.Date('Date')
    customer_id = fields.Many2one('res.partner', 'Customer')
    journal_id = fields.Many2one('account.journal', 'Journal')
    buy_type = fields.Selection([('car', 'Car'),
                                 ('tank', 'Tank'),
                                 ('vehicle', 'Vehicle'),
                                 ('wheel', 'Wheel')], 'Buy Type')
    car_id = fields.Many2one('new.car', 'Car')
    tank_id = fields.Many2one('new.tank', 'Tank')
    vehicle_id = fields.Many2one('new.vehicle', 'Vehicle')
    wheel_id = fields.Many2one('new.wheel', 'Wheel')
    head_price = fields.Float('Head Price')
    tank_price = fields.Float('Tank Price')
    income_account_id = fields.Many2one('account.account', 'Income Account')
    buy_price = fields.Float('Buy Price')
    note = fields.Html('Note')
    asset_categ_id = fields.Many2one('account.asset.category', 'Asset category')
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('closed', 'Closed')], 'State', default='draft')

    # @api.onchange('car_id')
    # def onchange_car(self):
    #     self.asset_categ_id = self.car_id.asset_category.id

    # @api.onchange('tank_id')
    # def onchange_car(self):
    #     self.asset_categ_id = self.tank_id.id

    # @api.onchange('vehicle_id')
    # def onchange_vehicle_id(self):
    #     self.car_id = self.vehicle_id.new_car_id
    #     self.tank_id = self.vehicle_id.new_tank_id

    # @api.one
    @api.constrains('buy_type', 'head_price', 'tank_price', 'buy_price')
    def _check_values(self):
        if self.buy_type == 'vehicle':
            if self.head_price == 0 or self.tank_price == 0:
                raise ValidationError(_('Head price/ Tank price should not be equal to  zero'))
            if self.head_price >= self.buy_price or self.tank_price >= self.buy_price:
                raise ValidationError(_('Head price/ Tank price should not be equal or greater than Buy price'))
            head_tank_price = self.head_price + self.tank_price
            if head_tank_price != self.buy_price:
                raise ValidationError(_('Summation of Head price and Tank price should be equal to Buy price'))
        if self.buy_price == 0:
            raise ValidationError(_('Buy price should not be equal to  zero'))

    # @api.one
    def button_review(self):
        self.code = self.env['ir.sequence'].get('buy.screen')
        self.write({'state': 'reviewed'})

    # @api.one
    def set_wheel_sold(self, wheel_id):
        wheel_obj = self.env['new.wheel'].browse(wheel_id)
        wheel_obj.state = 'sold'

    # @api.one
    def set_sold_car(self, car_id):
        car_obj = self.env['new.car'].browse(car_id)
        car_obj.state = 'sold'
        for line in car_obj.history_wheel_installed:
            self.set_wheel_sold(line.wheel_id.id)

    # @api.one
    def set_sold_tank(self, car_id):
        tank_obj = self.env['tank.car'].browse(car_id)
        tank_obj.state = 'sold'
        for line in tank_obj.history_wheel_installed:
            self.set_wheel_sold(line.wheel_id.id)

    # @api.one
    def set_vehicle_sold(self, vehicle_id):
        vehicle = self.env['new.vehicle'].browse(vehicle_id)
        vehicle.state = 'sold'
        self.set_sold_car(vehicle.new_car_id.id)
        self.set_sold_tank(vehicle.new_tank_id.id)

    # @api.one
    def button_confirm(self):
        total_depreciation = 0
        book_value = 0
        vals = {}
        line_vals = {}
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']
        if self.buy_type == 'vehicle' and self.vehicle_id.id:
            new_vehicle = self.env['new.vehicle'].browse(self.car_id.id)
            new_vehicle.write({'state': 'sold'})
            self.set_vehicle_sold(self.vehicle_id.id)
        if self.car_id:
            if not self.car_id.revenue_account.id or (not self.car_id.loss_account.id):
                raise ValidationError(_("Please complete accounting and purchasing  details in Car window"))
            for line in self.car_id.linked_asset:
                for record in line.depreciation_line_ids:
                    if record.move_check:
                        total_depreciation += record.amount
            if self.car_id.sale_method == 'asset':
                book_value = self.car_id.total_purchase_value - self.car_id.book_value - total_depreciation
            elif self.car_id.sale_method == 'instalment':
                book_value = self.car_id.total_value - self.car_id.instalment_book_value - total_depreciation

            if self.buy_price > book_value:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Car, Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.buy_price
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = total_depreciation
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    if self.car_id.sale_method == 'asset':
                        line_vals['account_id'] = self.asset_categ_id.account_depreciation_id.id
                        if not self.asset_categ_id.account_depreciation_id.id:
                            raise ValidationError(_("Please configure depreciation account in asset category \n%s" % (self.asset_categ_id.name)))
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['account_id'] = self.car_id.instalment_asset_category.account_depreciation_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.car_id.sale_method == 'asset':
                        line_vals['credit'] = self.car_id.total_purchase_value
                        line_vals['account_id'] = self.asset_categ_id.account_asset_id.id
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['credit'] = self.car_id.total_value
                        line_vals['account_id'] = self.car_id.instalment_asset_category.account_asset_id.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.car_id.sale_method == 'asset':
                        xxx = self.buy_price + total_depreciation - self.car_id.total_purchase_value
                        xxxx = 0
                        if xxx < 0:
                            xxxx = -xxx
                            xxx = 0
                        line_vals['debit'] = xxxx
                        line_vals['credit'] = xxx
                        line_vals['account_id'] = self.car_id.revenue_account.id
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['credit'] = self.buy_price + total_depreciation - self.car_id.total_value
                        line_vals['account_id'] = self.car_id.revenue_account.id
                    line_vals['partner_id'] = self.customer_id.id
                    if line_vals['credit'] < 0:
                        pass
                    account_move_line.create(line_vals)

            if self.buy_price < book_value:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Car, Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.buy_price
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = total_depreciation
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    if self.car_id.sale_method == 'asset':
                        line_vals['account_id'] = self.asset_categ_id.account_depreciation_id.id
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['account_id'] = self.car_id.instalment_asset_category.account_depreciation_id.id
                    account_move_line.create(line_vals)
                    line_vals['credit'] = 0.0
                    if self.car_id.sale_method == 'asset':
                        line_vals['debit'] = self.car_id.total_purchase_value - self.buy_price - total_depreciation
                        line_vals['account_id'] = self.car_id.loss_account.id
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['debit'] = self.car_id.total_value - self.buy_price - total_depreciation
                        line_vals['account_id'] = self.car_id.loss_account.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.car_id.sale_method == 'asset':
                        line_vals['credit'] = self.car_id.total_purchase_value
                        line_vals['account_id'] = self.asset_categ_id.account_asset_id.id
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['credit'] = self.car_id.total_value
                        line_vals['account_id'] = self.car_id.instalment_asset_category.account_asset_id.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)

            if self.buy_price == book_value:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Car, Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.buy_price
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = total_depreciation
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    if self.car_id.sale_method == 'asset':
                        line_vals['account_id'] = self.asset_categ_id.account_depreciation_id.id
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['account_id'] = self.car_id.instalment_asset_category.account_depreciation_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.car_id.sale_method == 'asset':
                        line_vals['credit'] = self.car_id.total_purchase_value
                        line_vals['account_id'] = self.asset_categ_id.account_asset_id.id
                    elif self.car_id.sale_method == 'instalment':
                        line_vals['credit'] = self.car_id.total_value
                        line_vals['account_id'] = self.car_id.instalment_asset_category.account_asset_id.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)

            self.set_sold_car(self.car_id.id)

        if self.tank_id:
            if not self.tank_id.revenue_account.id or (not self.tank_id.loss_account.id):
                raise ValidationError(_("Please complete accounting and purchasing  details in Tank window"))
            for line in self.car_id.linked_asset:
                for record in line.depreciation_line_ids:
                    if record.move_check:
                        total_depreciation += record.amount
            if self.tank_id.sale_method == 'asset':
                book_value = self.tank_id.total_purchase_value - self.tank_id.book_value - total_depreciation
            elif self.tank_id.sale_method == 'instalment':
                book_value = self.tank_id.total_value - self.tank_id.instalment_book_value - total_depreciation

            if self.buy_price > book_value:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Tank, Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.buy_price
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = total_depreciation
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    if self.tank_id.sale_method == 'asset':
                        line_vals['account_id'] = self.tank_id.asset_category.account_depreciation_id.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['account_id'] = self.tank_id.instalment_asset_category.account_depreciation_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.tank_id.sale_method == 'asset':
                        line_vals['credit'] = self.tank_id.total_purchase_value
                        line_vals['account_id'] = self.tank_id.asset_category.account_asset_id.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['credit'] = self.tank_id.total_value
                        line_vals['account_id'] = self.tank_id.instalment_asset_category.account_asset_id.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.tank_id.sale_method == 'asset':
                        line_vals['credit'] = self.buy_price + total_depreciation - self.tank_id.total_purchase_value
                        line_vals['account_id'] = self.tank_id.revenue_account.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['credit'] = self.buy_price + total_depreciation - self.tank_id.total_value
                        line_vals['account_id'] = self.tank_id.revenue_account.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)

            if self.buy_price < book_value:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Tank, Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.buy_price
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = total_depreciation
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    if self.tank_id.sale_method == 'asset':
                        line_vals['account_id'] = self.tank_id.asset_category.account_depreciation_id.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['account_id'] = self.tank_id.instalment_asset_category.account_depreciation_id.id
                    account_move_line.create(line_vals)
                    line_vals['credit'] = 0.0
                    if self.tank_id.sale_method == 'asset':
                        line_vals['debit'] = self.tank_id.total_purchase_value - self.buy_price - total_depreciation
                        line_vals['account_id'] = self.tank_id.loss_account.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['debit'] = self.tank_id.total_value - self.buy_price - total_depreciation
                        line_vals['account_id'] = self.tank_id.loss_account.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.tank_id.sale_method == 'asset':
                        line_vals['credit'] = self.tank_id.total_purchase_value
                        line_vals['account_id'] = self.tank_id.asset_category.account_asset_id.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['credit'] = self.tank_id.total_value
                        line_vals['account_id'] = self.tank_id.instalment_asset_category.account_asset_id.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)

            if self.buy_price == book_value:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Tank, Code: " + self.code
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = self.buy_price
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = total_depreciation
                    line_vals['credit'] = 0.0
                    line_vals['partner_id'] = self.customer_id.id
                    if self.tank_id.sale_method == 'asset':
                        line_vals['account_id'] = self.tank_id.asset_category.account_depreciation_id.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['account_id'] = self.tank_id.instalment_asset_category.account_depreciation_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    if self.tank_id.sale_method == 'asset':
                        line_vals['credit'] = self.tank_id.total_purchase_value
                        line_vals['account_id'] = self.tank_id.asset_category.account_asset_id.id
                    elif self.tank_id.sale_method == 'instalment':
                        line_vals['credit'] = self.tank_id.total_value
                        line_vals['account_id'] = self.tank_id.instalment_asset_category.account_asset_id.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)

            self.set_sold_tank(self.tank_id.id)
        elif self.wheel_id:
            vals.update({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'period_id': account_move._get_period(),
            })
            move = account_move.create(vals)
            if move:
                line_vals['move_id'] = move.id
                line_vals['name'] = "Wheel, Code: " + self.code
                line_vals['period_id'] = account_move._get_period()
                line_vals['debit'] = self.buy_price
                line_vals['credit'] = 0.0
                line_vals['partner_id'] = self.customer_id.id
                line_vals['account_id'] = self.customer_id.property_account_receivable.id
                account_move_line.create(line_vals)
                line_vals['debit'] = 0.0
                line_vals['credit'] = self.buy_price
                line_vals['partner_id'] = self.customer_id.id
                line_vals['account_id'] = self.income_account_id.id
                account_move_line.create(line_vals)
            self.set_wheel_sold(self.wheel_id.id)

        self.write({'state': 'confirmed'})

    # @api.one
    def button_close(self):
        self.write({'state': 'closed'})

    # @api.one
    def button_draft(self):
        self.write({'state': 'draft'})

    # 
    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise Warning(_('You cannot delete confirmed expense register'))
        return super(buy_screen, self).unlink()

        # @api.model
        # def create(self, vals):
        # vals['code'] = self.env['ir.sequence'].get('buy.screen')
        # return super(buy_screen, self).create(vals)
