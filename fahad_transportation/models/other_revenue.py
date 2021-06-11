import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class other_revenue_line(models.Model):
    _name = 'other.revenue.line'
    _description = 'Other Revenue Line'

    description = fields.Char('Description')
    number = fields.Integer('Number', default='1')
    amount = fields.Float('Amount')
    total = fields.Float('Total')
    note = fields.Char('Note', size=20)
    line_id = fields.Many2one('other.revenue', 'Line')

    # @api.multi
    @api.depends('number', 'amount')
    def _compute_total(self):
        self.total = self.number * self.amount

    # @api.one
    @api.constrains('number', 'amount')
    def _check_lines(self):
        for record in self:
            if record.number <= 0:
                raise ValidationError(_("Number must be +ve and bigger than 0"))
            if record.amount <= 0:
                raise ValidationError(_("Amount must be +ve and bigger than 0"))


class other_revenue(models.Model):
    _name = 'other.revenue'
    _description = 'Other Revenue'
    _rec_name = 'code'

    code = fields.Char('Code')
    car_category_id = fields.Many2one('car.category', 'Car Category')
    car_id = fields.Many2one('new.car', 'Car')
    ownership = fields.Selection(string='Ownership', related='car_id.ownership')
    owner = fields.Many2one('res.partner', string='Owner', related='car_id.external_ownership')
    commission = fields.Selection([('no', 'No'), ('yes', 'Yes')], 'Commission', default='no')
    commission_amount = fields.Float('Commission Amount')
    date = fields.Date('Date')
    customer_id = fields.Many2one('res.partner', 'Customer')
    journal_id = fields.Many2one('account.journal', 'Journal')
    income_account_id = fields.Many2one('account.account', 'Income Account')
    line_ids = fields.One2many('other.revenue.line', 'line_id', 'Data Entry')
    account_move_ids = fields.One2many('account.move', 'other_revenue_id', 'Journal Entry')
    note = fields.Html('Note')
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'Reviewed'),
                              ('confirmed', 'Confirmed'),
                              ('closed', 'Closed')], 'State', default='draft')

    # @api.one
    # @api.onchange('car_category_id')
    # def onchange_car_category_id(self):
    #     self.car_id = False

    # @api.one
    @api.constrains('commission', 'commission_amount')
    def _check_amount(self):
        if self.commission == 'yes':
            if self.commission_amount == 0.0:
                raise ValidationError(_("Commission cannot be 0"))

    # @api.one
    def button_review(self):
        if not self.line_ids:
            raise ValidationError(_("You have to enter at least one line"))
        self.code = self.env['ir.sequence'].get('other.revenue')
        self.write({'state': 'reviewed'})

    # @api.one
    def button_confirm(self):
        invoice_line = []
        vals = {}
        line_vals = {}
        total = 0
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']
        if self.ownership == 'private':
            for item in self.line_ids:
                total += item.total
                invoice_line.append([0, False, {'name': item.description,
                                                'price_unit': item.amount,
                                                'account_id': self.customer_id.property_account_receivable.id,
                                                'quantity': item.number}])
                # invoice
            invoice_id = self.env['account.account'].create({'partner_id': self.customer_id.id,
                                                             'account_id': self.income_account_id.id,
                                                             'invoice_line': invoice_line,
                                                             'journal_id': self.journal_id.id,
                                                             'type': 'out_invoice'})
            vals.update({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'period_id': account_move._get_period(),
                'other_revenue_id': self.id,
            })
            move = account_move.create(vals)
            if move:
                line_vals['move_id'] = move.id
                line_vals['name'] = "Plat No: " + self.car_id.plaque_no
                line_vals['period_id'] = account_move._get_period()
                line_vals['debit'] = total
                line_vals['credit'] = 0.0
                line_vals['account_id'] = self.customer_id.property_account_receivable.id
                line_vals['partner_id'] = self.customer_id.id
                account_move_line.create(line_vals)
                line_vals['debit'] = 0.0
                line_vals['credit'] = total
                line_vals['account_id'] = self.income_account_id.id
                account_move_line.create(line_vals)
        elif self.ownership == 'external':
            for item in self.line_ids:
                total += item.total
            if self.commission_amount == 0:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                    'other_revenue_id': self.id,
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Plat No: " + self.car_id.plaque_no
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = total
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = total
                    line_vals['account_id'] = self.owner.property_account_payable.id
                    line_vals['partner_id'] = self.owner.id
                    account_move_line.create(line_vals)
            elif self.commission_amount != 0:
                vals.update({
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': account_move._get_period(),
                    'other_revenue_id': self.id,
                })
                move = account_move.create(vals)
                if move:
                    line_vals['move_id'] = move.id
                    line_vals['name'] = "Plat No: " + self.car_id.plaque_no
                    line_vals['period_id'] = account_move._get_period()
                    line_vals['debit'] = total
                    line_vals['credit'] = 0.0
                    line_vals['account_id'] = self.customer_id.property_account_receivable.id
                    line_vals['partner_id'] = self.customer_id.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = total - self.commission_amount
                    line_vals['account_id'] = self.owner.property_account_payable.id
                    line_vals['partner_id'] = self.owner.id
                    account_move_line.create(line_vals)
                    line_vals['debit'] = 0.0
                    line_vals['credit'] = self.commission_amount
                    line_vals['account_id'] = self.income_account_id.id
                    account_move_line.create(line_vals)
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
                raise ValidationError(_('You cannot delete confirmed expense register'))
        return super(other_revenue, self).unlink()

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].get('other.revenue')
    #     return super(other_revenue, self).create(vals)


class account_move(models.Model):
    _inherit = 'account.move'

    other_revenue_id = fields.Many2one('other.revenue', _('Other Revenue'))