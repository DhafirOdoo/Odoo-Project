from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_count = fields.Integer(
        string="Payments",
        compute="_compute_payment_count"
    )

    def _get_reconciled_payments(self):
        payments = self.env['account.payment']
        for move in self:
            reconciled_lines = move.line_ids.mapped('matched_debit_ids.debit_move_id.move_id') | \
                               move.line_ids.mapped('matched_credit_ids.credit_move_id.move_id')
            payments |= reconciled_lines.filtered(lambda m: m.payment_id).mapped('payment_id')
        return payments

    def _compute_payment_count(self):
        for move in self:
            payments = move._get_reconciled_payments()
            move.payment_count = len(payments)

    def action_view_payments(self):
        self.ensure_one()
        payments = self._get_reconciled_payments()
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments.ids)],
        }