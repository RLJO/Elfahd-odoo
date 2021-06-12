import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class fahad_contract(models.Model):
    _name = 'fahad.contract'
    _description = 'Contract'
    _rec_name = 'contract_no'

    contract_no = fields.Char('Contract No', required=1)
    contractor_no = fields.Char('Contractor No', required=1)
    purchase_no = fields.Char('Purchase No', required=1)
    contract_start_date = fields.Date('Contract Start Date', required=1)
    contract_end_date = fields.Date('Contract End Date', required=1)
    note = fields.Html('Note')
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('closed', 'Closed')], 'State', default='draft')

    # @api.one
    @api.constrains('contract_start_date', 'contract_end_date')
    def _check_lines(self):
        for record in self:
            start_date = datetime.datetime.strptime(record.contract_start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(record.contract_end_date, '%Y-%m-%d').date()
            if start_date > end_date:
                raise ValidationError(_("Start date mus be less than End date"))

    # @api.one
    def button_review(self):
        self.write({'state': 'reviewed'})

    # @api.one
    def button_confirm(self):
        self.write({'state': 'confirmed'})

    # @api.one
    def button_close(self):
        self.write({'state': 'closed'})

    # @api.one
    def button_draft(self):
        self.write({'state': 'draft'})

    # 
    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise Warning(_('You cannot delete confirmed contract'))
        return super(fahad_contract, self).unlink()

