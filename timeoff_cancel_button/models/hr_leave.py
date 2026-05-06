from odoo import api, fields, models
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    cancel_requested = fields.Boolean(default=False)
    cancel_reason = fields.Text('Cancellation Reason')
    is_current_user = fields.Boolean(compute='_compute_is_current_user')


    def _compute_is_current_user(self):
        for rec in self:
            rec.is_current_user = rec.user_id == self.env.user

    @api.depends_context('uid')
    @api.depends('state', 'employee_id', 'date_from')
    def _compute_can_cancel(self):
        now = fields.Datetime.now().date()
        user = self.env.user

        is_officer = user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = user.has_group('hr_holidays.group_hr_holidays_manager')

        for leave in self:
            is_owner = leave.employee_id.user_id == user
            leave.can_cancel = (
                    leave.id
                    and leave.state in ['validate', 'validate1']
                    and leave.date_from
                    and leave.date_from.date() >= now
                    and (is_officer or is_manager or is_owner)
            )

    def action_cancel(self):
        self.ensure_one()

        return {
            'name': 'Cancel Request',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model':'timeoff.cancel.request.wizard',
            'view_mode':'form',
            'context': {
                'default_leave_id': self.id
            }
            
        }

    def _force_cancel(self, cancel_reason, msg_subtype='mail.mt_comment'):
        recs = self.browse() if self.env.context.get(MODULE_UNINSTALL_FLAG) else self
        template = self.env.ref('timeoff_cancel_button.time_off_cancel_request_template')
        for leave in recs:
            leave.message_post(
                body= f'The time off has been canceled: {cancel_reason}',
                subtype_xmlid=msg_subtype
            )



        leave_sudo = self.sudo()
        leave_sudo.with_context(from_cancel_wizard=True).active = False
        leave_sudo.meeting_id.active = False
        leave_sudo._remove_resource_leave()

    def manager_cancel(self):
        self.ensure_one()

        self._action_user_cancel(self.cancel_reason)
        self.cancel_requested = False
