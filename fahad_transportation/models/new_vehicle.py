# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class new_vehicle(models.Model):
    _name = 'new.vehicle'
    _description = "Vehicle"
    _inherit = ['mail.thread']
    _rec_name = 'code'

    code = fields.Char(string='Code')
    install_date = fields.Date(string='Install Date')
    cause = fields.Char(string='Cause')
    decision_no = fields.Char(string='Decision No.')
    ownership = fields.Selection([('private_private', 'Total Private Ownership'),
                                  ('external_external', 'Total External Ownership'),
                                  ('private_external', 'Private Car / External Tank Ownership'),
                                  ('external_private', 'External Car / Private Tank Ownership')], string='OwnerShip')

    new_car_id = fields.Many2one('new.car', _('New Car'))
    car_category_id = fields.Many2one('car.category', _('Car Category'))
    car_plaque_no = fields.Char(string='Plaque No.', related='new_car_id.plaque_no')
    car_aramco_no = fields.Char(string='aramco No.', related='new_car_id.aramco_no')
    car_aramco_expiry_date = fields.Date(string='Aramco Expiry Date', related='new_car_id.sticker_expiry_date')
    car_model = fields.Integer(string='Model', related='new_car_id.model')
    car_color = fields.Char(string='Color', related='new_car_id.color')
    # car_driver = fields.Many2one('car.category', _('Car Category'))
    new_tank_id = fields.Many2one('new.tank', _('Tank Code'))
    tank_chasih_no = fields.Char('Tank Chasih No.', related='new_tank_id.chasih_no')
    capacity = fields.Float(string='Capacity.', related='new_tank_id.capacity')
    tank_aramco_no = fields.Char(string='aramco No.', related='new_tank_id.aramco_no')
    tank_aramco_expiry_date = fields.Date(string='Aramco Expiry Date', related='new_tank_id.aramco_sticker_expiry_date')
    tank_model = fields.Char(string='Model', related='new_tank_id.model')
    tank_company_no = fields.Integer(string='Company No.', related='new_tank_id.company_number')

    state = fields.Selection([('new', _('New')), ('review', _('Reviewed')),
                              ('confirm', _('Confirmed')), ('sold', 'Sold'),
                              ('close', _('Closed'))], _('Status'), default='new', track_visibility='onchange')

    state_of_dismantling = fields.Selection([('connected', _('Connected')), ('dismantling', _('Dismantling'))],
                                            _('Status'))
    line_id = fields.Many2one('new.line', string='Linked Line')
    history_linked_line = fields.One2many('line.vehicle.history', 'vehicle_id', 'History Lines',
                                          domain=[('state_of_linked_line', '=', 'linked')])
    history_linked_all = fields.One2many('line.vehicle.history', 'vehicle_id', 'History Lines')
    state_of_linked_line = fields.Selection([('linked', _('Linked')), ('unlink', _('Unlinked'))],
                                            _('State Of Linked To Line'), default='unlink')
    for_rent = fields.Boolean(_('For Rent'))
    car_is_linked = fields.Boolean('Car is linked')

    # @api.one
    # @api.depends('new_car_id')
    # def _get_car_is_linked(self):
    #     if self.new_car_id.driver_id.id:
    #         self.car_is_linked = True
    #     else:
    #         self.car_is_linked = False

    # @api.one
    # @api.depends('history_linked_line')
    # def _compute_is_for_rent(self):
    #     if len(self.history_linked_line) == 0:
    #         self.for_rent = True
    #     else:
    #         self.for_rent = False

    has_driver = fields.Boolean(string='Has Driver', default=False)
    car_driver = fields.Many2one('hr.employee', _('Car Driver'))

    # driver_history = fields.One2many('custody.receive.line', 'vehicle_id', 'Driver History')

    # @api.one
    # @api.depends('new_car_id', 'new_tank_id')
    # def _compute_vehicle_code(self):
    #     if self.new_car_id and self.new_tank_id:
    #         self.code = self.new_car_id.code + '' + self.new_tank_id.code

    # @api.one
    # @api.depends('new_car_id', 'new_tank_id')
    # def _compute_vehicle_ownership(self):
    #     if self.new_car_id and self.new_tank_id:
    #         self.ownership = self.new_car_id.ownership + '_' + self.new_tank_id.ownership

    # @api.one
    @api.constrains('new_car_id', 'new_tank_id', )
    def _check_digits(self):
        if not self.new_car_id:
            raise ValidationError(_("You cannot save without enter car"))
        if not self.new_tank_id:
            raise ValidationError(_("You cannot save without enter tank"))



    # @api.one
    # def copy(self, default=None):
    #     if default is None:
    #         default = {}
    #     default['decision_no'] = '/'
    #     return super(new_vehicle, self).copy(default=default)


    # # @api.model
    # def write(self, vals):
    #     if vals.has_key('new_car_id') and self.env['new.car'].browse(vals['new_car_id.id']).for_wheel_action:
    #         raise ValidationError(_("The car which you selected must not have empty wheel places"))
    #     if vals.has_key('new_tank_id') and self.env['new.car'].browse(vals['new_tank_id.id']).for_wheel_action:
    #         raise ValidationError(_("The tank which you selected must not have empty wheel places"))
    #     return super(new_vehicle, self).write(vals)



    # # @api.multi
    # def unlink(self):
    #     for record in self:
    #         if record.state == 'confirm':
    #             raise ValidationError(_('You cannot delete confirmed wheel'))
    #     return super(new_vehicle, self).unlink()

    # @api.one
    def action_reviewed(self):
        return self.write({'state': 'review'})

    # @api.one
    def action_confirmed(self):
        for record in self:
            if self.new_car_id.state != 'confirm':
                raise ValidationError(_("Car states must be confirmed"))
            if self.new_tank_id.state != 'confirm':
                raise ValidationError(_("Tank states must be confirmed"))
            if self.new_car_id.for_wheel_action:
                raise ValidationError(_("Can not confirm this car because it have wheel(s) free"))
            if self.new_tank_id.for_wheel_action:
                raise ValidationError(_("Can not confirm this tank because it have wheel(s) free"))
            car_obj = self.env['new.car'].browse(record.new_car_id.id)
            car_obj.write({'state': 'connect', 'linked_vehicle': record.id})
            tank_obj = self.env['new.tank'].browse(record.new_tank_id.id)
            tank_obj.write({'state': 'connect', 'linked_vehicle': record.id})
            record.write({'state': 'confirm', 'state_of_dismantling': 'connected'})
        return True

    # @api.one
    def action_closed(self):
        return self.write({'state': 'close'})

    # @api.multi
    # @api.depends('tank_aramco_no')
    # def name_get(self):
    #     result = []
    #     for vehicle in self:
    #         result.append((vehicle.id, '%s' % (vehicle.tank_aramco_no)))
    #     return result

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     recs = self.browse()
    #     domain = []
    #     if name:
    #         domain = [('tank_aramco_no', '=', name)]
    #     if not recs:
    #         domain = [('tank_aramco_no', operator, name)]
    #     if self._context.get('connected_tanks_only', False):
    #         domain = ['state_of_dismantling', '=', 'connected']
    #     recs = self.search(domain + args, limit=limit)
    #     return recs.name_get()
