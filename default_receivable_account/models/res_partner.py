from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        partner = super().create(vals)
        company = partner.company_id or self.env.company

        if company.partner_receivable_account_id:
            partner.property_account_receivable_id = (
                company.partner_receivable_account_id.id
            )

        return partner
