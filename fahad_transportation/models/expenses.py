import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class expenses(models.Model):
    _name = 'expenses'
    _description = 'Expenses'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    code = fields.Char('Code', readonly=1)
    name = fields.Char('Expense Name', required=1)
    expense_nature = fields.Selection([('capital', 'Capital'),
                                       ('operational', 'Operational')], 'Expense Nature', required=1,)
    expense_account = fields.Many2one('account.account', 'Expense Account')
    expense_type = fields.Selection([('car', 'Car'),
                                     ('tank', 'Tank'),
                                     ('trip', 'Trip')], 'Expense Type', required=1, change_default=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=1)
    note = fields.Html('Note')
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('closed', 'Closed')], 'State', default='draft')

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].get('expense')
    #     return super(expenses, self).create(vals)

    # @api.one
    def button_review(self):
        self.code = self.env['ir.sequence'].get('expense')
        self.write({'state': 'reviewed'})

    # @api.one
    def button_confirm(self):
        for record in self:
            if record.expense_nature == 'capital' and record.expense_type == 'trip':
                raise ValidationError(_("You Cannot define capital expense on trip"))
        self.write({'state': 'confirmed'})

    # @api.one
    def button_close(self):
        self.write({'state': 'closed'})

    # @api.one
    def button_draft(self):
        self.write({'state': 'draft'})

    # @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise Warning(_('You cannot delete confirmed expense'))
        return super(expenses, self).unlink()

