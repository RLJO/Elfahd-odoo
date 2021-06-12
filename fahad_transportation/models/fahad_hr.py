# -*- coding: utf-8 -*-
#  from date_conversion.date_conversion import Hijri2Gregorian, reset_hijri_format
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from odoo.addons.date_conversion import date_conversion


# from date_conversion import *


class dependence_line(models.Model):
    _name = 'dependence.line'

    name = fields.Char('Name', required=1)
    kinship = fields.Selection([
        ('husband', 'Husband'),
        ('wife', 'Wife'),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('other', 'Other')], 'Kinship', required=1)
    iqama_no = fields.Integer('Iqama No')
    passport_no = fields.Char('Passport No')
    birthday = fields.Date('Birth Day')
    note = fields.Char('Note')
    employee_id = fields.Many2one('hr.employee', 'ID')


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    ###################################################################
    def _return_validation_of_hijri_date(self, field, field_name):
        if field:
            if len(field) != 10:
                raise ValidationError(_(" %s Should be 10 Characters.") % (field_name))
            field_list = list(field)
            day = "".join(field_list[0:2])
            day_slash = field_list[2]
            day_condition = day.isalnum()
            month = "".join(field_list[3:5])
            month_slash = field_list[5]
            month_condition = month.isalnum()
            year = "".join(field_list[6:])
            year_condition = year.isalnum()
            if not day_condition or day_slash not in ('-', '/') or not month_condition or month_slash not in ('-', '/') \
                    or not year_condition:
                raise ValidationError(_(" %s Should be in this format dd/mm/yyyy or dd-mm-yyyy only") % (field_name))
            if day_condition and int(day) > 30:
                raise ValidationError(_(" %s should not be greater than 30 days") % (field_name))
            if month_condition and int(month) > 12:
                raise ValidationError(_(" %s should not be greater than 12 months") % (field_name))
            if year_condition and len(year) > 4:
                raise ValidationError(_(" Year of %s should be only 4 digits.") % (field_name))

    ###################################################################
    arabic_name = fields.Char('Arabic Name', )
    code = fields.Integer('Code', required=1)
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Code No must be unique.'),
    ]
    employee_type = fields.Selection([('employee', 'Employee'),
                                      ('driver', 'Driver'),
                                      ('mechanical', 'Mechanical')], 'Employee Type', required=1)
    ####################################################################
    identification_date = fields.Date('Identification Date', )
    identification_expiry_date = fields.Date('Identification Expiry Date', )
    identification_hijri_date = fields.Char('Identification Hijri Date', )
    identification_hijri_date_ = fields.Char('Identification Hijri Date', store=True)
    identification_expiry_hijri_date = fields.Char('Identification Expiry Hijri Date', )
    identification_expiry_hijri_date_ = fields.Char('Identification Expiry Hijri Date', store=True)
    remaining_iqama_days = fields.Integer('Remaining Iqama Date')


    # @api.one
    @api.depends('identification_hijri_date', 'identification_expiry_hijri_date')
    def get_identification_hijri_date_format(self):
        self.identification_hijri_date_ = date_conversion.reset_hijri_format(self.identification_hijri_date)
        self.identification_expiry_hijri_date_ = date_conversion.reset_hijri_format(self.identification_expiry_hijri_date)

    @api.depends('identification_expiry_date', 'identification_date')
    def _compute_remaining_iqama(self):
        for record in self:
            if record.identification_expiry_hijri_date and record.identification_hijri_date:
                self._return_validation_of_hijri_date(record.identification_hijri_date, 'identification_hijri_date')
                self._return_validation_of_hijri_date(record.identification_expiry_hijri_date,
                                                      'identification_expiry_hijri_date')
                today_date = datetime.date.today()
                today_date = str(today_date).split('-')
                hijri_today_date = date_conversion.Gregorian2Hijri(int(today_date[0]), int(today_date[1]),
                                                                   int(today_date[2]))
                record.remaining_iqama_days = (datetime.datetime.strptime(record.identification_expiry_hijri_date,
                                                                          '%d/%m/%Y').date() - datetime.datetime.strptime(
                    hijri_today_date, '%Y/%m/%d').date()).days
            else:
                record.remaining_iqama_days = 0

    border_no = fields.Char('Border No')
    kingdom_entry_date = fields.Date('Kingdom Entry Date')
    executed = fields.Char('Enter From')
    visa_job = fields.Char('Job in Iqama')
    sponsor_type = fields.Selection([
        ('internal', 'Sponsor on Company'),
        ('external', 'External')], 'Sponsor Type', default='internal')
    sponsor = fields.Char('Sponsor')
    ####################################################################
    passport_no = fields.Char('Passport No')
    passport_issue_date = fields.Date('Passport Issue Date', )
    passport_expiry_date = fields.Date('Passport Expiry Date', )
    passport_issue = fields.Char('Passport Issue')
    passport_job = fields.Char('Job in Passport')
    remaining_passport_days = fields.Integer('Remaining Passport Date')

    @api.depends('passport_expiry_date', 'passport_issue_date')
    def _compute_remaining_passport(self):
        for record in self:
            if record.passport_issue_date and record.passport_expiry_date:
                record.remaining_passport_days = (
                    datetime.datetime.strptime(record.passport_expiry_date, '%Y-%m-%d').date() - datetime.date.today()).days
            else:
                record.remaining_passport_days = 0

    ####################################################################
    license_type = fields.Char('License Type')
    license_no = fields.Char('License No')
    license_hijri_date = fields.Char('License Hijri Date', )
    license_expiry_hijri_date = fields.Char('License Expiry Hijri Date', )
    license_hijri_date_ = fields.Char('License Hijri Date', store=True, multi=True)
    license_expiry_hijri_date_ = fields.Char('License Expiry Hijri Date', store=True, multi=True, )
    remaining_license_days = fields.Integer('Remaining License Date')

    # @api.one
    @api.depends('license_hijri_date', 'license_expiry_hijri_date')
    def get_license_hijri_dates_format(self):
        self.license_hijri_date_ = date_conversion.reset_hijri_format(self.license_hijri_date)
        self.license_expiry_hijri_date_ = date_conversion.reset_hijri_format(self.license_expiry_hijri_date)

    @api.depends('license_hijri_date', 'license_expiry_hijri_date')
    def _compute_remaining_license(self):
        for record in self:
            if record.license_hijri_date and record.license_expiry_hijri_date:
                self._return_validation_of_hijri_date(record.license_hijri_date, 'license_hijri_date')
                self._return_validation_of_hijri_date(record.license_expiry_hijri_date, 'license_expiry_hijri_date')
                today_date = datetime.date.today()
                today_date = str(today_date).split('-')
                hijri_today_date = date_conversion.Gregorian2Hijri(int(today_date[0]), int(today_date[1]),
                                                                   int(today_date[2]))

            if record.license_hijri_date and record.license_expiry_hijri_date:
                record.remaining_license_days = (datetime.datetime.strptime(record.license_expiry_hijri_date,
                                                                            '%d/%m/%Y').date() - datetime.datetime.strptime(
                    hijri_today_date, '%Y/%m/%d').date()).days
            else:
                record.remaining_license_days = 0

    ####################################################################
    religion = fields.Selection([('muslim', 'Muslim'),
                                 ('christian', 'Christian'),
                                 ('buddhist', 'Buddhist'),
                                 ('other', 'Other')], 'Religion')
    blood_type = fields.Char('Blood Type')
    other_1 = fields.Char('Other1')
    other_2 = fields.Char('Other2')
    other_3 = fields.Char('Other3')
    other_4 = fields.Char('Other4')
    other_5 = fields.Char('Other5')
    other_6 = fields.Char('Other6')
    other_7 = fields.Char('Other7')
    other_8 = fields.Char('Other8')
    other_9 = fields.Char('Other9')
    other_10 = fields.Char('Other10')
    ####################################################################
    emp_id = fields.Char('ID')
    buttom_date = fields.Date('Buttom Issue Date', )
    buttom_expiry_date = fields.Date('Buttom Expiry Date', )
    remaining_buttom_days = fields.Integer('Remaining Buttom Date')

    @api.depends('buttom_expiry_date', 'buttom_date')
    def _compute_remaining_buttom(self):
        for record in self:
            if record.buttom_date and record.buttom_expiry_date:
                record.remaining_buttom_days = (
                    datetime.datetime.strptime(record.buttom_expiry_date, '%Y-%m-%d').date() - datetime.date.today()).days
            else:
                record.remaining_buttom_days = 0

    ####################################################################
    aramco_no = fields.Char('Aramco No')
    serial = fields.Char('Serial No')
    aramco_issue_date = fields.Date('Aramco Issue Date', )
    aramco_expiry_date = fields.Date('Aramco Expiry Date', )
    remaining_aramco_days = fields.Integer('Remaining Aramco Date')

    @api.depends('aramco_expiry_date', 'aramco_issue_date')
    def _compute_remaining_aramco(self):
        for record in self:
            if record.aramco_expiry_date and record.aramco_issue_date:
                record.remaining_aramco_days = (
                    datetime.datetime.strptime(record.aramco_expiry_date, '%Y-%m-%d').date() - datetime.date.today()).days
            else:
                record.remaining_aramco_days = 0

    ####################################################################
    electric_no = fields.Char('Electric Card')
    electric_serial = fields.Char('Electric Serial No')
    electric_issue_date = fields.Date('Electric Issue Date', )
    electric_expiry_date = fields.Date('Electric Expiry Date', )
    remaining_electric_days = fields.Integer('Remaining Electric Date')

    @api.depends('electric_expiry_date', 'electric_issue_date')
    def _compute_remaining_electric(self):
        for record in self:
            if record.electric_expiry_date and record.electric_issue_date:
                record.remaining_electric_days = (
                    datetime.datetime.strptime(record.electric_expiry_date, '%Y-%m-%d').date() - datetime.date.today()).days
            else:
                record.remaining_electric_days = 0

    ####################################################################
    branch_name = fields.Many2one('branch', 'Branch Name')
    branch_no = fields.Char(string='Branch No', related="branch_name.code")
    has_vehicle = fields.Boolean(string='Has Vehicle', default=False)
    ####################################################################
    insurance_no = fields.Char('Insurance No')
    # insurance_company = fields.Many2one('res.partner', 'Insurance Company')
    insurance_degree = fields.Char('Insurance Degree')
    insurance_issue_date = fields.Date('Insurance Issue Date', )
    insurance_expiry_date = fields.Date('Insurance Expiry Date', )
    remaining_insurance_days = fields.Integer('Remaining Insurance Date')

    @api.depends('insurance_expiry_date', 'insurance_issue_date')
    def _compute_remaining_insurance(self):
        for record in self:
            if record.insurance_issue_date and record.insurance_expiry_date:
                record.remaining_insurance_days = (datetime.datetime.strptime(record.insurance_expiry_date,
                                                                              '%Y-%m-%d').date() - datetime.date.today()).days
            else:
                record.remaining_insurance_days = 0

    ####################################################################
    dependence_ids = fields.One2many('dependence.line', 'employee_id', 'Dependence')
    ####################################################################
    note = fields.Html('Notes')
    not_financial_custody_id = fields.One2many('not.financial.custody', 'employee_id', 'Custody')
    salary_receive = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], 'Salary Received')
    can_take_loan = fields.Boolean('Can take loan')
    loan_account_id = fields.Many2one('account.account', 'Loan account')
    ####################################################################
    liquidity_account_id = fields.Many2one('account.account', 'Liquidity Account')
    state = fields.Selection([('new', 'New'),
                              ('review', 'Reviewed'),
                              ('confirm', 'Confirmed'),
                              ('close', 'Closed')], 'State', default='new')

    ####################################################################
    # @api.one
    def button_review(self):
        self.write({'state': 'review'})

    # @api.one
    def button_confirm(self):
        return self.write({'state': 'confirm'})

    # @api.one
    def button_close(self):
        return self.write({'active': False, 'state': 'close'})

    # 
    def unlink(self):
        for record in self:
            if record.branch_name:
                raise ValidationError(_('You cannot delete employee linked to branch, please delete first from branch'))
        return super(hr_employee, self).unlink()

    ####################################################################

    # @api.one
    @api.constrains('arabic_name', 'code', 'border_no', 'visa_job', 'executed', 'emp_id', 'insurance_no',
                    'insurance_company', 'insurance_degree', 'identification_hijri_date',
                    'identification_expiry_hijri_date', 'license_hijri_date', 'license_expiry_hijri_date')
    def _check_digit(self):

        self._return_validation_of_hijri_date(self.identification_hijri_date, 'identification_hijri_date')
        self._return_validation_of_hijri_date(self.identification_expiry_hijri_date, 'identification_expiry_hijri_date')

        if self.arabic_name and len(self.arabic_name) > 40:
            raise ValidationError(_("Arabic Name should be less than 40 digits only"))

        if self.code and len(str(self.code)) > 6:
            raise ValidationError(_("Code should be less than 6 digits only"))

        if self.border_no:
            if self.border_no and len(self.border_no) > 20:
                raise ValidationError(_("Border No should be less than 6 digits only"))

        if self.visa_job:
            if self.visa_job and len(self.visa_job) > 20:
                raise ValidationError(_("Visa Job should be less than 6 digits only"))

        if self.executed:
            if self.executed and len(self.executed) > 20:
                raise ValidationError(_("Executed should be less than 6 digits only"))

        if self.emp_id:
            if self.emp_id and len(self.emp_id) > 15:
                raise ValidationError(_("ID should be less than 6 digits only"))

        if self.insurance_no:
            if self.insurance_no and len(self.insurance_no) > 15:
                raise ValidationError(_("Insurance should be less than 6 digits only"))

        if self.insurance_degree and len(self.insurance_degree) > 10:
            raise ValidationError(_("Insurance Degree should be less than 6 digits only"))

   
    # 
    def report_doc_expiry_data(self):
        data = {}
        if self.remaining_iqama_days <= 60 and self.identification_expiry_hijri_date:
            data['iqama'] = {'remaining': self.remaining_iqama_days, 'expiry_date': self.identification_expiry_hijri_date, 'name': 'الإقامة'}
        if self.remaining_passport_days <= 60 and self.passport_expiry_date:
            data['passport'] = {'remaining': self.remaining_passport_days, 'expiry_date': self.passport_expiry_date, 'name': 'جواز السفر'}
        if self.remaining_license_days <= 60 and self.license_expiry_hijri_date:
            data['license'] = {'remaining': self.remaining_license_days, 'expiry_date': self.license_expiry_hijri_date, 'name': 'رخصة القياده'}
        if self.remaining_buttom_days < 60 and self.buttom_expiry_date:
            data['buttom'] = {'remaining': self.remaining_buttom_days, 'expiry_date': self.buttom_expiry_date, 'name': 'البوتون'}
        if self.remaining_aramco_days <= 60 and self.aramco_expiry_date:
            data['aramco'] = {'remaining': self.remaining_aramco_days, 'expiry_date': self.aramco_expiry_date, 'name': 'ترخيص ارامكو'}
        if self.remaining_insurance_days < 60 and self.insurance_expiry_date:
            data['insurance'] = {'remaining': self.remaining_insurance_days, 'expiry_date': self.insurance_expiry_date, 'name': 'التأمين الصحين'}
        return data

    class discount_commission_line(models.Model):
        _name = 'discount.commission.line'

        employee_id = fields.Many2one('hr.employee', 'Employee', required=1)
        amount = fields.Float('Amount', required=1)
        type = fields.Selection([
            ('commission', 'Commission'),
            ('discount', 'Discount')], 'Type', required=1)
        cause = fields.Char('Cause', required=1)
        effective_date = fields.Date('Effective Date', required=1)
        done = fields.Boolean('Done', readonly=1)
        line_id = fields.Many2one('discount.commission', 'line')

        ####################################################################
        # @api.one
        @api.constrains('amount', 'type', 'cause')
        def _check_digit(self):

            if len(str(int(self.amount))) > 6:
                raise ValidationError(_("Amount should be less than 6 digits only"))

            if len(str(self.cause)) > 50:
                raise ValidationError(_("Cause should be less than 6 digits only"))

    class discount_commission(models.Model):
        _name = 'discount.commission'

        code = fields.Integer('Code')
        line_ids = fields.One2many('discount.commission.line', 'line_id', 'Data')
        note = fields.Html('Notes')


