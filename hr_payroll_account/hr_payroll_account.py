# -*- coding:utf-8 -*-

import time
from datetime import date, datetime, timedelta
from odoo.osv import fields, osv
from odoo.tools import float_compare, float_is_zero
from odoo.tools.translate import _


class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    _columns = {
        'period_id': fields.many2one('account.period', 'Force Period', states={'draft': [('readonly', False)]},
                                     readonly=True, domain=[('state', '<>', 'done')],
                                     help="Keep empty to use the period of the validation(Payslip) date."),
        'journal_id': fields.many2one('account.journal', 'Salary Journal', states={'draft': [('readonly', False)]},
                                      readonly=True, required=True),
        'move_id': fields.many2one('account.move', 'Accounting Entry', readonly=True, copy=False),
    }

    def _get_default_journal(self, cr, uid, context=None):
        model_data = self.pool.get('ir.model.data')
        res = model_data.search(cr, uid, [('name', '=', 'expenses_journal')])
        if res:
            return model_data.browse(cr, uid, res[0]).res_id
        return False

    _defaults = {
        'journal_id': _get_default_journal,
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'journal_id' in context:
            vals.update({'journal_id': context.get('journal_id')})
        return super(hr_payslip, self).create(cr, uid, vals, context=context)

    def onchange_contract_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False,
                             context=None):
        contract_obj = self.pool.get('hr.contract')
        res = super(hr_payslip, self).onchange_contract_id(cr, uid, ids, date_from=date_from, date_to=date_to,
                                                           employee_id=employee_id, contract_id=contract_id,
                                                           context=context)
        journal_id = contract_id and contract_obj.browse(cr, uid, contract_id, context=context).journal_id.id or False
        res['value'].update({'journal_id': journal_id})
        return res

    def cancel_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        move_ids = []
        move_to_cancel = []
        for slip in self.browse(cr, uid, ids, context=context):
            if slip.move_id:
                move_ids.append(slip.move_id.id)
                if slip.move_id.state == 'posted':
                    move_to_cancel.append(slip.move_id.id)
        move_pool.button_cancel(cr, uid, move_to_cancel, context=context)
        move_pool.unlink(cr, uid, move_ids, context=context)
        return super(hr_payslip, self).cancel_sheet(cr, uid, ids, context=context)

    def process_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        period_pool = self.pool.get('account.period')
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Payroll')
        timenow = time.strftime('%Y-%m-%d')
        ######## My Add #######
        vals = {}
        line_vals = {}
        flag = False
        ##### My Add finished #####

        for slip in self.browse(cr, uid, ids, context=context):
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            if not slip.period_id:
                search_periods = period_pool.find(cr, uid, slip.date_to, context=context)
                period_id = search_periods[0]
            else:
                period_id = slip.period_id.id

            default_partner_id = slip.employee_id.address_home_id.id
            name = _('Payslip of %s') % (slip.employee_id.name)
            move = {
                'narration': name,
                'date': timenow,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
            }
            for line in slip.details_by_salary_rule_category:
                amt = slip.credit_note and -line.total or line.total
                if float_is_zero(amt, precision_digits=precision):
                    continue
                partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    ##### My Add ####
                    flag = True
                    ##### My Add Finished ####
                    debit_line = (0, 0, {
                        'name': line.name,
                        'date': timenow,
                        'partner_id': (
                                          line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in (
                                              'receivable', 'payable')) and partner_id or False,
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id,
                        'debit': amt > 0.0 and amt or 0.0,
                        'credit': amt < 0.0 and -amt or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                        'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'date': timenow,
                        'partner_id': (
                                          line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_credit.type in (
                                              'receivable', 'payable')) and partner_id or False,
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id,
                        'debit': amt < 0.0 and -amt or 0.0,
                        'credit': amt > 0.0 and amt or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                        'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_credit_account_id.id
                # if not acc_id:
                #     raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise osv.except_osv(_('Configuration Error!'),
                                         _(
                                             'The Expense Journal "%s" has not properly configured the Debit Account!') % (
                                             slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            ########### My Code ##############
            if not flag:
                raise osv.except_osv(_('Configuration Error!'), _('At least one rule must have debit ACC'))

            def get_rule_by_code(code):
                rule_obj = self.pool.get('hr.salary.rule')
                id = rule_obj.search(cr, uid, [('code', '=', code)])
                return rule_obj.browse(cr, uid, id, context)

            (case, code) = len([rule for rule in slip.details_by_salary_rule_category
                                if (rule.salary_rule_id.code in ['COM', 'DED', 'LOAN'] and rule.amount)]) == 0 and \
                           (1, 'FAHAD_BASIC') or (2, 'FAHAD_NET')

            # ['COM', 'DED', 'LOAN', 'FAHAD_NET', 'FAHAD_BASIC'
            basic_account_id = get_rule_by_code(code).account_debit.id
            if not basic_account_id:
                raise osv.except_osv(_("Accounts Error"),_("Please!! Cofigure account for \n- %s Rule"%(get_rule_by_code(code).name)))
            line = {
                'debit': 0.0,
                'credit': 0.0,
                'account_id': False,
                'name': '/',  # 'راتب الموظف %s عن شهر %s' % (slip.employee_id.name, slip.month),
                'period_id': period_id,
                'journal_id': slip.journal_id.id,
            }
            lines = []
            for rule in slip.details_by_salary_rule_category:
                code = rule.salary_rule_id.code
                if code in ['FAHAD_BASIC','COM','DED','LOAN','FAHAD_NET'] and rule.amount < 0:
                    raise osv.except_osv(_("Error in rule valu"),_("rule value can't be less than zero \n(%s)"%rule.name))
                if code == 'FAHAD_BASIC':
                    line = {
                        'debit': rule.amount,
                        'credit': 0.0,
                        'account_id': basic_account_id,
                        'name': '/',  # 'راتب الموظف %s عن شهر %s' % (slip.employee_id.name, slip.month),
                        'period_id': period_id,
                        'journal_id': slip.journal_id.id,
                    }
                    lines.append((0, 0, line))
                    del line
                if code == 'COM' and case == 2:
                    if not get_rule_by_code(code).account_debit.id:
                        raise osv.except_osv(_("Accounts Error"),_("Please!! Cofigure account for \n- %s Rule" % (get_rule_by_code(code).name)))
                    line = {
                        'debit': rule.amount,
                        'credit': 0.0,
                        'account_id': get_rule_by_code(code).account_debit.id,
                        'name': '/',  # 'راتب الموظف %s عن شهر %s' % (slip.employee_id.name, slip.month),
                        'period_id': period_id,
                        'journal_id': slip.journal_id.id,
                    }
                    lines.append((0, 0, line))
                    del line
                if code in ['DED',] and case == 2:
                    if not get_rule_by_code(code).account_credit.id:
                        raise osv.except_osv(_("Accounts Error"),_("Please!! Cofigure account for \n- %s Rule"%(get_rule_by_code(code).name)))
                    line = {
                        'debit': 0.0,
                        'credit': rule.amount,
                        'account_id': get_rule_by_code(code).account_credit.id,
                        'name': '/',  # 'راتب الموظف %s عن شهر %s' % (slip.employee_id.name, slip.month),
                        'period_id': period_id,
                        'journal_id': slip.journal_id.id,
                    }
                    lines.append((0, 0, line))
                    del line
                if code in ['LOAN'] and case == 2:
                    if not slip.employee_id.loan_account_id.id:
                        raise osv.except_osv(_("Accounts Error"),
                             _("Please!! Cofigure account for loans in %s"%(slip.employee_id.name)))
                    line = {
                        'debit': 0.0,
                        'credit': rule.amount,
                        'account_id': slip.employee_id.loan_account_id.id,
                        'name': '/',  # 'راتب الموظف %s عن شهر %s' % (slip.employee_id.name, slip.month),
                        'period_id': period_id,
                        'journal_id': slip.journal_id.id,
                    }
                    lines.append((0, 0, line))
                    del line
                if code == 'FAHAD_NET':
                    if not slip.employee_id.liquidity_account_id.id:
                        raise osv.except_osv(_("Account Error"),_("Please!! Cofigure Liquidity account for \n%s"%(slip.employee_id.name)))
                    line = {
                        'debit': 0.0,
                        'credit': rule.amount,
                        'account_id': slip.employee_id.liquidity_account_id.id,
                        'name': '/',  # 'راتب الموظف %s عن شهر %s' % (slip.employee_id.name, slip.month),
                        'period_id': period_id,
                        'journal_id': slip.journal_id.id,
                    }
                    lines.append((0, 0, line))
                    del line
            move['line_id'] = lines
            move_id = move_pool.create(cr, uid, move, context=context)

            # for rule in slip.details_by_salary_rule_category:
            #     if rule.salary_rule_id.account_debit.id:
            #         default_debit_id = rule.salary_rule_id.account_debit.id
            # if rule.salary_rule_id.code == 'FAHAD_NET':
            #     if rule.salary_rule_id.account_debit.id:
            #         debit_account_id = rule.salary_rule_id.account_debit.id
            #     else:
            #         debit_account_id = default_debit_id
            #     vals.update({
            #         'journal_id': slip.journal_id.id,
            #         'date': timenow,
            #         'period_id': period_id,
            #     })
            #     move_id = move_pool.create(cr, uid, move, context=context)
            #     if move_id:
            #         line_vals['move_id'] = move_id
            #         line_vals['name'] = "Employee Payslip"
            #         line_vals['period_id'] = period_id
            #         line_vals['debit'] = rule.total
            #         line_vals['credit'] = 0.0
            #         line_vals['account_id'] = debit_account_id
            #         move_line_pool.create(cr, uid, line_vals, context=context)
            #         line_vals['debit'] = 0.0
            #         line_vals['credit'] = rule.total
            #         line_vals['account_id'] = slip.employee_id.liquidity_account_id.id
            #         move_line_pool.create(cr, uid, line_vals, context=context)

            # move.update({'line_id': line_ids})
            # move_id = move_pool.create(cr, uid, move, context=context)
            ########### My Added Finished ###########
            self.write(cr, uid, [slip.id], {'move_id': move_id, 'period_id': period_id}, context=context)
            if slip.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context=context)
        return super(hr_payslip, self).process_sheet(cr, uid, [slip.id], context=context)


class hr_salary_rule(osv.osv):
    _inherit = 'hr.salary.rule'
    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'account_tax_id': fields.many2one('account.tax.code', 'Tax Code'),
        'account_debit': fields.many2one('account.account', 'Debit Account'),
        'account_credit': fields.many2one('account.account', 'Credit Account'),
    }


class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'
    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'journal_id': fields.many2one('account.journal', 'Salary Journal'),
    }


class hr_payslip_run(osv.osv):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Run'
    _columns = {
        'journal_id': fields.many2one('account.journal', 'Salary Journal', states={'draft': [('readonly', False)]},
                                      readonly=True, required=True),
    }

    def _get_default_journal(self, cr, uid, context=None):
        model_data = self.pool.get('ir.model.data')
        res = model_data.search(cr, uid, [('name', '=', 'expenses_journal')])
        if res:
            return model_data.browse(cr, uid, res[0]).res_id
        return False

    _defaults = {
        'journal_id': _get_default_journal,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
