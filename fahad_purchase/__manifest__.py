# -*- coding: utf-8 -*-
{
    'name': 'Fahad Purchase',
    'version': '1.0',
    'sequence': '2',
    'summary': 'This module add fields in Purchase order and edit reports',
    'description': """
Transportation
======================================

New Module For Transportation

""",
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_view.xml',
        'views/purchase_report.xml',
        'views/products.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: