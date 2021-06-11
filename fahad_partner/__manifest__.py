# -*- coding: utf-8 -*-
{
    'name': 'Fahad Partner',
    'version': '1.0',
    'sequence': '2',
    'summary': 'This module add fields in res_partner',
    'description': """
Transportation
======================================

New Module For Transportation

""",
    'depends': ['purchase', 'sale'],
    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: