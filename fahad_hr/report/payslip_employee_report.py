# -*- coding: utf-8 -*-

import time
# from odoo.report import report_sxw
from odoo.tools.translate import _
from odoo.osv import osv



class employee_payslip():
    def __init__(self, cr, uid, name, context=None):
        super(employee_payslip, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'trips_count': self.trips_count,
            'month_name': self.month_name
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        return super(employee_payslip, self).set_context(objects, data, ids, report_type=report_type)

    def month_name(self, o):
        month = o.date_from.split('-')[1]
        months = {
            '01': 'يناير',
            '02': 'فبراير',
            '03': 'مارس',
            '04': 'ابريل',
            '05': 'مايو',
            '06': 'يونيو',
            '07': 'يوليو',
            '08': 'اغسطس',
            '09': 'سبتمبر',
            '10': 'أكتوبر',
            '11': 'نوفمبر',
            '12': 'ديسمبر',
        }
        return '%s / %s' % (months[month], o.date_from.split('-')[0])

    def trips_count(self, o):
        commision_obj = self.pool.get('commission.line')
        ids = commision_obj.search(self.cr, self.uid,
                                   [('contract_id', '=', o.contract_id.id),
                                    ('date', '>=', o.date_from),
                                    ('date', '<=', o.date_to), ])
        return len(ids)


class report_employee_payslip(osv.AbstractModel):
    _name = 'report.fahad_hr.report_payslip_employees'
    # _inherit = 'report.abstract_report'
    _template = 'fahad_hr.report_payslip_employees'
    _wrapped_report_class = employee_payslip
