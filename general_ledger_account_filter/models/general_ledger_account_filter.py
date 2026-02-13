from odoo import fields, models

class GeneralLedgerAccountFilterWizard(models.TransientModel):
    _inherit = 'account.report.general.ledger'


    account_ids = fields.Many2many('account.account', string='Accounts')

