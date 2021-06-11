# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class vehicles_on_line(models.Model):
    _name = "vehicles.on.line"
    _rec_name = 'code'
    _inherit = ['mail.thread']

    # TODO Following Fields code, decision_no, assemble_date, related_vehicle_no, plaque_no, model, mark, related_driver, related_tank_no, company_no, decision_type
    new_line_id = fields.Many2one('new.line', _("New Line"))
    new_line_history_id = fields.Many2one('new.line', _("New Line History"))
    code = fields.Char(string='Code')
    decision_date = fields.Date(string='Decision Date')
    decision_type = fields.Selection([('install', _('Install')), ('uninstall', _('Uninstall'))], _('Decision Type'))
    unconnected_vehicles_ids = fields.One2many('linked.unlinked.vehicles', 'line_id_for_unlink',
                                               string='Unconnected Vehicle')
    connected_vehicles_ids = fields.One2many('linked.unlinked.vehicles', 'line_id_for_link', string='Connected Vehicle')
    state = fields.Selection([('new', _('New')),
                              ('review', _('Reviewed')),
                              ('confirm', _('Confirmed')),
                              ('close', _('Closed'))], 'State', track_visibility='onchange', default='new')

    # @api.one
    @api.constrains('unconnected_vehicles_ids', 'connected_vehicles_ids')
    def _check_lines(self):
        if len(self.unconnected_vehicles_ids) == 0 and len(self.connected_vehicles_ids) == 0:
            raise ValidationError(_('You should have at least a line'))

    # @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = '/'
        return super(vehicles_on_line, self).copy(default=default)


    # @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise ValidationError(_('You cannot delete confirmed Decision'))
        return super(vehicles_on_line, self).unlink()

    # @api.one
    def action_reviewed(self):
        self.code = self.env['ir.sequence'].next_by_code('vehicles.on.line')
        return self.write({'state': 'review'})

    # @api.one
    def action_confirmed(self):
        for record in self:
            if record.decision_type == 'install':
                for line in record.unconnected_vehicles_ids:
                    vals = {}
                    if line.state_of_linked_line == 'linked':
                        vehicle_obj = self.env['new.vehicle'].browse(line.vehicle_id.id)
                        vehicle_obj.write({'line_id': record.new_line_id.id,
                                           'state_of_linked_line': 'linked'})
                        linked_obj = self.env['linked.unlinked.vehicles'].browse(line.id)
                        linked_obj.write({'new_line_id': record.new_line_id.id,
                                          'new_car_id': line.vehicle_id.new_car_id.id,
                                          'new_tank_id': line.vehicle_id.new_tank_id.id,
                                          'link_date': fields.Date.context_today(self)
                                          })
                        vals.update({
                            'new_line_id': record.new_line_id.id or False,
                            'new_car_id': line.vehicle_id.new_car_id.id or False,
                            'new_tank_id': line.vehicle_id.new_tank_id.id or False,
                            'vehicle_id': line.vehicle_id.id or False,
                            'code': record.new_line_id.code or '',
                            'route_no': record.new_line_id.route_no or '',
                            'route_number': record.new_line_id.route_number or '',
                            'line_name': record.new_line_id.line_name or '',
                            'start_point': record.new_line_id.start_point or '',
                            'end_point': record.new_line_id.end_point or '',
                            'distance': record.new_line_id.distance or 0.0,
                            'km_price': record.new_line_id.km_price or 0.0,
                            'line_price': record.new_line_id.line_price or 0.0,
                            'allowance': record.new_line_id.allowance or 0.0,
                            'state_of_linked_line': 'linked'})
                        self.env['line.vehicle.history'].create(vals)
                        car_obj = self.env['new.car'].browse(line.vehicle_id.new_car_id.id)
                        car_obj.write({'state_of_linked_line': 'linked', 'linked_line': record.new_line_id.id})
                        tank_obj = self.env['new.tank'].browse(line.vehicle_id.new_tank_id.id)
                        tank_obj.write({'state_of_linked_line': 'linked', 'linked_line': record.new_line_id.id})

            elif self.decision_type == 'uninstall':
                for line in record.connected_vehicles_ids:
                    vals = {}
                    if line.state_of_linked_line == 'unlink':
                        vehicle_obj = self.env['new.vehicle'].browse(line.vehicle_id.id)
                        vehicle_obj.write({'line_id': False, 'state_of_linked_line': 'unlink'})
                        linked_vehicle = self.env['linked.unlinked.vehicles'].browse(line.id)
                        linked_vehicle.write({'new_line_id': record.new_line_id.id,
                                              'new_car_id': line.vehicle_id.new_car_id.id,
                                              'new_tank_id': line.vehicle_id.new_tank_id.id,
                                              'unlink_date': fields.Date.context_today(self),
                                              })
                        vals.update({
                            'vehicle_id': line.vehicle_id.id or False,
                            'new_line_id': record.new_line_id.id or False,
                            'new_car_id': line.vehicle_id.new_car_id.id or False,
                            'new_tank_id': line.vehicle_id.new_tank_id.id or False,
                            'code': record.new_line_id.code or '',
                            'route_no': record.new_line_id.route_no or '',
                            'route_number': record.new_line_id.route_number or '',
                            'line_name': record.new_line_id.line_name or '',
                            'start_point': record.new_line_id.start_point or '',
                            'end_point': record.new_line_id.end_point or '',
                            'distance': record.new_line_id.distance or 0.0,
                            'km_price': record.new_line_id.km_price or 0.0,
                            'line_price': record.new_line_id.line_price or 0.0,
                            'allowance': record.new_line_id.allowance or 0.0,
                            'state_of_linked_line': 'unlink'

                        })
                        results_ids = self.env['line.vehicle.history'].search(
                            [('vehicle_id', '=', line.vehicle_id.id), ('new_line_id', '=', record.new_line_id.id),
                             ('state_of_linked_line', '=', 'linked')])
                        results_ids.unlink()
                        self.env['line.vehicle.history'].create(vals)
                        car_obj = self.env['new.car'].browse(line.vehicle_id.new_car_id.id)
                        car_obj.write({'state_of_linked_line': 'unlink', 'linked_line': False})
                        tank_obj = self.env['new.tank'].browse(line.vehicle_id.new_tank_id.id)
                        tank_obj.write({'state_of_linked_line': 'unlink', 'linked_line': False})
            record.write({'state': 'confirm'})

        return True

    # @api.one
    def action_closed(self):
        return self.write({'state': 'close'})

  


class new_line(models.Model):
    _name = 'new.line'
    _rec_name = 'line_name'
    _inherit = ['mail.thread']


    # TODO allowance get from trip screen, trip_ids from trip, all_vehicles_lines, tank_no
    code = fields.Char(_('Code'))
    route_no = fields.Char(_('Route number'))
    route_number = fields.Char(_('Route No'), size=12)
    line_name = fields.Char(_('Line Name'), size=30)
    start_point = fields.Many2one('z.cities', _('Start Point'))
    end_point = fields.Many2one('z.cities', _('End Point'))
    distance = fields.Float(_('Distance'))
    km_price = fields.Float(_('KM Price'), digits=(30,20))
    line_price = fields.Float(_('Line Price'), size=8, digits=(30,20))  # , compute = '_compute_line_price'
    allowance = fields.Float(_('Allowance'))
    driver_commission = fields.Float(_('Driver Commission'))
    loss_liter = fields.Float(_('Loss per each Liter'))
    income_account = fields.Many2one('account.account', _("Income Account"))
    loss_account = fields.Many2one('account.account', _("Loss Account"))
    journal = fields.Many2one('account.journal', _('Journal'))
    product_ids = fields.One2many('product.template', 'new_line_id', _('Products'))
    trip_ids = fields.One2many('trips.line', 'line_id', _('Trips'), domain=[('state', '=', 'complete')])
    all_vehicles_lines = fields.One2many('linked.unlinked.vehicles', 'new_line_id', _('History Vehicles'))
    branch_id = fields.Many2one('branch', 'Branch')
    vehicles_lines = fields.One2many('linked.unlinked.vehicles', 'new_line_id', _('Current Vehicles'))
    aramco_line_ids = fields.One2many('lines.aramco.cars', 'line_id', 'Aramco Cars')
    state = fields.Selection([('new', _('New')),
                              ('review', _('Reviewed')),
                              ('confirm', _('Confirmed')),
                              ('close', _('Closed'))], 'State', default='new', track_visibility='onchange')
    has_vehicle = fields.Selection([('yes', 'Has Vehicle'), ('no', 'Not Has Vehicle')], string='Has Vehicle?',
                                   default='no')
    connected_vehicles = fields.One2many('new.vehicle', 'line_id', 'Connected Vehicles')
    plaque_no = fields.Many2one('new.car', 'Plaque No')


    # @api.one
    def button_review(self):
        # if len(self.product_ids) < 1:
        #     raise ValidationError(_('You should have at least a product'))
        self.code = self.env['ir.sequence'].get('new.line')
        self.write({'state': 'review'})

    # @api.one
    def button_confirm(self):
        #if len(self.product_ids) < 1:
        #    raise ValidationError(_('You should have at least a product'))
        return self.write({'state': 'confirm'})

    # @api.one
    def button_close(self):
        return self.write({'state': 'close'})

    # @api.one
    @api.constrains('distance', 'km_price', 'driver_commission')
    def _check_digit_and_value(self):
        if self.driver_commission == 0:
            raise ValidationError(_("Driver Commission Should be greater than Zero"))
        if self.distance == 0.00:
            raise ValidationError(_("Distance should be greater than zero."))
        if len(str(int(self.distance))) > 5:
            raise ValidationError(_("Distance should be 5 digits only"))
        if self.km_price == 0.00:
            raise ValidationError(_("KM Price should be greater than zero."))
        if len(str(int(self.km_price))) > 5:
            raise ValidationError(_("KM Price should be 5 digits only"))



    # @api.one
    @api.constrains('allowance')
    def _check_allowance(self):
        if self.allowance > 2:
            raise ValidationError(_("Allowance should be less than 2"))



    # @api.multi
    def unlink(self):
        if self.state == 'close':
            raise ValidationError(_('New Line Can not be deleted when state is closed.'))
        if self.state == 'confirm' or self.trip_ids:
            raise ValidationError(_('New Line Can not be deleted when state is Confirmed and has trips on it.'))
        if self.state == 'confirm':
            raise ValidationError(_('New Line Can not be deleted when state is Confirmed'))
        return super(new_line, self).unlink()


class lines_aramco_cars(models.Model):
    _name = "lines.aramco.cars"

    line_id = fields.Many2one('new.line', 'Line')
    plaque_no = fields.Many2one('new.car', 'Plaque No')
    model = fields.Integer('Model', related='plaque_no.model')
    color = fields.Char('Color', related='plaque_no.color')
    chasih_no = fields.Char('Chasih No', related='plaque_no.chasih_no')
    aramco_no = fields.Char('Aramco No', related='plaque_no.aramco_no')
    aramco_date = fields.Date('Aramco Date', related='plaque_no.aramco_date')
    aramco_expiry_date = fields.Date('Aramco Expiry Date', related='plaque_no.sticker_expiry_date')
    tank_no = fields.Many2one('new.tank', 'Tank No')
    aramco_sticker_expiry_date = fields.Date('Expiry Date', related='tank_no.aramco_sticker_expiry_date')
    company_number = fields.Integer('Company Number', related='tank_no.company_number')


class z_cities(models.Model):
    _name = "z.cities"
    name = fields.Char('Name')
    e_name = fields.Char('English name')
    note = fields.Html('Notes')


class z_manufacture(models.Model):
    _name = "z.manufacture"
    name = fields.Char('Name')
    e_name = fields.Char('English name')
    code = fields.Char('code')
    note = fields.Html('Notes')
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Code No must be unique.'),
        ('name_unique', 'unique(name)', 'Name No must be unique.'),
    ]


class product_template(models.Model):
    _inherit = 'product.template'
    new_line_id = fields.Many2one('new.line', _("New Line"))
    is_aramco = fields.Boolean('Aramco product')


class linked_unlinked_vehicles(models.Model):
    _name = 'linked.unlinked.vehicles'

    vehicle_id = fields.Many2one('new.vehicle', string='Vehicle Id')
    code = fields.Char(string='Code')
    decision_no = fields.Char(string='Decision No.')
    install_date = fields.Date(string='Install Date')
    car_code = fields.Char(string='Car Code')
    plaque_no = fields.Char(string='Plaque No.')
    model = fields.Char(string='Car Model')
    mark = fields.Char(string='Car Mark')
    driver = fields.Many2one('hr.employee', string='Driver')
    tank_code = fields.Char(string='Tank Code')
    tank_capacity = fields.Float(string='Tank Capacity')
    tank_company_no = fields.Integer(string='Tank Company No.')
    state_of_linked_line = fields.Selection([('linked', _('Link')), ('unlink', _('Unlink'))], _('Linked/UnLinked'))
    new_line_id = fields.Many2one('new.line', 'New Line')
    line_id_for_link = fields.Many2one('vehicles.on.line', string='Line')
    line_id_for_unlink = fields.Many2one('vehicles.on.line', string='Line')
    new_car_id = fields.Many2one('new.car', 'New Car')
    new_tank_id = fields.Many2one('new.tank', 'New Tank')


class line_vehicle_history(models.Model):
    _name = 'line.vehicle.history'

    vehicle_id = fields.Many2one('new.vehicle', string='Vehicle Id')
    new_car_id = fields.Many2one('new.car', string='Car Id')
    new_tank_id = fields.Many2one('new.tank', string='Tank Id')
    code = fields.Char(_('Code'))
    route_no = fields.Char(_('Route number'))
    route_number = fields.Char(_('Route No'), size=12)
    line_name = fields.Char(_('Line Name'), size=30)
    start_point = fields.Char(_('Start Point'), size=15)
    end_point = fields.Char(_('End Point'), size=15)
    distance = fields.Float(_('Distance'))
    km_price = fields.Float(_('KM Price'))
    line_price = fields.Float(_('Line Price'))
    allowance = fields.Float(_('Allowance'))
    state_of_linked_line = fields.Selection([('linked', _('Linked')), ('unlink', _('Unlinked'))], _('Linked/UnLinked'))
    new_line_id = fields.Many2one('new.line', 'New Line')
