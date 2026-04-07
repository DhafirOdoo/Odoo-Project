from odoo import models, _
from odoo.exceptions import ValidationError

class CreateDepositWizard(models.TransientModel):
    _inherit = 'create.deposit'


    def create_deposit(self):
        active_ids = self._context.get('active_ids')
        student_admission = self.env['dev.student.admission'].browse(active_ids)
        company = self.env.company

        if not company.deposit_journal_id:
            raise ValidationError(_("Please configure deposit journal in configuration"))
        if not company.hostel_deposit_account_id:
            raise ValidationError(_("Please configure deposit account in configuration"))
        vals = {
            'payment_type': 'inbound',
            'journal_id': self.env.company.deposit_journal_id and self.env.company.deposit_journal_id.id,
            'amount': self.amount,
            'date': student_admission.admission_date,
            'partner_id': student_admission.student_id and student_admission.student_id.id or False,
            'partner_type': 'customer',
            'ref': f"Admission : {student_admission.admission_number} - Deposit",
            'destination_account_id': self.env.company.hostel_deposit_account_id.id,
            'admission_id': student_admission.id,

        }

        payment = self.env['account.payment'].create(vals)
        student_admission.deposit_created = True
        return True

