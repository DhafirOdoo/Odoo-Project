from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    partner_receivable_account_id = fields.Many2one(
        related='company_id.partner_receivable_account_id',
        readonly=False,
        string="Default Receivable Account",
    )

    def set_values(self):
        super().set_values()
        if self.partner_receivable_account_id:
            partners = self.env['res.partner'].search([
                ('customer_rank', '>', 0),
                ('company_id', 'in', [self.company_id.id, False])
            ])
            partners.write({
                'property_account_receivable_id': self.partner_receivable_account_id.id
            })