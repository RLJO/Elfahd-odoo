# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import datetime
from openerp.addons.date_conversion import date_conversion


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    _order = "id desc"

    unpaid_commission = fields.Float('Unpaid Commission', compute='_compute_extra', multi='payslip')
    unpaid_deduction = fields.Float('Unpaid Deduction', compute='_compute_extra', multi='payslip')
    unpaid_loan = fields.Float('Unpaid Loan', compute='_compute_extra', multi='payslip')
    unpaid_commission_ = fields.Float('Unpaid Commission', )
    unpaid_deduction_ = fields.Float('Unpaid Deduction', )
    unpaid_loan_ = fields.Float('Unpaid Loan', )
    paid_commission = fields.Float('Paid Commission')
    paid_deduction = fields.Float('Paid Deduction')
    paid_loan = fields.Float('Paid Loan')
    review = fields.Boolean('Review')
    eoc_id = fields.Many2one('hr.eoc', 'EOC')

    @api.depends('employee_id')
    def _compute_extra(self):
        contract_obj = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('active', '=', True)])
        for obj in contract_obj:
            self.unpaid_commission = obj.commission_diff
            self.unpaid_deduction = obj.deduction_diff
            self.unpaid_loan = obj.loan_diff

    def hr_verify_sheet(self):
        if not self.review:
            raise ValidationError(_("You have to review extra payment information"))
        if self.unpaid_commission < self.paid_commission:
            raise ValidationError(_("Paid Commission cannot be greater than Unpaid Commission"))
        if self.unpaid_deduction < self.paid_deduction:
            raise ValidationError(_("Paid Deduction cannot be greater than Unpaid Deduction"))
        if self.unpaid_loan < self.paid_loan:
            raise ValidationError(_("Paid Loan cannot be greater than Unpaid Loan"))
        self.write({
            'unpaid_commission_': self.unpaid_commission,
            'unpaid_deduction_': self.unpaid_deduction,
            'unpaid_loan_': self.unpaid_loan
        })
        total_com = self.paid_commission
        total_ded = self.paid_deduction
        total_loan = self.paid_loan
        # for line in self.details_by_salary_rule_category:
        #     if line.salary_rule_id.code == 'COM':
        #         total_com = line.total
        #     elif line.salary_rule_id.code == 'DED':
        #         total_ded = line.total
        #     elif line.salary_rule_id.code == 'LOAN':
        #         total_loan = line.total
        if self.paid_commission:
            dict = {
                'date': self.date_to,
                'amount': total_com,
                'note': "Commission from Payslip",
                'contract_id': self.contract_id.id,
            }
            self.env['commission.paid.line'].create(dict)
        if self.paid_deduction:
            dict = {
                'date': self.date_to,
                'amount': abs(total_ded),
                'note': "Deduction from Payslip",
                'contract_id': self.contract_id.id,
            }
            self.env['deduction.paid.line'].create(dict)
        if self.paid_loan:
            dict = {
                'date': self.date_to,
                'amount': abs(total_loan),
                'note': "Loan from Payslip",
                'contract_id': self.contract_id.id,
            }
            self.env['loan.paid.line'].create(dict)
        return super(hr_payslip, self).hr_verify_sheet()

    @api.model
    def create(self, vals):
        res = super(hr_payslip, self).create(vals)
        if vals.has_key('eoc_id'):
            self.env['hr.eoc'].browse(vals['eoc_id']).write({
                'payslip_id': res.id,
                'payslip_amount': self.get_net()
            })
        return res

    def write(self, vals):
        res = super(hr_payslip, self).write(vals)
        if vals.has_key('line_ids') and self.eoc_id.id:
            self.eoc_id.payslip_amount = self.get_net()
        return res

    def get_net(self):
        return sum([l.amount for l in self.line_ids if l.salary_rule_id.code == 'FAHAD_NET'])

    @api.constrains('contract_id')
    def check_contract(self):
        if not  self.contract_id.id:
            raise ValidationError(_("Please review contract start date & end date in order to create paysip"))
