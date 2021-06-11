from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import time

from odoo.osv import expression
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo.addons.date_conversion import date_conversion

class new_vehicle(models.Model):
    _name = 'new.vehicle'
    _inherit = ['mail.thread']


class new_line(models.Model):
    _name = 'new.line'


class commission_line(models.Model):
    _name = 'commission.line'

    date = fields.Date('Date')
    line_id = fields.Many2one('new.line', 'Line')
    trip_code = fields.Char('Code')
    vehicle_id = fields.Many2one('new.vehicle', 'Vehicle')
    amount = fields.Float('Amount')
    note = fields.Char('Notes')
    contract_id = fields.Many2one('hr.contract', 'Contract')


class commission_paid_line(models.Model):
    _name = 'commission.paid.line'

    date = fields.Date('Date')
    amount = fields.Float('Amount')
    note = fields.Char('Notes')
    contract_id = fields.Many2one('hr.contract', 'Contract')


class deduction_line(models.Model):
    _name = 'deduction.line'

    date = fields.Date('Date')
    amount = fields.Float('Amount')
    cause = fields.Char('Cause')
    document = fields.Char('Document')
    note = fields.Char('Notes')
    contract_id = fields.Many2one('hr.contract', 'Contract')


class deduction_paid_line(models.Model):
    _name = 'deduction.paid.line'

    date = fields.Date('Date')
    amount = fields.Float('Amount')
    note = fields.Char('Notes')
    contract_id = fields.Many2one('hr.contract', 'Contract')


class loan_line(models.Model):
    _name = 'loan.line'

    date = fields.Date('Date')
    amount = fields.Float('Amount')
    cause = fields.Char('Cause')
    note = fields.Char('Notes')
    contract_id = fields.Many2one('hr.contract', 'Contract')


class loan_paid_line(models.Model):
    _name = 'loan.paid.line'

    date = fields.Date('Date')
    amount = fields.Float('Amount')
    note = fields.Char('Notes')
    contract_id = fields.Many2one('hr.contract', 'Contract')


class leave_line(models.Model):
    _name = 'leave.line'

    date_to = fields.Date('Leave Beginning')
    date_from = fields.Date('Leave End')
    leave_balance = fields.Integer('Leave Balance', compute="_compute_leave_balance")
    note = fields.Char('Notes')
    contract_id = fields.Many2one('hr.contract', 'Contract')

    @api.depends('date_to', 'date_from')
    def _compute_leave_balance(self):
        if self.date_from and self.date_to:
            date_to = datetime.strptime(self.date_to, '%Y-%m-%d').date()
            date_from = datetime.strptime(self.date_from, '%Y-%m-%d').date()
            if date_to > date_from:
                raise ValidationError(_("leave beginning must be lease than leave end"))
            self.leave_balance = (date_from - date_to).days + 1


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    active = fields.Boolean('Active', default=True)
    commission_line = fields.One2many('commission.line', 'contract_id', 'Commission')
    commission_paid_line = fields.One2many('commission.paid.line', 'contract_id', 'Paid Commission')
    deduction_line = fields.One2many('deduction.line', 'contract_id', 'Deduction')
    deduction_paid_line = fields.One2many('deduction.paid.line', 'contract_id', 'Paid Deduction')
    loan_line = fields.One2many('loan.line', 'contract_id', 'Loan')
    loan_paid_line = fields.One2many('loan.paid.line', 'contract_id', 'Paid Loan')
    ticket_eligibility = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Ticket Eligibility', default='yes')
    ticket_used = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Ticket Used', default='no')
    commission_diff = fields.Char(_('Commission Diff'), compute='_compute_commission_diff')
    deduction_diff = fields.Char(_('Deduction Diff'), compute='_compute_deduction_diff')
    loan_diff = fields.Char(_('Loan Diff'), compute='_compute_loan_diff')
    eoc = fields.Boolean('EOC', readonly=1)
    leave_line = fields.One2many('leave.line', 'contract_id', 'Leaves')
    eoc_days = fields.Integer('EOC Days')
    remaining_eoc_days = fields.Integer('Remaining EOC Days', compute='_compute_remaining_eoc_days')
    eoc_boolean = fields.Boolean('EOC', readonly=1)
    # employee_code = fields.related('employee_id', 'code', type='integer', string="Employee code")

    def _get_salary_structure(self):
        return 3

    _defaults = {
        'struct_id': lambda s, cr, uid, c:
        s.pool.get('hr.payroll.structure').search(cr, uid, [('name', '=', 'Fahad Salary Scale')], context=c)[0],
    }
    # 'date_from': lambda *a: time.strftime('%Y-%m-01'),
    # 'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1,))[:10],

    @api.constrains('commission_line', 'deduction_line', 'loan_line', 'leave_line')
    def _check_lines(self):
        if self.commission_line:
            for record in self.commission_line:
                if record.amount == 0.0:
                    raise ValidationError(_("Error \n Amount cannot be Zero in Commission"))
        if self.deduction_line:
            for record in self.deduction_line:
                if record.amount == 0.0:
                    raise ValidationError(_("Error \n Amount cannot be Zero in Deduction"))
        if self.loan_line:
            for record in self.loan_line:
                if record.amount == 0.0:
                    raise ValidationError(_("Error \n Amount cannot be Zero on Loan"))
        if self.leave_line:
            leave_balance = 0.0
            for record in self.leave_line:
                date_to = datetime.datetime.strptime(record.date_to, '%Y-%m-%d').date()
                date_from = datetime.datetime.strptime(record.date_from, '%Y-%m-%d').date()
                leave_balance += record.leave_balance
                if record.date_to < self.date_start or record.date_to > self.date_end:
                    raise ValidationError(_("Error \n Leave beginning must be within contract duration"))
                if record.date_from < self.date_start or record.date_to > self.date_end:
                    raise ValidationError(_("Error \n Leave end must be within contract duration"))
                if date_to > date_from:
                    raise ValidationError(_("Error \n Leave beginning must be less than leave end"))
            if leave_balance > self.eoc_days:
                raise ValidationError(_("Error \n Leave balance must be less than EOC Days"))


    @api.constrains('wage')
    def _check_wage(self):
        if self.wage==0:
            raise ValidationError(_("Wage can not be zero"))


    @api.depends('leave_line', 'eoc_days')
    def _compute_remaining_eoc_days(self):
        total = self.eoc_days
        total_leave = 0.0
        for com in self.leave_line:
            total_leave += com.leave_balance
        if total_leave > total:
            raise ValidationError(
                _("Error \n Total Leave days %d is large that total eoc days %d") % (total_leave, total))
        self.remaining_eoc_days = total - total_leave

    @api.depends('commission_line', 'commission_paid_line')
    def _compute_commission_diff(self):
        total = 0.0
        total_paid = 0.0
        for com in self.commission_line:
            total += com.amount
        for p_com in self.commission_paid_line:
            total_paid += p_com.amount
        if total_paid > total:
            raise ValidationError(_("Error \n Total Paid %d is large that total commission %d") % (total_paid, total))
        self.commission_diff = total - total_paid

    @api.depends('active')
    def _double_active_contract(self):
        if self.active:
            if self.search([('active', '=', True), ('employee_id', '=', self.employee_id.id), ('id', '!=', self.id)]):
                raise ValidationError(_("Error \n Total Paid %d is large that total deduction %d"))

    @api.depends('deduction_line', 'deduction_paid_line')
    def _compute_deduction_diff(self):
        total = 0.0
        total_paid = 0.0
        for com in self.deduction_line:
            total += com.amount
        for p_com in self.deduction_paid_line:
            total_paid += p_com.amount
        if total_paid > total:
            pass
            #raise ValidationError(_("Error \n Total Paid %d is large that total deduction %d") % (total_paid, total))
        self.deduction_diff = total - total_paid

    @api.depends('loan_line', 'loan_paid_line')
    def _compute_loan_diff(self):
        total = 0.0
        total_paid = 0.0
        for com in self.loan_line:
            total += com.amount
        for p_com in self.loan_paid_line:
            total_paid += p_com.amount
        if total_paid > total:
            raise ValidationError(_("Error \n Total Paid %d is large that total loan %d") % (total_paid, total))
        self.loan_diff = total - total_paid

    @api.model
    def create(self, vals):
        emp_id = vals['employee_id']
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', emp_id)])
        for obj in contract_obj:
            if obj.active:
                raise ValidationError(_('You cannot create active contract for this employee \n He have one!'))
        return super(hr_contract, self).create(vals)

    def write(self, vals):
        if 'active' in vals.keys() and vals['active'] and self.search(
                [('active', '=', True), ('employee_id', '=', self.employee_id.id)]):
            raise ValidationError(_("You cannot create active contract for this employee. He has active one"))
        super(hr_contract, self).write(vals)
    def unlink(self):
        for record in self:
            if record.commission_line or record.deduction_line or record.loan_line:
                raise ValidationError(_(
                    'You cannot delete this contract because there are value in this fields \n\"Commission diff , deduction diff ,Loan diff\"'))
        return super(hr_contract, self).unlink()


class hr_payslip_(models.Model):
    _inherit = "hr.payslip"

    month = fields.Selection([('1', _('January')), ('2', _('February')), ('3', _('March')),
                              ('4', _('April')), ('5', _('May')), ('6', _('June')),
                              ('7', _('July')), ('8', _('August')), ('9', _('September')),
                              ('10', _('October')), ('11', _('November')), ('12', _('December'))], _('Month'))

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            month = str(self.month) if len(str(self.month)) == 2 else '0' + str(self.month)
            self.date_from = time.strftime('%Y-' + month + '-01')
            selected_month = int(self.month)
            now_month = int(time.strftime('%m'))
            diff = now_month - selected_month
            self.date_to = str(datetime.now() + relativedelta.relativedelta(months=+1 - diff, day=1, days=-1, ))[:10]
