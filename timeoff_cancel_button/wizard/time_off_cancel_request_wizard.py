from odoo import fields, models
from odoo.exceptions import ValidationError


class TimeoffCancelRequest(models.TransientModel):
    _name = 'timeoff.cancel.request.wizard'
    _description = 'Timeoff Cancel Request'

    reason = fields.Text(required=True)
    leave_id = fields.Many2one('hr.leave', required=True)


    def request_submit(self):
        for rec in self:
            if not rec.reason:
                raise ValidationError("Please enter a reason.")

            leave = rec.leave_id

            leave.sudo().write({
                'cancel_requested': True,
                'cancel_reason': rec.reason,
            })



        # group = self.env.ref('timeoff_cancel_button.group_timeoff_cancel_user', raise_if_not_found=False)
        # partners = group.users.mapped('partner_id') if group else self.env['res.partner']
        #
        # if partners:
            manager_user = leave.employee_id.leave_manager_id
            if manager_user:
                self.env['mail.activity'].sudo().create({
                    'res_id': leave.id,
                    'res_model_id': self.env['ir.model']._get(leave._name).id,
                    'user_id': manager_user.id,
                    'summary': 'Time Off Cancellation Request',
                    'note': f'Cancellation Reason: {rec.reason}',
                    'activity_type_id': self.env.ref('timeoff_cancel_button.mail_activity_type_cancellation').id,
                    'date_deadline': fields.Date.today(),
                })

            template = self.env.ref('timeoff_cancel_button.time_off_cancel_request_template')

            template.sudo().send_mail(
                leave.id,
                # email_values={
                #     'recipient_ids': [(6, 0, partners.ids)],
                # },
                force_send=True
            )


        return {'type': 'ir.actions.act_window_close'}


