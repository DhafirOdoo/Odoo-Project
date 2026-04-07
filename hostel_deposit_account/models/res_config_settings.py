from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hostel_deposit_account_id = fields.Many2one(
        related='company_id.hostel_deposit_account_id',
        readonly=False,
        string='Deposit Account'
    )