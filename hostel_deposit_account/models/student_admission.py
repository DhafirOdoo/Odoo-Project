from odoo import fields,models, _
from odoo.exceptions import ValidationError


class StudentAdmission(models.Model):
    _inherit = 'dev.student.admission'

    # Updated compute method to find liability deposits
    def compute_credit_deposit_count(self):
        for rec in self:
            # We search by admission_id link and payment type ONLY
            records = self.env['account.payment'].search([
                ('admission_id', '=', rec.id),
                ('payment_type', '=', 'inbound'),
                ('state', '!=', 'cancel')
            ])
            rec.credit_deposit_count = len(records)

    # Updated view method to display the found deposits
    def view_credit_deposit(self):
        records = self.env['account.payment'].search([
            ('admission_id', '=', self.id),
            ('payment_type', '=', 'inbound')
        ])

        action = self.env.ref('account.action_account_payments').sudo().read()[0]
        if len(records) > 1:
            action['domain'] = [('id', 'in', records.ids)]
        elif len(records) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = records.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    #Updated deposit refund method in hostel
    def return_deposit(self):
        if not self.env.company.deposit_journal_id:
            raise ValidationError(_("Please configure deposit journal in configuration"))
        records = self.env['account.payment'].search(
            [('partner_id', '=', self.student_id.id), ('payment_type', '=', 'inbound'), ('admission_id', '=', self.id)])
        if not records:
            raise ValidationError(_("Please credit some amount first."))

        for record in records:
            vals = {
                'payment_type': 'outbound',
                'journal_id': self.env.company.deposit_journal_id and self.env.company.deposit_journal_id.id,
                'amount': record.amount,
                'date': fields.Date.today(),
                'partner_id': record.partner_id and record.partner_id.id or False,
                'ref': f"Admission : {self.admission_number} - Deposit",
                'partner_type': 'supplier',
                'destination_account_id': self.env.company.hostel_deposit_account_id.id,
                'admission_id': record.admission_id.id,
            }
            return_payment = self.env['account.payment'].create(vals)
            self.deposit_refunded = True
            return True