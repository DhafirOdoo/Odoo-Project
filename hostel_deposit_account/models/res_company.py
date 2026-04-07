from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    hostel_deposit_account_id = fields.Many2one(
        'account.account',
        string='Hostel Deposit Account',
        domain=[('account_type', '=', 'liability_current')]
    )