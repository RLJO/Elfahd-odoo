# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import collections
import time


class new_wheel(models.Model):
    _name = 'new.wheel'
    _description = 'wheel definition'
    _inherit = ['mail.thread']
    _order = "id desc"
    _rec_name = 'wheel_no'

    code = fields.Char(string='Code')
    wheel_no = fields.Char(string='Wheel No.')

    # 
    @api.constrains('wheel_no')
    def _check_repeat_wheel_no(self):
        for r in self:
            if self.search([('wheel_no', '!=', False), ('wheel_no', '!=', ''), ('wheel_no', '=', r.wheel_no),
                            ('id', '!=', r.id)]):
                raise ValidationError(_("Wheel No must be unique"))

    manufacturing_company_id = fields.Many2one('z.manufacture', string='Wheel brand')
    size = fields.Float(string='Size')
    install_type = fields.Selection([('vehicle', 'Vehicle'), ('tank', 'Tank'), ('both', 'Both')], string='Wheel Installment Type', )
    car_category_ids = fields.Many2many('car.category', 'car_wheel_category', 'wheel_id', 'car_id', string='Car Category', )
    wheel_status = fields.Selection([('new', 'New'), ('used', 'Used'), ], string='Wheel Status', )
    supplier_code = fields.Char(string='Supplier Code')
    purchase_price = fields.Float(string='Purchase Price')
    purchase_date = fields.Date(string='Purchase date')
    supplier_id = fields.Many2one('res.partner', string='Supplier Id')
    supplier_invoice_type = fields.Selection([('no_invoice', 'Do Not Create Invoice'), ('invoiced', 'Create Invoice')], string='Supplier Invoice Type',
                                             default='no_invoice', readonly=1)
    expense_account = fields.Many2one('account.account', string='Warehouse Account')
    expense_journal = fields.Many2one('account.journal', string='Expense Journal')
    journal_id = fields.Many2one('account.journal', string='Journal')
    estimated_life = fields.Float(string='Estimated Life')
    supplier = fields.One2many('wheel.supplier', 'wheel_id', string='Supplier')
    purchase_id = fields.Many2one('wheel.purchase', 'Purchase Order')
    state = fields.Selection([('draft', 'New'), ('reviewed', 'Reviewed'), ('confirmed', 'Confirmed'), ('used', 'Used'),
                              ('installed', 'Installed'), ('damaged', 'Damaged'), ('sold', 'Sold'),
                              ('closed', 'Closed')], string='State', default='draft', track_visibility='onchange')

    install_history_ids = fields.One2many('wheel.action.lines.install', 'wheel_id', 'Install History')
    uninstall_history_ids = fields.One2many('wheel.action.lines.uninstall', 'wheel_id', 'Uninstall History', )
    wheel_expense_account_id = fields.Many2one('account.account', "Wheels expenses account")
    wheel_expense_journal_id = fields.Many2one('account.journal', "wheels expenses journal")
    location_id = fields.Many2one('stock.location', 'Location')

    # @api.one
    @api.constrains('estimated_life')
    def _check_estimated_life_non_zeros(self):
        if self.estimated_life <= 0:
            raise ValidationError('Estimated life Can not be zero')
        return True

    # @api.one
    @api.constrains('purchase_price')
    def _check_purchase_price_non_zeros(self):
        if self.purchase_price <= 0:
            raise ValidationError('Purchase Price Can not be zero')
        return True



    # 
    def unlink(self):
        raise ValidationError(_('you can not delete wheel '))

    # @api.one
    def button_review(self):
        self.code = self.env['ir.sequence'].next_by_code('new.wheel')
        if self.install_type == 'both' and (not self.car_category_ids):
            raise ValidationError(_("Please enter Car Category !!"))
        self.write({'state': 'reviewed'})

    # @api.one
    def button_confirmed(self):
        if self.install_type == 'both' and (not self.car_category_ids):
            raise ValidationError(_("Please enter Car Category !!"))
        for record in self:
            if record.wheel_status == 'used':
                record.write({'state': 'used'})
            else:
                record.write({'state': 'confirmed'})
            if not record.purchase_id:
                if record.supplier_invoice_type == 'invoiced':
                    invoice_vals = {
                        'partner_id': record.supplier_id and record.supplier_id.id,
                        'type': 'in_invoice',
                        'journal_id': record.journal_id and record.journal_id.id,
                        'account_id': record.supplier_id.property_account_payable and record.supplier_id.property_account_payable.id,
                        'date_invoice': fields.Date.context_today(self),
                        'invoice_line': [(0, _, {'name': record.code + ' ' + record.size, 'quantity': 1,
                                                 'price_unit': record.purchase_price})],
                    }
                    self.env['account.account'].create(invoice_vals)
                    # invoice
        return True

    # 
    def button_closed(self):
        if self.state != 'closed':
            raise ValidationError(_("You can not close more that once"))
        if not self.uninstall_history_ids:
            account_move_obj = self.env['account.move']
            account_move_line_obj = self.env['account.move.line']
            vals = {
                'journal_id': self.wheel_expense_journal_id.id,
                'date': time.strftime('%Y-%m-%d'),
                'period_id': account_move_obj._get_period()
            }
            move_id = account_move_obj.create(vals)
            vals['move_id'] = move_id.id
            vals['name'] = 'اغلاق اطار رقم "%s" '.decode('utf-8') % self.wheel_no
            vals['account_id'] = self.wheel_expense_account_id.id
            vals['debit'] = self.purchase_price
            account_move_line_obj.create(vals)
            vals['debit'] = 0.0
            vals['credit'] = self.purchase_price
            vals['account_id'] = self.expense_account.id
            account_move_line_obj.create(vals)

        return self.write({'state': 'closed'})


class wheel_supplier(models.Model):
    _name = 'wheel.supplier'

    supplier_id = fields.Many2one('res.partner', 'Supplier')
    supplier_product = fields.Char(string='Supplier Product Name')
    supplier_product_code = fields.Char(string='Supplier Product Code')
    wheel_id = fields.Many2one('new.wheel', string='Wheel Id')


################## wheel action ###################


class wheel_action(models.Model):
    _name = 'wheel.action'
    _description = 'Register actions on wheel'
    _inherit = ['mail.thread']
    _rec_name = 'decision_date'
    _order = "id desc"

    decision_date = fields.Date(string='Decision Date')
    install_on = fields.Selection([('vehicle', 'Car'),
                                   ('tank', 'Tank')], string='Installed on')
    vehicle_id = fields.Many2one('new.car', string='Car')
    basic_wheel_no_id = fields.Integer(string='Car Basic Wheel No', related="vehicle_id.basic_wheel_no")
    backup_wheel_no_id = fields.Integer(string='Car Backup Wheel No', related="vehicle_id.backup_wheel_no")
    current_wheel_no_id = fields.Integer(string='Car Installed Wheel No', related="vehicle_id.current_wheel_no")
    car_free_places = fields.Integer(string='Car Installed Wheel No', related="vehicle_id.free_places")
    vehicle_wheel_no = fields.Integer(string='Total Wheels No')
    employee_id = fields.Many2one('hr.employee', 'Mechanical')

    # 
    @api.depends('basic_wheel_no_id', 'backup_wheel_no_id', 'current_wheel_no_id')
    def _compute_vehicle_wheel_no(self):
        self.vehicle_wheel_no = self.basic_wheel_no_id + self.backup_wheel_no_id

    tank_id = fields.Many2one('new.tank', string='Tank')
    # ToDO make the coming three fields related
    t_basic_wheel_no_id = fields.Integer(string='Tank Basic Wheel No', related="tank_id.basic_wheel_no")
    t_backup_wheel_no_id = fields.Integer(string='Tank Backup Wheel No', related="tank_id.backup_wheel_no")
    t_current_wheel_no_id = fields.Integer(string='Tank Current Wheel No', related="tank_id.current_wheel_no")
    tank_free_places = fields.Integer(string='Tank Current Wheel No', related="tank_id.free_places")
    tank_wheel_no = fields.Integer(string='Tank Wheel No')

    # 
    @api.depends('t_basic_wheel_no_id', 't_backup_wheel_no_id', 't_current_wheel_no_id')
    def _compute_tank_wheel_no(self):
        self.tank_wheel_no = self.t_basic_wheel_no_id + self.t_backup_wheel_no_id

    order_type = fields.Selection([
        ('install', 'Install'),
        ('uninstall', 'Uninstall'),
        # ('uninstall_install', 'Uninstall Old / Install New'),
    ],
        string='Order Type', )
    install_decision = fields.One2many('wheel.action.lines.install', 'action_id', 'Install Decision',
                                       # domain=[('action_status', '=', 'confirmed')]
                                       )
    uninstall_decision = fields.One2many('wheel.action.lines.uninstall', 'action_id', 'UnInstall Decision',
                                         # domain=[('action_status', '=', 'confirmed')]
                                         )
    state = fields.Selection([('draft', 'New'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('closed', 'Closed')], string='State', default='draft', track_visibility='onchange')
    notes = fields.Html(string='Notes')


    # 
    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise ValidationError(_('You cannot delete confirmed wheel action'))
        return super(wheel_action, self).unlink()



    # 
    def write(self, vals):
        if 'install_decision' in vals.keys():
            xxx = self.env['new.car'].browse(self.vehicle_id.id) if self.install_on == 'vehicle' else self.env[
                'new.tank'].browse(self.tank_id.id)
            lines = []
            for line in vals['install_decision']:
                if line[0] != 2:
                    lines.append(line)
            if len(lines) > xxx.free_places:
                raise ValidationError(_("You are trying to install number of wheels more than empty wheels"))
        return super(wheel_action, self).write(vals)

    # @api.one
    def button_review(self):
        for record in self:
            list_ids = []
            wheel_list = []
            for line in record.install_decision:
                list_ids.append(line.install_place_.id)
                wheel_list.append(line.wheel_id.id)
            res = [item for item, count in collections.Counter(list_ids).items() if count > 1]
            wheel_res = [item for item, count in collections.Counter(wheel_list).items() if count > 1]
            if res:
                raise ValidationError(_('You Can not install Two Wheel in Same Place'))
            if wheel_res:
                raise ValidationError(_('You Can not install The same wheel in two places'))
        self.write({'state': 'reviewed'})

    # 
    def button_confirmed(self):
        for rec in self:
            # ############## Req. V2.0 #######################
            if rec.order_type == 'install':
                if rec.install_on == 'vehicle':
                    if rec.vehicle_id:
                        for line in rec.install_decision:
                            matched = False
                            for place in rec.vehicle_id.action_place_ids:
                                if place.action_place_id == line.install_place_:
                                    if place.linked_wheel_id:
                                        raise ValidationError(_('Sorry , there is another wheel linked to this place'))
                                    else:
                                        place.linked_wheel_id = line.wheel_id.id
                                        matched = True
                            if not matched:
                                raise ValidationError(_("Sorry \nThe following place  not exist in the car\n\"%s\"" % (line.install_place_.name)))
                else:
                    if rec.tank_id:
                        for line in rec.install_decision:
                            matched = False
                            for place in rec.tank_id.action_place_ids:
                                if place.action_place_id == line.install_place_:
                                    if place.linked_wheel_id:
                                        raise ValidationError(_('Sorry , there is another wheel linked to this place'))
                                    else:
                                        place.linked_wheel_id = line.wheel_id.id
                                        matched = True
                            if not matched:
                                raise ValidationError(_("Sorry \nThe following place  not exist in the tank\n\"%s\"" % (line.install_place_.name)))
            if rec.order_type == 'uninstall':
                if rec.install_on == 'vehicle':
                    if rec.vehicle_id:
                        for line in rec.uninstall_decision:
                            for place in rec.vehicle_id.action_place_ids:
                                if place.action_place_id == line.install_place_:
                                    if place.linked_wheel_id != line.wheel_id:
                                        # raise ValidationError(_('Sorry , this wheel is no longer linked to this place'))
                                        pass
                                    else:
                                        place.linked_wheel_id = False
                else:
                    if rec.tank_id:
                        for line in rec.uninstall_decision:
                            for place in rec.tank_id.action_place_ids:
                                if place.action_place_id == line.install_place_:
                                    if place.linked_wheel_id != line.wheel_id:
                                        # raise ValidationError(_('Sorry , this wheel is no longer linked to this place'))
                                        pass
                                    else:
                                        place.linked_wheel_id = False
            # ############## End of Req. V2.0 ##############################
            if self.order_type == 'install':
                xxx = rec.vehicle_id if self.install_on == 'vehicle' else rec.tank_id
                if (not xxx.for_wheel_action) or (xxx.state not in ['confirm', 'rent', 'connect']):
                    raise ValidationError(
                        _("You cannot confirm install to this %s" % _('Car') if rec.install_on == 'vehicle' else _(
                            'Tank')))
            for line in rec.install_decision:
                if line.wheel_id.state not in ['confirmed', 'used']:
                    raise ValidationError(_("Wheel %s must be confirmed or used" % line.wheel_id.wheel_no))
                history = [x for x in line.wheel_id.uninstall_history_ids]
                if line.wheel_status == 'confirmed' or (line.wheel_status == 'used' and len(history) == 0):
                    move_obj = self.env['account.move']
                    move_line_obj = self.env['account.move.line']
                    move_vals = {}
                    move_line_vals = {}
                    move_vals['period_id'] = move_obj._get_period()
                    move_vals['date'] = time.strftime('%Y-%m-%d')
                    move_vals['journal_id'] = line.wheel_id.wheel_expense_journal_id.id
                    move_id = move_obj.create(move_vals)
                    line.move_id = move_id.id
                    install_on = 'Car ' + str(rec.vehicle_id.plaque_no.encode('utf-8')) if rec.install_on == 'vehicle' \
                        else 'Tank ' + str(rec.tank_id.chasih_no)
                    move_line_vals['name'] = 'install wheel No %s on %s' % (
                        line.wheel_id.wheel_no.encode('utf-8'), install_on)
                    move_line_vals['move_id'] = move_id.id
                    move_line_vals['debit'] = line.wheel_id.purchase_price
                    move_line_vals['account_id'] = line.wheel_id.wheel_expense_account_id.id
                    move_line_vals['journal_id'] = line.wheel_id.wheel_expense_journal_id.id
                    move_line_vals['date'] = time.strftime('%Y-%m-%d')
                    move_line_vals['period_id'] = move_obj._get_period()
                    move_line_obj.create(move_line_vals)
                    move_line_vals['debit'] = 0.0
                    move_line_vals['credit'] = line.wheel_id.purchase_price
                    move_line_vals['account_id'] = line.wheel_id.expense_account.id
                    move_line_obj.create(move_line_vals)
                    line.write({'show_in_history': True})
                    ## if Install on External Thing
                    install_on = line.action_id.install_on == 'vehicle' and line.action_id.vehicle_id or line.action_id.tank_id
                    external = (install_on.ownership == 'external')
                    if external:
                        move_obj = self.env['account.move']
                        move_line_obj = self.env['account.move.line']
                        vals = {
                            'journal_id': line.wheel_id.wheel_expense_journal_id.id,
                            'period_id': move_obj._get_period(),
                            'date': time.strftime('%Y-%m-%d')
                        }
                        move_id = move_obj.create(vals)
                        vals['move_id'] = move_id.id
                        vals['debit'] = line.wheel_id.purchase_price
                        external_owner = line.action_id.install_on == 'vehicle' and \
                                         line.action_id.vehicle_id.external_ownership or line.action_id.tank_id.tank_owner
                        vals['account_id'] = external_owner.property_account_payable.id
                        vals['partner_id'] = external_owner.id
                        vals['name'] = 'تحميل تكلفة الاطار على مالك المركبه / التانك '.decode('utf-8')
                        move_line_obj.create(vals)
                        vals['patner_id'] = False
                        vals['debit'] = 0.0
                        vals['credit'] = line.wheel_id.purchase_price
                        vals['account_id'] = line.wheel_id.wheel_expense_account_id.id
                        move_line_obj.create(vals)
            list_ids = []
            wheel_list = []
            for line in rec.install_decision:
                list_ids.append(line.install_place_.id)
                wheel_list.append(line.wheel_id.id)
            for line in rec.uninstall_decision:
                if line.select and line.wheel_id.state != 'installed':
                    raise ValidationError(_("The wheel %s must be installed" % line.wheel_id.wheel_no))

            res = [item for item, count in collections.Counter(list_ids).items() if count > 1]
            wheel_res = [item for item, count in collections.Counter(wheel_list).items() if count > 1]
            if res:
                raise ValidationError(_('You Can not install Two Wheel in Same Place'))
            if wheel_res:
                raise ValidationError(_('You Can not install The same wheel in two places'))
            if rec.install_on == 'vehicle':
                if rec.order_type == 'install':
                    for line in rec.install_decision:
                        vals = {}
                        vals.update({
                            'date': rec.decision_date or '',
                            'payment_method': '',
                            'expense_name': line.wheel_id.code + '' + line.wheel_id.wheel_no or '',
                            'quantity': 1,
                            'amount': line.wheel_id.purchase_price or 0.0,
                            'total_amount': line.wheel_id.purchase_price or 0.0,
                            'note': line.install_place_.name or 'Empty',
                            'new_car_id': rec.vehicle_id and rec.vehicle_id.id or False

                        })
                        self.env['wheel.expenses'].create(vals)
                        wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                        wheel_obj.write({'state': 'installed'})
                        line_obj = self.env['wheel.action.lines.install'].browse(line.id)
                        line_obj.write({'car_id': rec.vehicle_id.id})
                if rec.order_type == 'uninstall_install':
                    uninstalled_wheels = [line for line in rec.uninstall_decision if line.select]
                    if len(rec.install_decision) != len(uninstalled_wheels):
                        raise Warning(_('New Installed Wheels Must Be equal Uninstalled Wheels'))
                    for line in rec.install_decision:
                        vals = {}
                        if line.wheel_id.wheel_status == 'new':
                            vals.update({
                                'date': rec.decision_date or '',
                                'payment_method': '',
                                'expense_name': line.wheel_id.code + '' + line.wheel_id.wheel_no or '',
                                'quantity': 1,
                                'amount': line.wheel_id.purchase_price or 0.0,
                                'total_amount': line.wheel_id.purchase_price or 0.0,
                                'note': line.install_place_.name or '',
                                'new_car_id': rec.vehicle_id and rec.vehicle_id.id or False
                            })
                            self.env['wheel.expenses'].create(vals)
                            wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                            # wheel_obj.write({'state': 'installed'})
                            line_obj = self.env['wheel.action.lines.install'].browse(line.id)
                            line_obj.write({'car_id': rec.vehicle_id.id})
                    for line in rec.uninstall_decision:
                        wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                        wheel_obj.write({'state': line.wheel_status})
                        line_obj = self.env['wheel.action.lines.uninstall'].browse(line.id)
                        line_obj.write({'car_id': rec.vehicle_id.id})
                        results_obj = self.env['wheel.action.lines.install'].search(
                            [('wheel_id', '=', line.wheel_id.id), ('car_id', '=', rec.vehicle_id.id)])
                        # results_obj.unlink()
                if rec.order_type == 'uninstall':
                    for line in rec.uninstall_decision:
                        if line.select:
                            wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                            wheel_obj.write({'state': line.wheel_status})
                            line_obj = self.env['wheel.action.lines.uninstall'].browse(line.id)
                            line_obj.write({'car_id': rec.vehicle_id.id})
                            results_obj = self.env['wheel.action.lines.install'].search(
                                [('wheel_id', '=', line.wheel_id.id), ('car_id', '=', rec.vehicle_id.id)])
                            results_obj.unlink()

            if rec.install_on == 'tank':
                if rec.order_type == 'install':
                    if rec.tank_id.state == 'connected':
                        for line in rec.install_decision:
                            vals = {}
                            if line.wheel_id.wheel_status == 'new':
                                vals.update({
                                    'date': rec.decision_date or '',
                                    'payment_method': '',
                                    'expense_name': line.wheel_id.code + '' + line.wheel_id.wheel_no or '',
                                    'quantity': 1,
                                    'amount': line.wheel_id.purchase_price or 0.0,
                                    'total_amount': line.wheel_id.purchase_price or 0.0,
                                    'note': line.install_place_.name or '',
                                    'new_car_id': rec.tank_id.car_id and rec.tank_id.car_id.id or False

                                })
                            self.env['wheel.expenses'].create(vals)
                            wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                            wheel_obj.write({'state': 'installed'})
                            line_obj = self.env['wheel.action.lines.install'].browse(line.id)
                            line_obj.write({'tank_id': rec.tank_id.id})

                    else:
                        for line in rec.install_decision:
                            vals = {}
                            if line.wheel_id.wheel_status == 'new':
                                vals.update({
                                    'date': rec.decision_date or '',
                                    'payment_method': '',
                                    'expense_name': line.wheel_id.code + '' + line.wheel_id.wheel_no or '',
                                    'quantity': 1,
                                    'amount': line.wheel_id.purchase_price or 0.0,
                                    'total_amount': line.wheel_id.purchase_price or 0.0,
                                    'note': line.install_place_.name or '',
                                    'new_tank_id': rec.tank_id and rec.tank_id.id or False

                                })
                            self.env['wheel.expenses'].create(vals)
                            wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                            wheel_obj.write({'state': 'installed'})
                            line_obj = self.env['wheel.action.lines.install'].browse(line.id)
                            line_obj.write({'tank_id': rec.tank_id.id})

                if rec.order_type == 'uninstall_install':
                    uninstalled_wheels = [line for line in rec.uninstall_decision if line.select]
                    if len(rec.install_decision) != len(uninstalled_wheels):
                        raise Warning(_('New Installed Wheels Must Be equal Uninstalled Wheels'))
                    for line in rec.install_decision:
                        vals = {}
                        if rec.tank_id.state == 'connected':
                            if line.wheel_id.wheel_status == 'new':
                                vals.update({
                                    'date': rec.decision_date or '',
                                    'payment_method': '',
                                    'expense_name': line.wheel_id.code + '' + line.wheel_id.wheel_no or '',
                                    'quantity': 1,
                                    'amount': line.wheel_id.purchase_price or 0.0,
                                    'total_amount': line.wheel_id.purchase_price or 0.0,
                                    'note': line.install_place_.action_place_id.name or '',
                                    'new_tank_id': rec.tank_id and rec.tank_id.id or False
                                })
                            self.env['wheel.expenses'].create(vals)
                            wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                            wheel_obj.write({'state': line.wheel_status})
                            line_obj = self.env['wheel.action.lines.uninstall'].browse(line.id)

                            line_obj.write({'tank_id': rec.tank_id.id})
                            results_obj = self.env['wheel.action.lines.install'].search(
                                [('wheel_id', '=', line.wheel_id.id), ('tank_id', '=', rec.tank_id.id)])
                            results_obj.unlink()
                            # self.env['wheel.action.lines.install'].write(line.id, {'car_id': rec.tank_id.new_car_id.id})

                        else:
                            for line in rec.install_decision:
                                vals = {}
                                if line.wheel_id.wheel_status == 'new':
                                    vals.update({
                                        'date': rec.decision_date or '',
                                        'payment_method': '',
                                        'expense_name': line.wheel_id.code + '' + line.wheel_id.wheel_no or '',
                                        'quantity': 1,
                                        'amount': line.wheel_id.purchase_price or 0.0,
                                        'total_amount': line.wheel_id.purchase_price or 0.0,
                                        'note': line.install_place_.name or '',
                                        'new_tank_id': rec.tank_id and rec.tank_id.id or False

                                    })
                                self.env['wheel.expenses'].create(vals)
                                wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                                wheel_obj.write({'state': 'installed'})
                                line_obj = self.env['wheel.action.lines.install'].browse(line.id)
                                line_obj.write({'tank_id': rec.tank_id.id})

                    for line in rec.uninstall_decision:
                        wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                        wheel_obj.write({'state': line.wheel_status})
                        line_obj = self.env['wheel.action.lines.uninstall'].browse(line.id)
                        line_obj.write({'tank_id': rec.tank_id.id})
                        results_obj = self.env['wheel.action.lines.install'].search(
                            [('wheel_id', '=', line.wheel_id.id), ('tank_id', '=', rec.tank_id.id)])
                        results_obj.unlink()

                if rec.order_type == 'uninstall':
                    for line in rec.uninstall_decision:
                        if line.select:
                            wheel_obj = self.env['new.wheel'].browse(line.wheel_id.id)
                            wheel_obj.write({'state': line.wheel_status})
                            line_obj = self.env['wheel.action.lines.uninstall'].browse(line.id)
                            line_obj.write({'tank_id': rec.tank_id.id})
                            results_obj = self.env['wheel.action.lines.install'].search(
                                [('wheel_id', '=', line.wheel_id.id), ('tank_id', '=', rec.tank_id.id)])
                            results_obj.unlink()

        return self.write({'state': 'confirmed'})

    # @api.one
    def button_closed(self):
        return self.write({'state': 'closed'})

    # @api.one
    @api.constrains('order_type', 'uninstall_decision')
    def _check_install_decision(self):
        if self.order_type in ['uninstall', 'uninstall_install']:
            for line in self.uninstall_decision:
                if line.select:
                    return True
            raise ValidationError(_("You Should select one line at least in uninstall decision"))


class wheel_action_lines_install(models.Model):
    _name = 'wheel.action.lines.install'
    _description = 'register wheel installed on vehicle or tank'

    wheel_id = fields.Many2one('new.wheel', 'Wheel NO.')
    wheel_code = fields.Char('Wheel Code', related="wheel_id.code")
    size = fields.Float('Size', related="wheel_id.size")
    wheel_status = fields.Selection(
        [('draft', 'New'), ('reviewed', 'Reviewed'), ('confirmed', 'Confirmed'), ('used', 'Used'),
         ('installed', 'Installed'), ('damaged', 'Damaged'), ('sold', 'Sold'),
         ('closed', 'Closed')], string='State', related="wheel_id.state")
    action_status = fields.Selection([('draft', 'New'),
                                      ('reviewed', 'Reviewed'),
                                      ('confirmed', 'Confirmed'),
                                      ('closed', 'Closed')], string='Action State', related="action_id.state")
    install_type = fields.Selection([('vehicle', 'Car'), ('tank', 'Tank'), ('both', 'Both')], string='Installed on',
                                    related="wheel_id.install_type", )
    show_in_history = fields.Boolean('Show in history', default=False)
    install_date = fields.Date('Install Date', )
    car_meter = fields.Float('Car Meter', )
    # install_place = fields.Many2one('action.place.line', 'Install Place')
    install_place_ = fields.Many2one('install.place', 'Install Place')
    action_id = fields.Many2one('wheel.action', 'Wheel Action')
    car_id = fields.Many2one('new.car', string='Car')
    tank_id = fields.Many2one('new.tank', string='Tank')
    wheel_expense_account_id = fields.Many2one('account.account', "Wheels expenses account")
    wheel_expense_journal_id = fields.Many2one('account.journal', "wheels expenses journal")
    move_id = fields.Many2one('account.move', 'Journal Entry')

    # 
    @api.constrains('car_meter')
    def _check_values(self):
        if not self.car_meter:
            raise ValidationError(_("Car Meter Should not be equal to zero."))

    # @api.one
    @api.constrains('wheel_id')
    def _check_car_wheels(self):
        machine = self.action_id.vehicle_id if self.action_id.vehicle_id.id else self.action_id.tank_id
        if (machine.current_wheel_no or 0) >= (machine.backup_wheel_no + machine.basic_wheel_no):
            raise ValidationError(_("Tou are trying to install number of wheels more than empty wheels"))


class wheel_action_lines_uninstall(models.Model):
    _name = 'wheel.action.lines.uninstall'
    _description = 'register wheel uninstalled on vehicle or tank'

    wheel_id = fields.Many2one('new.wheel', 'Wheel NO.')
    wheel_code = fields.Char('Wheel Code', related="wheel_id.code")
    size = fields.Float('Size', related="wheel_id.size")
    wheel_status = fields.Selection([('draft', 'New'),
                                     ('reviewed', 'Reviewed'),
                                     ('confirmed', 'Confirmed'),
                                     ('used', 'Used'),
                                     ('installed', 'Installed'),
                                     ('damaged', 'Damaged'),
                                     ('sold', 'Sold'),
                                     ('closed', 'Closed')], string='State', related="wheel_id.state")
    install_type = fields.Selection([('vehicle', 'Vehicle'),
                                     ('tank', 'Tank'),
                                     ('both', 'Both')], string='Installed on',
                                    related="wheel_id.install_type", )
    action_status = fields.Selection([('draft', 'New'),
                                      ('reviewed', 'Reviewed'),
                                      ('confirmed', 'Confirmed'),
                                      ('closed', 'Closed')], string='Action State', related="action_id.state")
    install_date = fields.Date('Install Date', )
    car_meter = fields.Float('Car Meter', )
    # install_place = fields.Many2one('action.place.line', 'Install Place')
    install_place_ = fields.Many2one('install.place', 'Install Place')
    select = fields.Boolean('Select')
    uninstall_date = fields.Date('Uninstall Date')
    meter_at_uninstall = fields.Float('Meter When Uninstall')
    distance = fields.Float('Distance')
    wheel_status = fields.Selection([
        ('damaged', 'Damaged'),
        ('used', 'Used'),
    ], string='Wheel Status', default='used')
    action_id = fields.Many2one('wheel.action', 'Wheel Action')
    car_id = fields.Many2one('new.car', string='Car', )
    tank_id = fields.Many2one('new.tank', string='Tank')


    # @api.one
    @api.constrains('meter_at_uninstall')
    def _check_meter_at_uninstall(self):
        if self.meter_at_uninstall < self.car_meter:
            raise ValidationError('Meter For Wheel Can not Be Less Than Car Meter')
        return True

    # 
    @api.depends('meter_at_uninstall', 'car_meter')
    def _compute_distance(self):
        for rec in self:
            rec.distance = rec.meter_at_uninstall - rec.car_meter


class install_place(models.Model):
    _name = 'install.place'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=1)
    code = fields.Char(string='Code')

    # @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = '/'
        return super(install_place, self).copy(default=default)

    # 
    def unlink(self):
        for record in self:
            results_ids = self.env['action.place.line'].search([('action_place_id', '=', record.id)])
            if results_ids:
                raise ValidationError(_('You cannot delete Place has Linked Wheels'))
        return super(install_place, self).unlink()


class account_move(models.Model):
    _inherit = 'account.move'
    _rec_name = 'code'


class wheel_purchase(models.Model):
    _name = 'wheel.purchase'
    _description = 'Purchasing bulk of wheels'
    _inherit = ['mail.thread']

    _rec_name = 'invoice_number'
    _order = "id desc"

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
        self.number_of_wheels = len(self.wheels_ids)

    supplier_id = fields.Many2one('res.partner', string='Supplier')

    supplier_invoice_type = fields.Selection([
        ('no_invoice', 'Do Not Create Invoice'),
        ('invoiced', 'Create Invoice'),
    ], string='Supplier Invoice Type')

    expense_account = fields.Many2one('account.account', string='Warehouse Account')
    expense_journal = fields.Many2one('account.journal', string='Purchase journal')
    estimated_life = fields.Float(string='Estimated Life')
    show_wheels = fields.Boolean(string='Show Wheels')
    wheel_expense_account_id = fields.Many2one('account.account', "Wheels expenses account")
    wheel_expense_journal_id = fields.Many2one('account.journal', "Wheels expenses Journal")
    invoice_id = fields.Many2one('account.account', 'Purchase invoice')
    # invoice
    number_of_wheels = fields.Integer('Number of Wheels')
    location_id = fields.Many2one('stock.location', 'Location')



    state = fields.Selection([('draft', 'New'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed')], string='State', default='draft', track_visibility='onchange')

    # @api.one
    def button_review(self):
        if not self.wheels_ids:
            raise ValidationError('You Must Register at least one line in Wheels')
        self.code = self.env['ir.sequence'].get('wheel.purchase')
        self.write({'state': 'reviewed'})

    # 
    def button_confirmed(self):
        for record in self:
            if record.supplier_invoice_type == 'invoiced':
                name = 'Purchasing Num ' + str(
                    len(record.wheels_ids)) + ' Wheel With Invoice Number' + record.invoice_number,
                invoice_vals = {
                    'partner_id': record.supplier_id and record.supplier_id.id,
                    'type': 'in_invoice',
                    'journal_id': record.expense_journal and record.expense_journal.id,
                    'currency_id': record.expense_journal.currency.id or record.expense_journal.company_id.currency_id.id,
                    'account_id': record.supplier_id.property_account_payable and record.supplier_id.property_account_payable.id,
                    'date_invoice': record.invoice_date,
                    'invoice_line': [(0, _, {'name': name,
                                             'quantity': 1,
                                             'price_unit': record.total,
                                             'account_id': record.expense_account.id})],
                }
                inv_id = self.env['account.account'].create(invoice_vals)
                # invoice
                record.write({'invoice_id': inv_id.id})
            for line in record.wheels_ids:
                vals = {}
                vals.update({
                    'wheel_no': line.wheel_no or '',
                    'manufacturing_company_id': line.manufacturing_company_id.id or False,
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
                    'wheel_expense_account_id': record.wheel_expense_account_id.id or False,
                    'wheel_expense_journal_id': record.wheel_expense_journal_id.id or False,
                    'location_id': record.location_id.id or False,

                })
                self.env['new.wheel'].create(vals)
        self.state = 'confirmed'
        return True

    # @api.one
    def button_closed(self):
        return self.write({'state': 'closed'})

        

class wheel_purchase_line(models.Model):
    _name = 'wheel.purchase.line'

    wheel_no = fields.Char(string='Wheel No.')
    manufacturing_company_id = fields.Many2one('z.manufacture', string='Wheel brand')
    size = fields.Float(string='Size')
    install_type = fields.Selection([
        ('vehicle', 'Vehicle'),
        ('tank', 'Tank'),
        ('both', 'Both'),
    ], string='Wheel Installment Type', )



    wheel_status = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
    ], string='Wheel Status', )

    purchase_price = fields.Float(string='Purchase Price')



    purchase_date = fields.Date(string='Purchase date')
    estimated_life = fields.Float(string='Estimated Life')
    purchase_id = fields.Many2one('wheel.purchase', 'Purchase Number')
