# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class vehicle_dismantling(models.Model):
    _name = 'vehicle.dismantling'
    _rec_name = 'vehicle_id'
    _inherit = ['mail.thread']

    vehicle_id = fields.Many2one('new.vehicle', 'Vehicle Code')
    new_car_id = fields.Many2one('new.car', _('Car'), related='vehicle_id.new_car_id')
    new_tank_id = fields.Many2one('new.tank', _('Tank'), related='vehicle_id.new_tank_id')
    install_date = fields.Date('Install Date', related='vehicle_id.install_date')
    uninstall_date = fields.Date(string='UnInstall Date')
    decision_no = fields.Char(string='Decision No.')
    cause = fields.Char(string='Cause')
    note = fields.Html(string='Notes')
    state = fields.Selection([('new', _('New')), ('review', _('Reviewed')),
                              ('confirm', _('Confirmed')),
                              ('close', _('Closed'))], _('Status'), default='new', track_visibility='onchange')


    # @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['decision_no'] = '/'
        return super(vehicle_dismantling, self).copy(default=default)


    # @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise Warning(_('You cannot delete confirmed Vehicle'))
        return super(vehicle_dismantling, self).unlink()

    # @api.one
    @api.constrains('install_date', 'uninstall_date')
    def _check_dates(self):
        install_date = datetime.datetime.strptime(self.install_date, '%Y-%m-%d').date()
        uninstall_date = datetime.datetime.strptime(self.uninstall_date, '%Y-%m-%d').date()
        if install_date > uninstall_date:
            raise ValidationError(_("‫‪Sorry‬‬‫‪.‬‬ Uninst‬‬all Date Must be After install Date"))

    # @api.one
    def action_reviewed(self):
        return self.write({'state': 'review'})

    # @api.one
    def action_confirmed(self):
        for record in self:
            vehicle_obj = self.env['new.vehicle'].browse(record.vehicle_id.id)
            vehicle_obj.write({'state_of_dismantling': 'dismantling', 'state': 'close'})
            car_obj = self.env['new.car'].browse(record.vehicle_id.new_car_id.id)
            car_obj.write({'state': 'confirm', 'linked_vehicle': False})
            tank_obj = self.env['new.tank'].browse(record.vehicle_id.new_tank_id.id)
            tank_obj.write({'state': 'confirm', 'linked_vehicle': False})
            record.write({'state': 'confirm'})
        return True

    # @api.one
    def action_closed(self):
        return self.write({'state': 'close'})

