# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from openerp.addons.date_conversion import date_conversion


class hr_eoc(models.Model):
    _name = 'hr.eoc'
    _order = "id desc"

    name = fields.Char(string='Employee name', related='employee_id.name')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    eoc_reward = fields.Selection([('complete', 'Complete'),
                                   ('incomplete', 'Incomplete'),
                                   ('less', 'Less than 3 Month')], 'EOC Reward')
    ### Computed ###
    eoc_days = fields.Float('EOC Days', compute='_compute_eoc', multi=True)
    eoc_consumed_days = fields.Integer('EOC Consumed Days', compute='_compute_eoc', multi=True)
    eoc_calculated = fields.Float('EOC Calculated Days')
    contract_id = fields.Many2one('hr.contract', 'Contract', compute='_compute_eoc', multi=True, )
    ticket_eligibility = fields.Char('Ticket Eligibility', compute='_compute_eoc', multi=True)
    ticket_used = fields.Char('Ticket Used', compute='_compute_eoc', multi=True)
    unpaid_commission = fields.Float('Unpaid Commission', compute='_compute_eoc', multi=True)
    unpaid_deduction = fields.Float('Unpaid Deduction', compute='_compute_eoc', multi=True)
    unpaid_loan = fields.Float('Unpaid Loan', compute='_compute_eoc', multi=True)
    net = fields.Float('Net', compute='_compute_eoc', multi=True)
    ### End of Computed ###
    last_payslip = fields.Date('Last Payslip at', compute='_compute_eoc', multi=True)
    ticket_price = fields.Float('Ticket Price')
    close_contract = fields.Selection([('no', 'No'), ('yes', 'Yes')], 'Close Contract', default='yes')
    liquidity_account_id = fields.Many2one('account.account', 'Liquidity Account')
    expense_account_id = fields.Many2one('account.account', 'Expense Account')
    journal_id = fields.Many2one('account.journal', 'Journal')

    state = fields.Selection([('draft', 'Draft'),
                              ('review', 'Review'),
                              ('confirm', 'Confirm')], 'State', default='draft')
    other_payment_deduction = fields.Float('Other payment / Deduction')
    cause = fields.Char('Cause')
    note = fields.Html('Notes')
    close_employee = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Close Employee', default='yes')
    wage = fields.Float('wage')
    eoc_calculation = fields.Float("Eoc Calculation", compute='_compute_eoc', multi=True, )
    last_working_day = fields.Date('Last working day')
    working_days = fields.Integer('Working Days', compute='_compute_eoc', multi=True)
    contract_start_date = fields.Date('Contract Start date', compute='_compute_eoc', multi=True)
    contract_end_date = fields.Date('Contract End date', compute='_compute_eoc', multi=True)
    contract_duration = fields.Char('Contract duration', compute='get_contract_duration')
    payslip_id = fields.Many2one('hr.payslip', 'Payslip')
    payslip_amount = fields.Float('Payslip amount')
    payslip_id_ = fields.Many2one('hr.payslip', 'Payslip')
    payslip_amount_ = fields.Float('Payslip amount')
    move_id = fields.Many2one('account.move', 'Journal Entry')
    payslip_month = fields.Char("payslip month")

    @api.depends('contract_start_date', 'contract_end_date')
    def get_contract_duration(self):
        d1 = datetime.strptime(self.contract_start_date, "%Y-%m-%d")
        d2 = datetime.strptime(self.contract_end_date, "%Y-%m-%d")
        d = relativedelta(d2, d1)
        self.contract_duration = u"%s سنة , %s شهر , %s يوم" % (d.years, d.months, d.days)

    @api.onchange('payslip_id_')
    def onchange_payslip_id_(self):
        res = 0.0
        if self.payslip_id_:
            res = self.payslip_id_.get_net()
        self.payslip_amount_ = res

    @api.constrains('ticket_price', 'eoc_calculated', 'eoc_days', 'last_working_day')
    def _check_ticket_price(self):
        # if self.ticket_eligibility == 'yes' and self.ticket_used == 'no':
        # if self.ticket_price == 0.0:
        # raise ValidationError(_("Error \n Ticket price cannot be zero(0)"))
        # if self.eoc_calculated > self.eoc_days:
        #     raise ValidationError(_("Error \n EOC calculated cannot be large than EOC days)"))
        pass

    @api.depends('employee_id', 'ticket_price', 'eoc_calculated', 'wage', 'last_working_day', 'state', 'payslip_amount')
    def _compute_eoc(self):
        domain = [('employee_id', '=', self.employee_id.id)]
        if self.state not in ['confirm', ]:
            domain.append(('active', '=', True))
        else:
            domain.append(('active', '=', False))
        contract_obj = self.env['hr.contract'].search(domain, order='date_end')
        for obj in contract_obj:
            self.contract_id = obj.id
            self.wage = obj.wage
            self.contract_start_date = obj.date_start
            self.contract_end_date = obj.date_end
            self.eoc_consumed_days = 0.0  # obj.remaining_eoc_days
            # self.eoc_calculated = obj.eoc_days - obj.remaining_eoc_days
            self.ticket_eligibility = obj.ticket_eligibility
            self.ticket_used = obj.ticket_used
            self.unpaid_commission = obj.commission_diff
            self.unpaid_deduction = obj.deduction_diff
            self.unpaid_loan = obj.loan_diff

            ######## Claculate EOC Days    #############
            if obj.date_start:
                d1 = datetime.strptime(obj.date_start, "%Y-%m-%d")
            if self.last_working_day and obj.date_start:
                d2 = datetime.strptime(self.last_working_day, "%Y-%m-%d")
                total_days = abs((d2 - d1).days)
                self.working_days = total_days
                days_per_year = self.eoc_reward == 'complete' and 36.00 or \
                                self.eoc_reward == 'incomplete' and 21.00 or \
                                self.eoc_reward == 'less' and 0
                self.eoc_days = 0
                if self.eoc_reward != 'less':
                    self.eoc_days = float(days_per_year) * float(total_days) / 365.00
                    self.eoc_calculated = self.eoc_calculated or self.eoc_days
            ######## End of Claculate EOC Days    #############

            self.eoc_calculation = self.eoc_calculated * self.wage / 30
            self.eoc_calculated = self.eoc_calculated or self.eoc_days  # - self.remaining_eoc_days
            self.net = self.eoc_calculation + self.unpaid_commission \
                       - self.unpaid_loan - self.unpaid_deduction + self.other_payment_deduction + (
                           self.ticket_price or 0) + self.payslip_amount
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)])
        for obj in payslip_obj:
            self.last_payslip = obj.date_to

    def create_payslip(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_payroll', 'view_hr_payslip_form')
        view_id = res and res[1] or False
        employee = self.browse(cr, uid, ids[0], context).employee_id
        if not employee.active:
            raise ValidationError(_("Sorry , you can not create a payslip for inactive employee"))
        if not self.pool.get('hr.contract').search(cr, uid, [('employee_id', '=', employee.id), ('active', '=', True)]):
            raise ValidationError(_("the employee did not have an active contact"))
        ctx = {
            'default_employee_id': employee.id,
            'default_date_from': time.strftime("%Y-%m-01"),
            'default_date_to': self.browse(cr, uid, ids[0], context).last_working_day,
            'default_eoc_id': ids[0],
        }
        return {
            'domain': "[]",
            'name': _('Payslip for %s' % (employee.name)),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }

    def button_review(self):
        contract_obj = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('active', '=', True)])
        if not contract_obj:
            raise ValidationError(_("Error \n This employee has not active contract"))
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('active', '=', True),
                                                       ('eoc_boolean', '=', True)])
        if contract_obj:
            raise ValidationError(_("Error \n This employee take EOC Before"))
        self.write({'state': 'review'})

    def button_draft(self):
        self.write({'state': 'draft'})

    def button_confirm(self):
        if self.payslip_id.id and self.payslip_id.state not in [False, 'done']:
            raise ValidationError(_("You can't confirm EOC until you create payslip and confirm it"))
        vals = {}
        line_vals = {}
        eoc_calculation = self.eoc_calculation
        contract_id = self.contract_id.id
        contract_obj = self.env['hr.contract'].browse([contract_id, self.employee_id.contract_id.id])
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']
        vals.update({
            'journal_id': self.journal_id.id,
            'date': time.strftime("%Y-%m-%d"),
            'period_id': account_move._get_period(),
        })
        move = account_move.create(vals)
        self.move_id = move.id
        # self.note = str(self.net)
        total_debit, total_credit = 0.0, 0.0

        def get_rule(code):
            return self.env['hr.salary.rule'].search([['code', '=', code]])

        def create_line(obj, vals):
            if vals['debit'] < 0:
                vals['credit'] = vals['credit'] + abs(vals['debit'])
                vals['debit'] = 0.0
            if vals['credit'] < 0:
                vals['debit'] = vals['debit'] + abs(vals['credit'])
                vals['credit'] = 0.0
            obj.create(vals)

        if move:
            line_vals['move_id'] = move.id
            line_vals['name'] = "EOC for employee: " + self.employee_id.name
            line_vals['period_id'] = account_move._get_period()
            line_vals['debit'] = self.eoc_calculation + self.ticket_price + self.other_payment_deduction
            line_vals['credit'] = 0.0
            line_vals['account_id'] = self.expense_account_id.id
            total_debit += line_vals['debit']
            if line_vals['debit'] != 0:
                create_line(account_move_line, line_vals)

            if self.unpaid_commission:
                line_vals['move_id'] = move.id
                line_vals['name'] = "EOC for employee: " + self.employee_id.name
                line_vals['period_id'] = account_move._get_period()
                line_vals['debit'] = self.unpaid_commission
                total_debit += self.unpaid_commission
                line_vals['credit'] = 0.0
                line_vals['account_id'] = get_rule('COM').account_debit.id
                create_line(account_move_line, line_vals)

            if self.unpaid_deduction:
                line_vals['debit'] = 0.0
                line_vals['credit'] = self.unpaid_deduction
                total_credit += self.unpaid_deduction
                line_vals['account_id'] = get_rule('DED').account_credit.id
                create_line(account_move_line, line_vals)

            if self.unpaid_loan:
                line_vals['debit'] = 0.0
                line_vals['credit'] = self.unpaid_loan
                total_credit += self.unpaid_loan
                line_vals['account_id'] = self.employee_id.loan_account_id.id
                create_line(account_move_line, line_vals)

            if total_debit - total_credit != 0:
                line_vals['debit'] = 0.0
                line_vals['credit'] = total_debit - total_credit
                line_vals['account_id'] = self.liquidity_account_id.id
                create_line(account_move_line, line_vals)

        if self.close_employee == 'yes':
            self.employee_id.write({'active': False})
        contract_obj.write({'ticket_used': 'yes', 'eoc_boolean': True, 'active': False})
        self.write({'state': 'confirm'})

    def unlink(self):
        if self.state == "confirm":
            raise ValidationError(_("You cannot delete confirmed EOC"))
        super(hr_eoc, self).unlink()
