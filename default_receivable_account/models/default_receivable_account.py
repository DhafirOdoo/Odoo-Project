from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    partner_receivable_account_id = fields.Many2one(
        'account.account',
        string="Default Receivable Account",
        domain="[('account_type','=','asset_receivable')]",
        help="Default Receivable Account For Customers",
        default_model='res.company'
    )
