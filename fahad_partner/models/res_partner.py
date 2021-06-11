from odoo import models, fields, api, _



class res_partner(models.Model):
    _inherit = 'res.partner'

    partner_id_unique = fields.Char('Customer ID')

    _sql_constraints = [
        ('partner_id_unique', 'unique(partner_id_unique)', 'Customer ID must be unique.'),
    ]

    #def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
    #    args = args or []
    #    if name:
    #        ids = self.search(cr, user, ['|', ('name', 'ilike', name), ('partner_id_unique', 'ilike', name)], limit=6)
    #    else:
    #        ids = self.search(cr, user, args, limit=limit, context=context or {})
    #    return super(res_partner, self).name_get(cr, user, ids, context=context)
