from odoo import models, api


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'



    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        template = self.env.ref('timeoff_mail_template.time_off_request_mail')

        for rec in records:
            if rec.state == 'confirm':
                template.send_mail(rec.id, force_send=True)

        return records

    def action_approve(self, check_state=True):
        res = super().action_approve(check_state=check_state)
        records = self.filtered(lambda rec: rec.state == 'validate1')
        template = self.env.ref('timeoff_mail_template.time_off_second_approve')

        for rec in records:
            exclude_users = rec.employee_id.leave_manager_id
            officers = rec.holiday_status_id.responsible_ids - exclude_users

            for officer in officers:
                email = officer.work_email
                template.with_context(
                    officer_name=officer.name
                ).send_mail(
                    rec.id,
                    force_send=True,
                    email_values={'email_to': email}
                )

        return res