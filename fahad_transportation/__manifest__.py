# -*- coding: utf-8 -*-
{
    'name': 'Transportation ',
    'version': '1.0',
    'sequence': '1',
    'summary': 'This module deal with transportation company business',
    'description': """
Transportation
======================================

New Module For Transportation

""",
    'depends': [
        'base',
        'hr',
        'account',
        'account_accountant',
        'product',
        'account_asset',
        'stock',
        # 'web_m2x_options',
        'stock_account',
        # 'document',
        'fahad_hr',
        'l10n_multilang',
        'purchase',
        # 'account_anglo_saxon',
        # 'web_rtl',
        # 'web_printscreen_zb',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/fahad_security.xml',
        'views/transportation_seq.xml',
        'views/car_category_view.xml',
        'views/vehicle_history.xml',
        'views/transportation_view.xml',
        'views/new_car_view.xml',
        'views/new_tank_view.xml',
        'views/transport_branch_view.xml',

        'views/transport_wheel_view.xml',
        'views/transport_vehicle_view.xml',
        'views/transport_vehicle_dismantling_view.xml',
        'views/fahad_hr_view.xml',
        'views/contract_view.xml',
        'views/expenses_view.xml',
        'views/trips_view.xml',
        'views/expense_register_view.xml',
        'views/rent_view.xml',
        'views/other_revenue_view.xml',
        'views/buy_screen_view.xml',

        'views/car_maintenance_view.xml',
        'views/car_asset_view.xml',
        'reports/report_new_car.xml',
        'reports/report_new_tank.xml',
        'reports/employee_document_expiry.xml',
        'views/transportation_report.xml',
        'views/transportation_menu.xml',
        'views/others.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
