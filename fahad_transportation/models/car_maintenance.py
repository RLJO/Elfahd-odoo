# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta


class car_maintenance(models.Model):
    _name = "car.maintenance"
    _description = "Car maintenance"
    _rec_name = 'plaque_no'

    new_car_id = fields.Many2one('new.car', _('Car'))
    code = fields.Char(_("Code"), related='new_car_id.code')
    car_category = fields.Many2one('car.category', 'Car Category', related='new_car_id.car_category')
    plaque_no = fields.Char(_('Plaque No'), related='new_car_id.plaque_no')
    model = fields.Integer(_('Model'), related='new_car_id.model')
    mark = fields.Char(_('Mark'), related='new_car_id.mark')
    record_type = fields.Char(_('Record Type'), related='new_car_id.record_type')
    color = fields.Char(_('Color'), related='new_car_id.color')
    chasih_no = fields.Char(_('Chasih No'), related='new_car_id.chasih_no')
    type = fields.Char(_('Type'), related='new_car_id.type')
    examine_date = fields.Date(_("Periodic Examine Date"), related='new_car_id.examine_date')
    note = fields.Html(_("Notes"), related='new_car_id.note')
    ownership = fields.Selection([('private', 'Private'),
                                  ('external', 'External')], 'Ownership', related='new_car_id.ownership')
    cat_state = fields.Selection([('new', 'New'), ('review', 'Reviewed'),
                                  ('confirm', 'Confirmed'), ('connect', 'Connected to Vehicle'),
                                  ('rent', 'Rented'), ('sold', 'Sold'),
                                  ('close', 'Closed')], 'Status', related='new_car_id.state')
    external_ownership = fields.Many2one('res.partner', 'External Ownership', related='new_car_id.external_ownership')
    # related_tank_id = fields.Many2one('new.tank', string='Related Tank', related='new_car_id.tank_id.id')
    # related_driver_id = fields.Many2one('hr.employee', string='Related Driver', related='new_car_id.driver_id.id')
    active = fields.Boolean(string='Active', default=True)
    current_meter = fields.Float(string='current Meter', digits=(15,3))
    maintenance_journal = fields.Many2one('account.journal', string='Maintenance Expense Journal')
    # #######################Gear Box Oil(New Tab)########################
    gear_change_after = fields.Integer(string='Change Oil After')
    gearbox_line_ids = fields.One2many('gearbox.line', 'maintenance_id', string='Entry Data')
    # #######################Differential Oil(New Tab) #########################
    differential_change_after = fields.Integer(string='Change Oil After')
    differential_line_ids = fields.One2many('differential.line', 'maintenance_id', string='Entry Data')

    # #######################Machine Oil(New Tab) #########################
    machine_change_after = fields.Integer(string='Change Oil After')
    machine_line_ids = fields.One2many('machine.motor.line', 'maintenance_id', string='Entry Data')

    state = fields.Selection([('draft', 'New'), ('review', 'Reviewed'), ('confirm', 'Confirmed'), ('end', 'End')],
                             string='State', default='draft')

    # @api.one
    @api.constrains('machine_change_after', 'differential_change_after', 'price_unit')
    def _check_digits(self):
        if len(str(self.machine_change_after)) > 5:
            raise ValidationError(_("Machine Oil Change should not be more than 5 digits only"))

        if len(str(self.differential_change_after)) > 5:
            raise ValidationError(_("Diferance Oil Change should not be more than 5 digits only"))

        if len(str(self.gear_change_after)) > 5:
            raise ValidationError(_("Gear Box Change should not be more than 5 digits only"))

            # @api.one
            # def button_review(self):
            # self.write({'state': 'review'})
            #
            # @api.one
            # def button_draft(self):
            #     self.write({'state': 'draft'})
            #
            # @api.one
            # def button_end(self):
            #     self.write({'state': 'end'})
            #
            # 
            # def button_confirm(self):
            #     for line in self.gearbox_line_ids:
            #         line_obj = self.env['gearbox.line'].browse(line.id)
            #         line_obj.write({'new_car_id': self.new_car_id.id})
            #
            #     for line in self.differential_line_ids:
            #         line_obj = self.env['differential.line'].browse(line.id)
            #         line_obj.write({'new_car_id': self.new_car_id.id})
            #
            #     for line in self.machine_line_ids:
            #         line_obj = self.env['machine.motor.line'].browse(line.id)
            #         line_obj.write({'new_car_id': self.new_car_id.id})
            #     self.write({'state': 'confirm'})


# ######################## Gear Box Lines################################

class gearbox_line(models.Model):
    _name = 'gearbox.line'
    _description = 'Register Gearbox records'

    meter_read = fields.Float(string='Meter Read',digits=(15,3))
    maintenance_id = fields.Many2one('car.maintenance', string='Car Maintenance')
    new_car_id = fields.Many2one('new.car', string='Car')
    rent_id = fields.Many2one('rent', string='rend')
    gear_change_after = fields.Integer(string='Change Oil After', related='maintenance_id.gear_change_after')
    next_oil_change = fields.Float(string='Next Oil Change')

    # @api.one
    @api.depends('gear_change_after', 'meter_read')
    def _compute_next_oil_change(self):
        self.next_oil_change = self.meter_read + self.gear_change_after

    date = fields.Datetime('Date')
    product_id = fields.Many2one('product.template', string='Product Name')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')
    total = fields.Float(string='Total')

    # @api.one
    @api.depends('quantity', 'price_unit')
    def _compute_total_amount(self):
        self.total = self.quantity * self.price_unit

    # current_driver = fields.Many2one('hr.employee', string= 'Current Driver')
    mechanical = fields.Many2one('hr.employee', string='Mechanical')
    expense_type_id = fields.Many2one('expenses', string='Expense Type')
    location_id = fields.Many2one('stock.location', string='Stock Location')
    warehouse_account = fields.Many2one('account.account', string='Warehouse Account')
    note = fields.Html(string='Note')
    complete = fields.Boolean(string='Hide')


    # @api.one
    # @api.constrains('meter_read', 'quantity', 'price_unit')
    # def _check_digits(self):
    #     if len(str(int(self.meter_read))) > 7:
    #         raise ValidationError(_("Meter Read should not be more than 7 digits only"))
    #     if len(str(int(self.quantity))) > 3:
    #         raise ValidationError(_('Quantity should not be more than 3 digits only'))
    #     if len(str(int(self.price_unit))) > 3:
    #         raise ValidationError(_("Price Unit should not be more than 3 digits only."))

    # 
    def create_delivery_order(self):
        order_line = []
        expense_register_line = []
        delivery_order = self.env['stock.picking']
        expense_register = self.env['expense.register']
        picking_type_obj = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        order_line.append([0, False, {'product_id': self.product_id.id,
                                      'name': self.product_id.name,
                                      'product_uom_qty': self.quantity,
                                      'product_uom': self.product_id.uom_id.id,
                                      'price_unit': self.price_unit,
                                      'location_id': self.location_id.id,
                                      'location_dest_id': picking_type_obj.default_location_dest_id and picking_type_obj.default_location_dest_id.id
        }])
        self.env['stock.picking'].create({
            'date': self.date,
            'move_lines': order_line,
            'picking_type_id': picking_type_obj.id,
        })

        expense_register_line.append([0, False, {
            'expense_name': self.expense_type_id and self.expense_type_id.id or '',
            'number': self.quantity,
            'amount': self.price_unit,
            'total': self.total,
            'note': self.note,
        }])
        self.env['expense.register'].create({
            'date': self.date,
            'expense_register_level': 'car',
            'car_id': self.maintenance_id.new_car_id.id,
            'payment_method': 'warehouse',
            'location_id': self.location_id.id or False,
            'location_account': self.warehouse_account.id or False,
            'expense_register_line_ids': expense_register_line,
        })
        self.new_car_id = self.maintenance_id.new_car_id.id
        self.complete = True
        return True


# ######################## Differential Lines################################
class differential_line(models.Model):
    _name = 'differential.line'
    _description = 'Register differential records'

    meter_read = fields.Float(string='Meter Read',digits=(15,3))
    maintenance_id = fields.Many2one('car.maintenance', string='Car Maintenance')
    new_car_id = fields.Many2one('new.car', string='Car')
    rent_id = fields.Many2one('rent', string='rend')
    differential_change_after = fields.Integer(string='Change Oil After',
                                               related='maintenance_id.differential_change_after')
    next_oil_change = fields.Float(string='Next Oil Change')

    # @api.one
    @api.depends('meter_read', 'differential_change_after')
    def _compute_next_oil_change(self):
        self.next_oil_change = self.meter_read + self.differential_change_after


    date = fields.Datetime(string='Date')
    product_id = fields.Many2one('product.template', string='Product Name')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')
    total = fields.Float(string='Total')

    # @api.one
    @api.depends('quantity', 'price_unit')
    def _compute_total_amount(self):
        self.total = self.quantity * self.price_unit

    # current_driver = fields.Many2one('hr.employee', string= 'Current Driver')
    mechanical = fields.Many2one('hr.employee', string='Mechanical')
    expense_type_id = fields.Many2one('expenses', string='Expense Type')
    location_id = fields.Many2one('stock.location', string='Stock Location')
    warehouse_account = fields.Many2one('account.account', string='Warehouse Account')
    note = fields.Html(string='Note')
    complete = fields.Boolean(string='Hide')

    # @api.one
    # @api.constrains('meter_read', 'quantity', 'price_unit')
    # def _check_digits(self):
    #     if len(str(self.meter_read)) > 9:
    #         raise ValidationError(_("Meter Read should not be more than 7 digits only"))
    #     if len(str(self.quantity)) > 3:
    #         raise ValidationError(_('Quantity should not be more than 3 digits only'))
    #     if len(str(self.price_unit)) > 3:
    #         raise ValidationError(_("Price Unit should not be more than 3 digits only."))

    # 
    def create_delivery_order(self):
        order_line = []
        expense_register_line = []
        delivery_order = self.env['stock.picking']
        expense_register = self.env['expense.register']
        picking_type_obj = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        order_line.append([0, False, {'product_id': self.product_id.id,
                                      'name': self.product_id.name,
                                      'product_uom_qty': self.quantity,
                                      'product_uom': self.product_id.uom_id.id,
                                      'price_unit': self.price_unit,
                                      'location_id': self.location_id.id,
                                      'location_dest_id': picking_type_obj.default_location_dest_id and picking_type_obj.default_location_dest_id.id
        }])
        self.env['stock.picking'].create({
            'date': self.date,
            'move_lines': order_line,
            'picking_type_id': picking_type_obj.id,
        })
        expense_register_line.append([0, False, {
            'expense_name': self.expense_type_id and self.expense_type_id.id or '',
            'number': self.quantity,
            'amount': self.price_unit,
            'total': self.total,
            'note': self.note,
        }])
        self.env['expense.register'].create({
            'date': self.date,
            'expense_register_level': 'car',
            'car_id': self.maintenance_id.new_car_id.id,
            'payment_method': 'warehouse',
            'location_id': self.location_id.id or False,
            'location_account': self.warehouse_account.id or False,
            'expense_register_line_ids': expense_register_line,
        })
        self.new_car_id = self.maintenance_id.new_car_id.id
        self.complete = True
        return True


# ######################## Machine Motor Lines################################
class machine_motor_line(models.Model):
    _name = 'machine.motor.line'
    _description = 'Register Machine Motor records'

    meter_read = fields.Float(string='Meter Read',digits=(15,3))
    maintenance_id = fields.Many2one('car.maintenance', string='Car Maintenance')
    new_car_id = fields.Many2one('new.car', string='Car')
    rent_id = fields.Many2one('rent', string='rend')
    machine_change_after = fields.Integer(string='Change Oil After', related='maintenance_id.machine_change_after')

    next_oil_change = fields.Float(string='Next Oil Change')

    # @api.one
    @api.depends('meter_read', 'machine_change_after')
    def _compute_next_oil_change(self):
        self.next_oil_change = self.meter_read + self.machine_change_after

    date = fields.Datetime(string='Date')
    product_id = fields.Many2one('product.template', string='Product Name')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')
    total = fields.Float(string='Total')

    # @api.one
    @api.depends('quantity', 'price_unit')
    def _compute_total_amount(self):
        self.total = self.quantity * self.price_unit

    # current_driver = fields.Many2one('hr.employee', string= 'Current Driver')
    mechanical = fields.Many2one('hr.employee', string='Mechanical')
    expense_type_id = fields.Many2one('expenses', string='Expense Type')
    location_id = fields.Many2one('stock.location', string='Stock Location')
    warehouse_account = fields.Many2one('account.account', string='Warehouse Account')
    note = fields.Html(string='Note')
    complete = fields.Boolean(string='Hide')

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     self.price_unit = self.product_id.standard_price

    # @api.one
    # @api.constrains('meter_read', 'quantity', 'price_unit')
    # def _check_digits(self):
    #     if len(str(self.meter_read)) > 7:
    #         raise ValidationError(_("Meter Read should not be more than 7 digits only"))
    #     if len(self.quantity) > 3:
    #         raise ValidationError(_('Quantity should not be more than 3 digits only'))
    #     if len(str(self.price_unit)) > 3:
    #         raise ValidationError(_("Price Unit should not be more than 3 digits only."))

    # 
    def create_delivery_order(self):
        order_line = []
        expense_register_line = []
        delivery_order = self.env['stock.picking']
        expense_register = self.env['expense.register']
        picking_type_obj = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        order_line.append([0, False, {'product_id': self.product_id.id,
                                      'name': self.product_id.name,
                                      'product_uom_qty': self.quantity,
                                      'product_uom': self.product_id.uom_id.id,
                                      'price_unit': self.price_unit,
                                      'location_id': self.location_id.id,
                                      'location_dest_id': picking_type_obj.default_location_dest_id and picking_type_obj.default_location_dest_id.id
        }])
        self.env['stock.picking'].create({
            'date': self.date,
            'move_lines': order_line,
            'picking_type_id': picking_type_obj.id,
        })
        expense_register_line.append([0, False, {
            'expense_name': self.expense_type_id and self.expense_type_id.id or '',
            'number': self.quantity,
            'amount': self.price_unit,
            'total': self.total,
            'note': self.note,
            'invoice': self.note,
            'filling_station': self.note,
        }])
        self.env['expense.register'].create({
            'date': self.date,
            'expense_register_level': 'car',
            'car_id': self.maintenance_id.new_car_id.id,
            'payment_method': 'warehouse',
            'location_id': self.location_id.id or False,
            'location_account': self.warehouse_account.id or False,
            'expense_register_line_ids': expense_register_line,
        })
        self.new_car_id = self.maintenance_id.new_car_id.id
        self.complete = True
        return True



