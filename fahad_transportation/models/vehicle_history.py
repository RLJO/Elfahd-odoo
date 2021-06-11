import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class VehicleHistory(models.Model):
    _name = 'vehicle.history'
    _description = 'Vehicle History'
    _rec_name = 'driver_id'

    driver_id = fields.Many2one('hr.employee', string='Driver')
    date = fields.Datetime(string='Date')
    vehicle_id = fields.Many2one('new.vehicle', string='Vehicle')
    car_id = fields.Many2one('new.car', string='Linked Car')
    vehicle_state = fields.Selection([('received', 'Receiver'), ('delivered', 'Deliver')], string='Vehicle State',
                                     default='received')
    car_code = fields.Char(string='Car code')
    line_id = fields.Many2one('new.line', 'Line')
