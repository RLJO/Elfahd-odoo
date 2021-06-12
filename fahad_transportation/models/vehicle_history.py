import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class VehicleHistory(models.Model):
    _name = 'vehicle.history'
    _description = 'Vehicle History'
    _inherit = ['mail.thread']
    _rec_name = 'driver_id'

    driver_id = fields.Many2one('hr.employee', string='Driver', track_visibility='onchange')
    date = fields.Datetime(string='Date')
    vehicle_id = fields.Many2one('new.vehicle', string='Vehicle', track_visibility='onchange')
    car_id = fields.Many2one('new.car', string='Linked Car')
    vehicle_state = fields.Selection([('received', 'Receiver'), ('delivered', 'Deliver')], string='Vehicle State',
                                     default='received', track_visibility='onchange')
    car_code = fields.Char(string='Car code')
    line_id = fields.Many2one('new.line', 'Line')
