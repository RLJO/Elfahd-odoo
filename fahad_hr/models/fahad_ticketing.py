from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
from odoo.addons.date_conversion import date_conversion


class hr_ticketing(models.Model):
    _name = 'hr.ticketing'

    name = fields.Char(string='Employee name', related='employee_id.name')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    ticket_nature = fields.Selection([('cash', 'Cash'), ('reserve', 'Reserve')], 'Ticket Nature')
    ticket_price = fields.Float('Ticket Price')
    contract_start_date = fields.Date('Contract Start Date', compute='_compute_contract', multi='contract')
    contract_end_date = fields.Date('Contract End Date', compute='_compute_contract', multi='contract')
    contract_id = fields.Many2one('hr.contract', compute='_compute_contract')
    liquidity_account_id = fields.Many2one('account.account', 'Liquidity Account')
    expense_account_id = fields.Many2one('account.account', 'Expense Account')
    journal_id = fields.Many2one('account.journal', 'Journal')
    state = fields.Selection([('draft', 'Draft'),
                              ('review', 'Review'),
                              ('confirm', 'Confirm')], 'State', default='draft')
    note=fields.Html('Notes')

    @api.constrains('ticket_price')
    def _check_ticket_price(self):
        if self.ticket_price == 0.0:
            raise ValidationError(_("Error \n Ticket price cannot be zero(0)"))

    @api.depends('employee_id')
    def _compute_contract(self):
        contract_obj = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('active', '=', True)])
        for obj in contract_obj:
            self.contract_start_date = obj.date_start or False
            self.contract_end_date = obj.date_end or False
            self.contract_id = obj.id

    def button_review(self):
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('active', '=', True),
                                                       ('ticket_used', '=', 'yes')])
        if contract_obj:
            raise ValidationError(_("Error \n You cannot create ticket for this employee, "
                                    "He take ticket before in this contract"))
        self.write({'state': 'review'})

    def button_draft(self):
        self.write({'state': 'draft'})

    def button_confirm(self):
        vals = {}
        line_vals = {}
        dict = {}
        contract_obj = self.env['hr.contract'].browse(self.contract_id.id)
        contract_obj.write({'ticket_used': 'yes'})
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']
        vals.update({
            'journal_id': self.journal_id.id,
            'date': datetime.date.today(),
            'period_id': account_move._get_period(),
        })
        move = account_move.create(vals)
        if move:
            line_vals['move_id'] = move.id
            line_vals['name'] = "Ticket allowance for employee: " + self.employee_id.name
            line_vals['period_id'] = account_move._get_period()
            line_vals['debit'] = self.ticket_price
            line_vals['credit'] = 0.0
            line_vals['account_id'] = self.expense_account_id.id
            account_move_line.create(line_vals)
            line_vals['debit'] = 0.0
            line_vals['credit'] = self.ticket_price
            line_vals['account_id'] = self.liquidity_account_id.id
            account_move_line.create(line_vals)
        self.write({'state': 'confirm'})

    def unlink(self):
        if self.state == "confirm":
            raise ValidationError(_("You cannot delete confirmed ticket"))
        super(hr_ticketing, self).unlink()