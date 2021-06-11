# -*- coding: utf-8 -*-
{
    'name': 'Fahad HR ',
    'version': '1.0',
    'sequence': '2',
    'summary': 'This module deal with HR company business',
    'description': """
Transportation
======================================

New Module For Adding new windows in HR

""",
    'depends': [
        'hr',
        'hr_contract',
        'hr_payroll',
        'hr_payroll_account'
        # ,
        # 'web_m2x_options'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fahad_hr_view.xml',
        'views/fahad_ticketing_view.xml',
        'views/fahad_eoc_view.xml',
        'views/fahad_payslip_view.xml',
        'views/hr_menu.xml',
        'data/fahad_salary_scale.xml',
        'views/fahad_report.xml',
        'report/payslip_report.xml',
        'views/eoc_report_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: