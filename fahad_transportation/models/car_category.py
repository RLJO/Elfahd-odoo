from odoo import models, fields, api, _


class car_category(models.Model):
    _name = 'car.category'
    _description = 'Car Categories'
    _rec_name = 'category_name'

    category_name = fields.Char(string='Category Name')
    code = fields.Char(string='Code')
    tankable = fields.Selection([('yes', 'Yes'),
                                ('no', 'No')], string='Tankable',)

    revenue = fields.Selection([('yes', 'Yes'),
                                ('no', 'No')], string='Car Get Revenue')
    linked_cars = fields.One2many('new.car', 'car_category', 'Linked Cars')

    # @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = '/'
        return super(car_category, self).copy(default=default)

  

    # 
    def unlink(self):
        for record in self:
            if len(record.linked_cars) > 0:
                raise Warning(_('You cannot delete Category that has linked cars'))
        return super(car_category, self).unlink()
