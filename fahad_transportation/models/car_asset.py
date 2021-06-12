# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import time
from collections import defaultdict


class vehicle_custody(models.Model):
    _name = 'vehicle.custody'
    _description = 'Link vehicle(car-tank) with driver'
    _inherit = ['mail.thread']

    name = fields.Char('Name')
    driver_id = fields.Many2one('hr.employee', string='Driver')
    decision_date = fields.Date(string='Decision Date', default=fields.Date.today)

    decision_type = fields.Selection([('deliver', 'Deliver'), ('receive', 'Receive')], string='Decision Type')
    vehicle_id = fields.Many2one('new.vehicle', string='Vehicle')
    new_car_id = fields.Many2one('new.car', string='Linked Car', related='vehicle_id.new_car_id')
    new_tank_id = fields.Many2one('new.tank', string='Linked Tank', related='vehicle_id.new_tank_id')
    note = fields.Html('Notes')
    driver_custody_ids = fields.One2many('driver.not.financial.custody', 'line_deliver_id', string='Driver Custody', )
    car_custody_ids = fields.One2many('car.not.financial.custody', 'line_deliver_id', string='Car Custody', )
    tank_custody_ids = fields.One2many('tank.not.financial.custody', 'line_deliver_id', string='Tank Custody', )
    driver_custody_to_warehouse = fields.One2many('driver.custody.warehouse.line', 'line_receive_id',
                                                  string='Return Custody')
    driver_custody_lost = fields.One2many('driver.custody.lost.line', 'line_receive_id', string='Lost Custody')
    car_custody_to_warehouse = fields.One2many('car.custody.warehouse.line', 'line_receive_id', string='Return Custody')
    car_custody_lost = fields.One2many('car.custody.lost.line', 'line_receive_id', string='Lost Custody')

    tank_custody_to_warehouse = fields.One2many('tank.custody.warehouse.line', 'line_receive_id',
                                                string='Return Custody')
    tank_custody_lost = fields.One2many('tank.custody.lost.line', 'line_receive_id', string='Lost Custody')
    state = fields.Selection([('draft', 'New'), ('review', 'Review'), ('confirm', 'Confirm'), ('close', 'Closed')], string='State',
                             default='draft', track_visibility='onchange')
    expense_account = fields.Many2one('account.account', string='Expense Account')
    custody_account = fields.Many2one('account.account', string='Custody Account')
    location = fields.Many2one('stock.location', string='Stock Location')
    account_journal = fields.Many2one('account.journal', string='Journal')
    dismantling_vehicle = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Dismantling Vehicle?')

    # @api.one
    @api.depends('new_tank_id', 'driver_id')
    def _get_name(self):
        self.name = self.driver_id.name + "-" + (self.new_tank_id.chasih_no or '')

    # @api.onchange('decision_type', 'driver_id')
    # def onchange_decision_type(self):
    #     driver_custody = []
    #     res = []
    #     vehicle_pool = self.env['new.vehicle']
    #     driver_pool = self.env['hr.employee']
    #     if self.decision_type == 'deliver':
    #         self.vehicle_id = False
    #         domain = [('state', '=', 'confirm'), ('state_of_dismantling', '=', 'connected'), ('has_driver', '=', False)]
    #         vehicles_obj = vehicle_pool.search(domain)
    #         vehicles_ids = [x.id for x in vehicles_obj]
    #         res = {'domain': {'vehicle_id': [('id', 'in', vehicles_ids)]}}
    #         if self.driver_id:
    #             driver_custody_ids = self.env['not.financial.custody'].search([('employee_id', '=', self.driver_id.id)])
    #             for obj in driver_custody_ids:
    #                 driver_custody.append((0, _, {'employee_id': obj.employee_id.id,
    #                                               'custody': obj.custody.id or False,
    #                                               'location': obj.location.id or False,
    #                                               'number': obj.number or 0,
    #                                               'unit_price': obj.unit_price or 0.0,
    #                                               'product_uom_id': obj.product_uom_id.id or False,
    #                                               'total': obj.total or 0.0,
    #                                               'custody_state': obj.custody_state or '',
    #                                               'delivery_date': obj.delivery_date or False,
    #                                               'state': obj.state or False,
    #                 }))  # this dict contain keys which are fields of one2many field
    #             self.driver_custody_ids = driver_custody
    #             # res.update({
    #             # 'value':{'driver_custody_ids': driver_custody}
    #             # })
    #     elif self.driver_id and self.decision_type == 'receive':
    #         vehicle_driver = self.env['new.vehicle'].search([('car_driver', '=', self.driver_id.id)])
    #         if len(vehicle_driver) != 0:
    #             self.vehicle_id = vehicle_driver[0].id
    #         if self.driver_id:
    #             driver_custody_ids = self.env['not.financial.custody'].search([('employee_id', '=', self.driver_id.id)])
    #             for obj in driver_custody_ids:
    #                 driver_custody.append((0, _, {'employee_id': obj.employee_id.id,
    #                                               'custody': obj.custody.id or False,
    #                                               'location': obj.location.id or False,
    #                                               'number': obj.number or 0,
    #                                               'unit_price': obj.unit_price or 0.0,
    #                                               'product_uom_id': obj.product_uom_id.id or False,
    #                                               'total': obj.total or 0.0,
    #                                               'custody_state': obj.custody_state or '',
    #                                               'delivery_date': obj.delivery_date or False,
    #                                               'state': obj.state or False,
    #                                               'driver_custody_line': obj.id
    #                 }))  # this dict contain keys which are fields of one2many field
    #             self.driver_custody_ids = driver_custody
    #     return res

    # @api.onchange('vehicle_id')
    # def onchange_vehicle_id(self):
    #     res = []
    #     car_custody = []
    #     tank_custody = []
    #     if self.vehicle_id:
    #         car_custody_ids = self.env['not.financial.custody'].search([('car_id', '=', self.vehicle_id.new_car_id.id)])
    #         tank_custody_ids = self.env['not.financial.custody'].search(
    #             [('tank_id', '=', self.vehicle_id.new_tank_id.id)])
    #         for obj in car_custody_ids:
    #             car_custody.append((0, _, {'car_id': obj.car_id.id,
    #                                        'custody': obj.custody.id or False,
    #                                        'location': obj.location.id or False,
    #                                        'number': obj.number or 0,
    #                                        'unit_price': obj.unit_price or 0.0,
    #                                        'product_uom_id': obj.product_uom_id.id or False,
    #                                        'total': obj.total or 0.0,
    #                                        'custody_state': obj.custody_state or '',
    #                                        'delivery_date': obj.delivery_date or False,
    #                                        'state': obj.state or '',
    #                                        'car_custody_line': obj.id,
    #             }))  # this dict contain keys which are fields of one2many field
    #         self.car_custody_ids = car_custody

    #         for obj in tank_custody_ids:
    #             tank_custody.append((0, _, {'tank_id': obj.tank_id.id,
    #                                         'custody': obj.custody.id or False,
    #                                         'location': obj.location.id or False,
    #                                         'number': obj.number or 0,
    #                                         'unit_price': obj.unit_price or 0.0,
    #                                         'product_uom_id': obj.product_uom_id.id or False,
    #                                         'total': obj.total or 0.0,
    #                                         'custody_state': obj.custody_state or '',
    #                                         'delivery_date': obj.delivery_date or False,
    #                                         'state': obj.state or False,
    #                                         'tank_custody_line': obj.id,
    #             }))  # this dict contain keys which are fields of one2many field
    #         self.tank_custody_ids = tank_custody
    #     # res = {'value': {'car_custody_ids': car_custody, 'tank_custody_ids':tank_custody}}
    #     return res

    # @api.one
    def reload_driver_custody_data(self):
        driver_not_financial_custody_obj = self.env['driver.not.financial.custody']
        driver_not_financial_custody_obj.search([['line_deliver_id','=',self.id]]).unlink()
        if self.decision_type == 'deliver':
            if self.driver_id:
                driver_custody_ids = self.env['not.financial.custody'].search([('employee_id', '=', self.driver_id.id)])
                for obj in driver_custody_ids:
                    dict=  {'employee_id': obj.employee_id.id,
                        'custody': obj.custody.id or False,
                        'location': obj.location.id or False,
                        'number': obj.number or 0,
                        'unit_price': obj.unit_price or 0.0,
                        'product_uom_id': obj.product_uom_id.id or False,
                        'total': obj.total or 0.0,
                        'custody_state': obj.custody_state or '',
                        'delivery_date': obj.delivery_date or False,
                        'state': obj.state or False,
                        'line_deliver_id': self.id,
                    }
                    driver_not_financial_custody_obj.create(dict)
        elif self.driver_id and self.decision_type == 'receive':
            if self.driver_id:
                driver_custody_ids = self.env['not.financial.custody'].search([('employee_id', '=', self.driver_id.id)])
                for obj in driver_custody_ids:
                    dict = {'employee_id': obj.employee_id.id,
                        'custody': obj.custody.id or False,
                        'location': obj.location.id or False,
                        'number': obj.number or 0,
                        'unit_price': obj.unit_price or 0.0,
                        'product_uom_id': obj.product_uom_id.id or False,
                        'total': obj.total or 0.0,
                        'custody_state': obj.custody_state or '',
                        'delivery_date': obj.delivery_date or False,
                        'state': obj.state or False,
                        'driver_custody_line': obj.id,
                        'line_deliver_id': self.id,
                    }  # this dict contain keys which are fields of one2many field
                    driver_not_financial_custody_obj.create(dict)

    # @api.one
    def reset_vehicle_data(self):
        car_not_financial_custody_obj = self.env['car.not.financial.custody']
        car_not_financial_custody_obj.search([['line_deliver_id', '=', self.id]]).unlink()
        tank_not_financial_custody_obj = self.env['tank.not.financial.custody']
        tank_not_financial_custody_obj.search([['line_deliver_id', '=', self.id]]).unlink()
        if self.vehicle_id:
            car_custody_ids = self.env['not.financial.custody'].search([('car_id', '=', self.vehicle_id.new_car_id.id)])
            tank_custody_ids = self.env['not.financial.custody'].search( [('tank_id', '=', self.vehicle_id.new_tank_id.id)])
            for obj in car_custody_ids:
                dict =  {'car_id': obj.car_id.id,
                    'custody': obj.custody.id or False,
                    'location': obj.location.id or False,
                    'number': obj.number or 0,
                    'unit_price': obj.unit_price or 0.0,
                    'product_uom_id': obj.product_uom_id.id or False,
                    'total': obj.total or 0.0,
                    'custody_state': obj.custody_state or '',
                    'delivery_date': obj.delivery_date or False,
                    'state': obj.state or '',
                    'car_custody_line': obj.id,
                    'line_deliver_id': self.id,
                }
                car_not_financial_custody_obj.create(dict)

            for obj in tank_custody_ids:
                dict =  {'tank_id': obj.tank_id.id,
                    'custody': obj.custody.id or False,
                    'location': obj.location.id or False,
                    'number': obj.number or 0,
                    'unit_price': obj.unit_price or 0.0,
                    'product_uom_id': obj.product_uom_id.id or False,
                    'total': obj.total or 0.0,
                    'custody_state': obj.custody_state or '',
                    'delivery_date': obj.delivery_date or False,
                    'state': obj.state or False,
                    'tank_custody_line': obj.id,
                    'line_deliver_id': self.id,
                }
                tank_not_financial_custody_obj.create(dict)

    # @api.one
    def button_review(self):
        self.reset_vehicle_data()
        self.reload_driver_custody_data()
        self.write({'state': 'review'})

    # @api.one
    def button_close(self):
        self.reset_vehicle_data()
        self.reload_driver_custody_data()
        self.write({'state': 'close'})

    # @api.model
    def _check_receiving_custody(self, rec):
        car_obj = self.env['new.car'].browse(rec.new_car_id.id)
        car_obj.write({'driver_id': False})
        tank_obj = self.env['new.tank'].browse(rec.new_tank_id.id)
        tank_obj.write({'driver_id': False})
        vehicle_obj = self.env['new.vehicle'].browse(rec.vehicle_id.id)
        vehicle_obj.write({'car_driver': False, 'has_driver': False})
        driver_custody = defaultdict(int)
        car_custody = defaultdict(int)
        tank_custody = defaultdict(int)
         #### Driver Custody ###
        for driver_return in rec.driver_custody_to_warehouse:
            driver_custody[driver_return.custody.id] += driver_return.number
            if driver_return.custody.id not in [line.custody.id for line in rec.driver_custody_ids]:
                raise ValidationError(_("Error!! \nYou are tring to recieve Custody not exist"))
        for driver_lost in rec.driver_custody_lost:
            driver_custody[driver_lost.custody.id] += driver_lost.number
            if driver_lost.custody.id not in [line.custody.id for line in rec.driver_custody_ids]:
                raise ValidationError(_("Error!! \nYou are tring to recieve Custody not exist"))
        for line in rec.driver_custody_ids:
            received_qty = driver_custody[line.custody.id]
            if received_qty > line.number:
                raise ValidationError(  _("Received Quantity is greater than delivered quantity"))
            elif received_qty == line.number:
                driver_custody_line = self.env['not.financial.custody'].browse(line.driver_custody_line.id)
                driver_custody_line.unlink()
                line.unlink()
            elif received_qty < line.number:
                driver_custody_line = self.env['not.financial.custody'].browse(line.driver_custody_line.id)
                driver_custody_line.write({'number': line.number - received_qty})
                custody_line = self.env['driver.not.financial.custody'].browse(line.id)
                custody_line.write({'number': line.number - received_qty})
        #### Car Custody ####
        for car_return in rec.car_custody_to_warehouse:
            car_custody[car_return.custody.id] += car_return.number
            if car_return.custody.id not in [line.custody.id for line in rec.car_custody_ids]:
                raise ValidationError(_("Error!! \nYou are tring to recieve Custody not exist"))
        for car_lost in rec.car_custody_lost:
            car_custody[car_lost.custody.id] += car_lost.number
            if car_lost.custody.id not in [line.custody.id for line in rec.car_custody_ids]:
                raise ValidationError(_("Error!! \nYou are tring to recieve Custody not exist"))
        for line in rec.car_custody_ids:
            received_qty = car_custody[line.custody.id]
            if received_qty > line.number:
                raise ValidationError(
                    _("Received Quantity is greater than delivered quantity"))
            elif received_qty == line.number:
                car_custody_line = self.env['not.financial.custody'].browse(line.car_custody_line.id)
                car_custody_line.unlink()
                line.unlink()
            elif received_qty < line.number:
                car_custody_line = self.env['not.financial.custody'].browse(line.car_custody_line.id)
                car_custody_line.write({'number': line.number - received_qty})
                custody_line = self.env['car.not.financial.custody'].browse(line.id)
                custody_line.write({'number': line.number - received_qty})
        #### Tank Custody ####
        for tank_return in rec.tank_custody_to_warehouse:
            tank_custody[tank_return.custody.id] += tank_return.number
            if tank_return.custody.id not in [line.custody.id for line in rec.tank_custody_ids]:
                raise ValidationError(_("Error!! \nYou are tring to recieve Custody not exist"))
        for tank_lost in rec.tank_custody_lost:
            tank_custody[tank_lost.custody.id] += tank_lost.number
            if tank_lost.custody.id not in [line.custody.id for line in rec.tank_custody_ids]:
                raise ValidationError(_("Error!! \nYou are tring to recieve Custody not exist"))
        for line in rec.tank_custody_ids:
            received_qty = tank_custody[line.custody.id]
            if received_qty > line.number:
                raise ValidationError(
                    _("Received Quantity is greater than delivered quantity"))
            elif received_qty == line.number:
                tank_custody_line = self.env['not.financial.custody'].browse(line.tank_custody_line.id)
                tank_custody_line.unlink()
                line.unlink()
            elif received_qty < line.number:
                tank_custody_line = self.env['not.financial.custody'].browse(line.tank_custody_line.id)
                tank_custody_line.write({'number': line.number - received_qty})
                custody_line = self.env['tank.not.financial.custody'].browse(line.id)
                custody_line.write({'number': line.number - received_qty})
        # raise ValidationError("End")
        return True

    # @api.model
    def _create_account_journal(self, rec):
        vals = {}
        line_vals = {}
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']
        vals.update({
            'journal_id': rec.account_journal.id,
            'date': rec.decision_date,
            'period_id': account_move._get_period(),
        })
        move = account_move.create(vals)
        if move:
            def create_account_move(line):
                line_vals['move_id'] = move.id
                line_vals['name'] = line.custody.name
                line_vals['period_id'] = account_move._get_period()
                if line.product_uom_id.uom_type != 'reference':
                    if line.product_uom_id.uom_type != 'bigger':
                        uom = line.product_uom_id.factor
                    else:
                        uom = 1 / line.product_uom_id.fator
                else:
                    uom = 1
                line_vals['name'] = u"إعادة عهدة الى المستودع من "+"%s - %s"% (rec.driver_id.name,rec.new_car_id.plaque_no)
                line_vals['debit'] = line.number * line.custody.standard_price * uom
                line_vals['credit'] = 0.0
                line_vals['account_id'] = rec.location.account_id.id
                account_move_line.create(line_vals)
                line_vals['debit'] = 0.0
                line_vals['credit'] = line.number * line.custody.standard_price * uom
                line_vals['account_id'] = rec.custody_account.id
                account_move_line.create(line_vals)

            for line in rec.driver_custody_to_warehouse:
                create_account_move(line)
                # line_vals['move_id'] = move.id
                # line_vals['name'] = line.custody.name
                # line_vals['period_id'] = account_move._get_period()
                # if line.product_uom_id.uom_type != 'reference':
                #     if line.product_uom_id.uom_type != 'bigger':
                #         uom = line.product_uom_id.factor
                #     else:
                #         uom = 1 / line.product_uom_id.fator
                # else:
                #     uom = 1
                # line_vals['name'] = "إعادة عهدة الى المستودع من "+"%s - %s"% rec.driver_id.name,rec.new_car_id.plaque_no
                # line_vals['debit'] = line.number * line.custody.standard_price * uom
                # line_vals['credit'] = 0.0
                # line_vals['account_id'] = rec.location.account_id.id
                # account_move_line.create(line_vals)
                # line_vals['debit'] = 0.0
                # line_vals['credit'] = line.number * line.custody.standard_price * uom
                # line_vals['account_id'] = rec.custody_account.id
                # account_move_line.create(line_vals)

            for line in rec.car_custody_to_warehouse:
                create_account_move(line)
                # line_vals['move_id'] = move.id
                # line_vals['name'] = line.custody.name
                # line_vals['period_id'] = account_move._get_period()
                # if line.product_uom_id.uom_type != 'reference':
                #     if line.product_uom_id.uom_type != 'bigger':
                #         uom = line.product_uom_id.fator
                #     else:
                #         uom = 1 / line.product_uom_id.fator
                # else:
                #     uom = 1
                # line_vals['debit'] = line.number * line.custody.standard_price * uom
                # line_vals['credit'] = 0.0
                # line_vals['account_id'] = rec.expense_account.id
                # account_move_line.create(line_vals)
                # line_vals['debit'] = 0.0
                # line_vals['credit'] = line.number * line.custody.standard_price * uom
                # line_vals['account_id'] = rec.location.account_id.id
                # account_move_line.create(line_vals)

            for line in rec.tank_custody_to_warehouse:
                create_account_move(line)
                # line_vals['move_id'] = move.id
                # line_vals['name'] = line.custody.name
                # line_vals['period_id'] = account_move._get_period()
                # if line.product_uom_id.uom_type != 'reference':
                #     if line.product_uom_id.uom_type != 'bigger':
                #         uom = line.product_uom_id.fator
                #     else:
                #         uom = 1 / line.product_uom_id.fator
                # else:
                #     uom = 1
                # line_vals['debit'] = line.number * line.custody.standard_price * uom
                # line_vals['credit'] = 0.0
                # line_vals['account_id'] = rec.expense_account.id
                # account_move_line.create(line_vals)
                # line_vals['debit'] = 0.0
                # line_vals['credit'] = line.number * line.custody.standard_price * uom
                # line_vals['account_id'] = rec.location.account_id.id
                # account_move_line.create(line_vals)
        return move

    # @api.model
    def _create_stock_picking(self, rec):
        picking_type_obj = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('default_location_dest_id', '=', self.location.id)])
        if len(picking_type_obj) != 0:
            picking_type_obj = picking_type_obj[0]
        else:
            raise ValidationError(_("The location witch you select don't have valid types of operation"))
        location_dest_id = picking_type_obj.default_location_src_id.id
        order_line = []
        discount_line = []
        for line in rec.driver_custody_to_warehouse:
            order_line.append([0, False, {'product_id': line.custody.id,
                                          'name': line.custody.name,
                                          'product_uom_qty': line.number,
                                          'product_uom': line.custody.uom_id.id,
                                          'price_unit': line.unit_price,
                                          'location_id': location_dest_id,
                                          'location_dest_id': rec.location.id,
            }])
        for line in rec.car_custody_to_warehouse:
            order_line.append([0, False, {'product_id': line.custody.id,
                                          'name': line.custody.name,
                                          'product_uom_qty': line.number,
                                          'product_uom': line.custody.uom_id.id,
                                          'price_unit': line.unit_price,
                                          'location_id': location_dest_id,
                                          'location_dest_id': rec.location.id,
            }])

        for line in rec.tank_custody_to_warehouse:
            order_line.append([0, False, {'product_id': line.custody.id,
                                          'name': line.custody.name,
                                          'product_uom_qty': line.number,
                                          'product_uom': line.custody.uom_id.id,
                                          'price_unit': line.unit_price,
                                          'location_id': location_dest_id,
                                          'location_dest_id': rec.location.id,
            }])
        self.env['stock.picking'].create({
            'move_lines': order_line,
            'is_internal': False,
            'picking_type_id': picking_type_obj.id,
        })

    # @api.model
    def _create_driver_penalties(self, rec):
        total = 0.0
        for line in rec.driver_custody_lost:
            total += line.driver_discount

        for line in rec.car_custody_lost:
            total += line.driver_discount

        for line in rec.tank_custody_lost:
            total += line.driver_discount
            if not self.driver_id.contract_id.id:
                raise ValidationError(_("This driver don't have contract"))
            if not self.driver_id.contract_id.active:
                raise ValidationError(_("This driver don't have active contract"))
        self.env['deduction.line'].create({
            'date': fields.Date.context_today(self),
            'amount': total,
            'cause': 'complete lost/damaged custody',
            'contract_id': self.driver_id.contract_id.id,
        })
        return True

    # @api.model
    def create_move_stock(self, rec):
        stock_move_obj = self.env['stock.move']
        product_obj = self.env['product.product']
        location_obj = self.env['stock.location']
        def _create_stock_move(line):
            product_id = product_obj.search([['product_tmpl_id','=',line.custody]])[0].id
            supplier_locations = location_obj.search([['usage','=','supplier']])
            if len(supplier_locations) == 0:
                raise ValidationError(_('Please define one location for supplieres in locations window'))

            stock_move_dict = {
                'product_id': product_id,
                'product_uom_qty':line.number ,
                'product_uom':line.product_uom_id.id ,
                'location_id':supplier_locations[0].id ,
                'location_dest_id':rec.location.id ,
            }
            stock = stock_move_obj.create(stock_move_dict)
            stock_move_obj.browse(stock).action_done()

        for line in rec.driver_custody_to_warehouse:
            _create_stock_move(line)

        for line in rec.car_custody_to_warehouse:
            _create_stock_move(line)

        for line in rec.tank_custody_to_warehouse:
            _create_stock_move(line)

    # @api.one
    def button_confirm(self):
        self.reset_vehicle_data()
        self.reload_driver_custody_data()
        for rec in self:
            if rec.decision_type == 'receive':
                if not self.location.account_id.id:
                    raise ValidationError(_("please select account for this location %s \n" % self.location.name))
                if self.new_car_id.driver_id.id != self.driver_id.id:
                    raise ValidationError(_("Car must be linked with this Driver"))
                if self.vehicle_id.state != 'confirm':
                    raise ValidationError(_("Vehicle must be confirmed"))
                new_dict = {}
                driver_history = {}
                self._check_receiving_custody(rec)
                if rec.driver_custody_to_warehouse or rec.tank_custody_to_warehouse or rec.car_custody_to_warehouse:
                    if rec.expense_account and rec.account_journal and rec.location:
                        self._create_account_journal(rec)
                        # self._create_stock_picking(rec)
                    else:
                        raise ValidationError(
                            _("Please, fill expense account and account journal and stock location"))
                if rec.driver_custody_lost or rec.car_custody_lost or rec.tank_custody_lost:
                    self._create_driver_penalties(rec)
                if rec.dismantling_vehicle == 'yes':
                    new_dict.update({
                        'vehicle_id': self.vehicle_id.id or False,
                        'uninstall_date': self.decision_date or False,
                        'Decision_no': self.decision_type or '',
                    })
                    dismantling = self.env['vehicle.dismantling'].create(new_dict)
                    dismantling.action_confirmed()
                    driver_history.update({
                        'driver_id': self.driver_id.id,
                        'vehicle_id': self.vehicle_id.id,
                        'car_id': self.vehicle_id.new_car_id.id,
                    })

                    self.env['driver.history'].create(driver_history)

                # if len(rec.car_custody_to_warehouse)!=0:
                #     self.create_move_stock(rec)
            else:
                car_obj = self.env['new.car'].browse(self.new_car_id.id)
                car_obj.write({'driver_id': self.driver_id.id})
                tank_obj = self.env['new.tank'].browse(self.new_tank_id.id)
                tank_obj.write({'driver_id': self.driver_id.id})
                vehicle_obj = self.env['new.vehicle'].browse(self.vehicle_id.id)
                vehicle_obj.write({'car_driver': self.driver_id.id, 'has_driver': True})
        self.write({'state': 'confirm'})


    # 
    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise Warning(_('You cannot delete confirmed expense'))
        return super(vehicle_custody, self).unlink()


class car_not_financial_custody(models.Model):
    _name = 'car.not.financial.custody'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')
    custody_state = fields.Selection([('new', 'New'), ('used', 'Used')], string='Custody State')
    state = fields.Selection([('deliver', 'Deliver'), ('receive', 'Receive')], string='State')
    delivery_date = fields.Datetime(string='Delivery Date')
    note = fields.Char('Note')
    car_id = fields.Many2one('new.car', 'Car')
    line_deliver_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')
    car_custody_line = fields.Many2one('not.financial.custody', 'line_id')


class tank_not_financial_custody(models.Model):
    _name = 'tank.not.financial.custody'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')
    custody_state = fields.Selection([('new', 'New'), ('used', 'Used')], string='Custody State')
    state = fields.Selection([('deliver', 'Deliver'), ('receive', 'Receive')], string='State')
    delivery_date = fields.Datetime(string='Delivery Date')
    note = fields.Char('Note')
    tank_id = fields.Many2one('new.tank', 'Tank')
    line_deliver_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')
    tank_custody_line = fields.Many2one('not.financial.custody', 'line_id')


class driver_not_financial_custody(models.Model):
    _name = 'driver.not.financial.custody'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')
    custody_state = fields.Selection([('new', 'New'), ('used', 'Used')], string='Custody State')
    state = fields.Selection([('deliver', 'Deliver'), ('receive', 'Receive')], string='State')
    delivery_date = fields.Datetime(string='Delivery Date')
    note = fields.Char('Note')
    driver_id = fields.Many2one('hr.employee', 'Driver')
    line_deliver_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')
    driver_custody_line = fields.Many2one('not.financial.custody', 'line_id')


class driver_custody_warehouse_line(models.Model):
    _name = 'driver.custody.warehouse.line'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')
    note = fields.Char('Note')
    line_receive_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')

    # @api.one
    @api.depends('line_receive_id')
    def _get_uom(self):
        uom_id = False
        if self.line_receive_id.id:
            for line in self.line_receive_id.driver_custody_ids:
                if line.custody.id == self.custody.id:
                    uom_id = line.product_uom_id.id
        self.product_uom_id=uom_id


class driver_custody_lost_line(models.Model):
    _name = 'driver.custody.lost.line'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')

    # @api.one
    @api.depends('unit_price', 'number')
    def _compute_total(self):
        self.total = self.unit_price * self.number

    driver_discount = fields.Float(string='Deduct From Driver')

    # 
    @api.constrains('driver_discount')
    def _check_driver_discount(self):
        if self.driver_discount > self.total:
            raise ValidationError('Driver Discount Can not be greater than total')

    line_receive_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')
    note = fields.Char('Note')

    # @api.onchange('custody')
    # def onchange_custody_id(self):
    #     self.unit_price = self.custody.standard_price


class car_custody_warehouse_line(models.Model):
    _name = 'car.custody.warehouse.line'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')
    note = fields.Char('Note')
    line_receive_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')

    # @api.one
    @api.depends('line_receive_id')
    def _get_uom(self):
        uom_id =False
        if self.line_receive_id.id:
            for line in self.line_receive_id.car_custody_ids:
                if line.custody.id == self.custody.id:
                    uom_id = line.product_uom_id.id
        self.product_uom_id = uom_id


class car_custody_lost_line(models.Model):
    _name = 'car.custody.lost.line'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')

    # 
    @api.depends('unit_price', 'number')
    def _compute_total(self):
        self.total = self.unit_price * self.number


    driver_discount = fields.Float(string='Deduct From Driver')

    # @api.one
    @api.constrains('driver_discount')
    def _check_driver_discount(self):
        if self.driver_discount > self.total:
            raise ValidationError('Driver Discount Can not be greater than total')
        return True

    line_receive_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')
    note = fields.Char('Note')

    # @api.onchange('custody')
    # def onchange_custody_id(self):
    #     self.unit_price = self.custody.standard_price


class tank_custody_warehouse_line(models.Model):
    _name = 'tank.custody.warehouse.line'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')
    note = fields.Char('Note')
    line_receive_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')

    # @api.one
    @api.depends('line_receive_id')
    def _get_uom(self):
        uom_id = False
        if self.line_receive_id.id:
            for line in self.line_receive_id.tank_custody_ids:
                if line.custody.id == self.custody.id:
                    uom_id = line.product_uom_id.id
        self.product_uom_id = uom_id


class tank_custody_lost_line(models.Model):
    _name = 'tank.custody.lost.line'

    custody = fields.Many2one('product.template', string='Custody')
    location = fields.Many2one('stock.location', string='Location')
    number = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom', string='UOM')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Total')

    # @api.one
    @api.depends('unit_price', 'number')
    def _compute_total(self):
        total =  self.unit_price * self.number
        self.total = total


    driver_discount = fields.Float(string='Deduct From Driver')

    # @api.one
    @api.constrains('driver_discount')
    def _check_driver_discount(self):
        if self.driver_discount > self.total:
            raise ValidationError('Driver Discount Can not be greater than total')
        return True

    line_receive_id = fields.Many2one('vehicle.custody', 'Vehicle Custody')
    note = fields.Char('Note')

    # @api.onchange('custody')
    # def onchange_custody_id(self):
    #     self.unit_price = self.custody.standard_price


class driver_history(models.Model):
    _name = 'driver.history'

    driver_id = fields.Many2one('hr.employee', 'Driver Name')
    vehicle_id = fields.Many2one('new.vehicle', 'Vehicle')
    car_id = fields.Many2one('new.car', 'Car')