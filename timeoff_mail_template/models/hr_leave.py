from odoo import fields, models, api
from odoo.exceptions import UserError


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'


    is_request_submitted = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        template = self.env.ref('timeoff_mail_template.time_off_request_mail')

        for rec in records:
            if rec.state == 'confirm':
                template.send_mail(rec.id, force_send=True)
                rec.is_request_submitted = True

                # rec.with_context(
                #     skip_leave_security=True
                # ).write({
                #     'is_request_submitted': True
                # })

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


    def write(self, values):
        if 'active' in values and not self.env.context.get('from_cancel_wizard'):
            raise UserError("You can't manually archive/unarchive a time off.")

        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.is_superuser()
        if not is_officer and values.keys() - {'attachment_ids', 'supported_attachment_ids', 'message_main_attachment_id', 'is_request_submitted'}:
            if any(hol.date_from.date() < fields.Date.today() and hol.employee_id.leave_manager_id != self.env.user
                   and hol.state not in ('confirm', 'draft') for hol in self):
                raise UserError('You must have manager rights to modify/validate a time off that already begun')

        # Unlink existing resource.calendar.leaves for validated time off
        if 'state' in values and values['state'] != 'validate':
            validated_leaves = self.filtered(lambda l: l.state == 'validate')
            validated_leaves._remove_resource_leave()

        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create'):
            if values.get('state'):
                self._check_approval_update(values['state'])
                if any(holiday.validation_type == 'both' for holiday in self):
                    if values.get('employee_id'):
                        employees = self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees = self.mapped('employee_id')
                    self._check_double_validation_rules(employees, values['state'])
            if 'date_from' in values:
                values['request_date_from'] = values['date_from']
            if 'date_to' in values:
                values['request_date_to'] = values['date_to']
        result = super(HolidaysRequest, self).write(values)
        if any(field in values for field in ['request_date_from', 'date_from', 'request_date_from', 'date_to', 'holiday_status_id', 'employee_id', 'state']):
            self._check_validity()
        if not self.env.context.get('leave_fast_create'):
            for holiday in self:
                if employee_id:
                    holiday.add_follower(employee_id)

        return result