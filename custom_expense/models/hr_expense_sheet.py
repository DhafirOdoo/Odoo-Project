from odoo import fields, models
from odoo.tools import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'



    vendor_id = fields.Many2one('res.partner', string='Vendor', domain="[('supplier_rank', '>', 0)]")

    def _do_create_moves(self):
        self = self.with_context(clean_context(self.env.context))  # remove default_*
        skip_context = {
            'skip_invoice_sync': True,
            'skip_invoice_line_sync': True,
            'skip_account_move_synchronization': True,
        }
        own_account_sheets = self.filtered(lambda sheet: sheet.payment_mode == 'own_account')
        company_account_sheets = self - own_account_sheets

        moves = self.env['account.move'].create([sheet._prepare_bills_vals() for sheet in own_account_sheets])
        # Set the main attachment on the moves directly to avoid recomputing the
        # `register_as_main_attachment` on the moves which triggers the OCR again
        for move in moves:
            move.message_main_attachment_id = move.attachment_ids[0] if move.attachment_ids else None
        payments = self.env['account.payment'].with_context(**skip_context).create([
            expense._prepare_payments_vals() for expense in company_account_sheets.expense_line_ids
        ])
        moves |= payments.move_id
        self.activity_update()

        return moves

    def _prepare_bills_vals(self):
        vals = super()._prepare_bills_vals()

        if self.vendor_id:
            vals['partner_id'] = self.vendor_id.id

        return vals