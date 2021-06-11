from odoo import models, fields, api, _


class branch(models.Model):
    _name = 'branch'
    _description = 'Branches'

    rec_name = 'name'

    code = fields.Char(string='Branch Code')
    name = fields.Char(string='Branch Name')
    city = fields.Char(string='city')
    district = fields.Char(string='District')
    community = fields.Char(string='Community')
    street = fields.Char(string='Street')
    building_name = fields.Char(string='Building Name')
    building_no = fields.Integer(string='Building No.')
    floor_no = fields.Integer(string='Floor No.')
    telephone_no = fields.Char(string='Tel. No.')
    mobile1 = fields.Char(string='Mobile 1 No.')
    mobile2 = fields.Char(string='Mobile 2 No.')
    mobile3 = fields.Char(string='Mobile 3 No.')
    email = fields.Char(string='E-Mail')
    branch_manager = fields.Char(string='Branch Manager')
    city_id=fields.Many2one('z.cities',string='City')
    employee_ids = fields.One2many('hr.employee', 'branch_name', string='Employees', )
    # employee_branch_ids = fields.Many2many('hr.employee', 'branch_on_employees', 'branch_id', 'line_id',string='Employees on Branch',)
    line_ids = fields.One2many('new.line', 'branch_id', string='Lines', domain=[('state', '=', 'confirm')])

    cars_ids = fields.One2many('new.car', 'branch_id', string='Cars', domain=[('state', 'in', ['confirm', 'rented'])])

    tanks_ids = fields.One2many('new.tank', 'branch_id', string='Tanks',
                                domain=[('state', 'in', ['confirm', 'rented'])])


    # @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = '/'
        return super(branch, self).copy(default=default)

    # # @api.model
    # def create(self, vals):
    #     if vals.get('code', '/') == '/':
    #         vals['code'] = self.env['ir.sequence'].next_by_code(
    #             'branch') or '/'
    #     return super(branch, self).create(vals)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    line_id = fields.Many2one('branch', string='Branch')
    branch_id = fields.Many2one('branch', string='Branch')
