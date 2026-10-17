from dateutil.rrule import weekday
from docutils.nodes import option

from odoo import api, fields, models
from odoo.api import onchange
from odoo.exceptions import UserError


class EmployeeRequest(models.Model):
    _name = 'employee.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Request'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env.user.employee_id,
        required=True, readonly=True)
    user_id = fields.Many2one(related='employee_id.user_id')
    req_reason = fields.Text(string='Description')
    login_date_time = fields.Date(
        string='Date',
        required=True,
        default=lambda self: fields.Date.today()
    )
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('compensated', 'Compensated'),
        ('rejected', 'Rejected'),
    ], default='draft')
    request_type_id = fields.Many2one(
        'request.type',
        string="Request Type",
        required=True,
    )
    approver_id = fields.Many2one(related='request_type_id.approver_id')
    previous_request_ids = fields.Many2many(
        'employee.request',
        string="Previous Approved Requests",
        compute='_compute_previous_requests',
        store=False
    )
    late_time = fields.Float(string='Late Login Time')
    early_time = fields.Float(string='Early Exit Time')
    is_late = fields.Boolean(
        related='request_type_id.is_late',
        store=False
    )
    is_early = fields.Boolean(
        related='request_type_id.is_early',
        store=False
    )
    login_reason = fields.Text(string='Reason')
    display_note = fields.Text(
        string="Reason/Description",
        compute="_compute_display_note"
    )
    compensate_date = fields.Date(
        'Compensated On'
    )# Deprecated
    from_time = fields.Float(string='From')# Deprecated
    to_time = fields.Float(string='To')# Deprecated
    late_duration = fields.Float('Late Duration', compute='_compute_late_duration', readonly=True)
    early_duration = fields.Float('Duration', compute='_compute_early_duration', readonly=True)
    compensate_duration = fields.Float('Compensate Duration', compute='_compute_compensate_duration',
                                       readonly=True, store=True)# Deprecated
    display_time = fields.Float(string="Login/Exit Time", compute="_compute_display_time")
    day_period = fields.Selection([
        ('morning','Morning'),
        ('afternoon','Afternoon'),
    ])
    compensate_line_ids = fields.One2many('employee.request.compensate','employee_request_id')
    total_compensated = fields.Float(
        string='Total Compensated',
        compute='_compute_total_compensated',
    )
    is_request_admin = fields.Boolean(compute='_compute_is_request_admin')

    @api.depends('req_reason', 'login_reason')
    def _compute_display_note(self):
        for rec in self:
            if rec.req_reason:
                rec.display_note = rec.req_reason
            else:
                rec.display_note = rec.login_reason

    @api.depends('employee_id')
    def _compute_previous_requests(self):
        for rec in self:
            if not rec.employee_id:
                rec.previous_request_ids = False
                continue
            domain = [
                ('employee_id', '=', rec.employee_id.id),
                ('status', 'in', ['approved', 'compensated']),
            ]
            if rec.is_early or rec.is_late:
                domain += [
                    '|',
                    ('is_late', '=', True),
                    ('is_early', '=', True),
                ]
            elif rec.request_type_id:
                domain.append(
                    ('request_type_id', '=', rec.request_type_id.id)
                )
            else:
                rec.previous_request_ids = False
                continue

            if rec._origin.id:
                domain.append(('id', '<', rec._origin.id))

            previous = self.env['employee.request'].search(
                domain,
                order="id desc"
            )

            rec.previous_request_ids = previous


    def button_submit(self):
        template = self.env.ref('request.employee_request_approver_mail')
        for rec in self:
            if rec.is_late:
                if rec.late_time <= 0:
                    raise UserError("Please set late login time")
            elif rec.is_early:
                if rec.early_time <= 0:
                    raise UserError("Please set early login time")
            rec.status = 'submitted'

            rec.message_post(
                body=f"{rec.request_type_id.request_name} has been submitted by {rec.employee_id.name}."
            )
            template.send_mail(rec.id, force_send=True)

            rec.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=rec.approver_id.user_id.id,
            )

    def button_approve(self):
        for rec in self:
            rec.status = 'approved'

            rec.activity_feedback(['mail.mail_activity_data_todo'])

            requester_user = rec.employee_id.user_id
            if not requester_user:
                raise UserError("Requester employee has no linked user")

            rec.message_subscribe(partner_ids=[requester_user.partner_id.id])

            rec.message_post(
                body=f"Your {rec.request_type_id.request_name} has been approved.",
                partner_ids=[requester_user.partner_id.id]
            )


    def button_reject(self):
        for rec in self:
            rec.status = 'rejected'

            rec.activity_feedback(['mail.mail_activity_data_todo'])

            requester_user = rec.employee_id.user_id
            if not requester_user:
                raise UserError("Requester employee has no linked user")

            rec.message_subscribe(partner_ids=[requester_user.partner_id.id])

            rec.message_post(
                body=f"Your {rec.request_type_id.request_name} has been rejected.",
                partner_ids=[requester_user.partner_id.id]
            )


    @onchange('late_time','day_period')
    def _compute_late_duration(self):
        for rec in self:
            rec.late_duration = 0.0
            calendar = rec.employee_id.resource_calendar_id

            if not calendar:
                continue

            weekday = str(rec.login_date_time.weekday())
            attendances = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)

            if not attendances:
                continue

            if rec.day_period == 'morning':
                attendance = attendances.sorted('hour_from')[0]
                scheduled_minutes = attendance.hour_from
                if rec.late_time:
                    rec.late_duration = rec.late_time - scheduled_minutes
            elif rec.day_period == 'afternoon':
                attendance = attendances.sorted('hour_from')[2]
                scheduled_minutes = attendance.hour_from
                if rec.late_time:
                    rec.late_duration = rec.late_time - scheduled_minutes + 12.00


    @api.onchange('early_time','day_period')
    def _compute_early_duration(self):
        for rec in self:
            rec.early_duration = 0.0
            calendar = rec.employee_id.resource_calendar_id

            if not calendar:
                continue

            weekday = str(rec.login_date_time.weekday())
            attendances = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)

            if not attendances:
                continue

            if rec.day_period == 'afternoon':
                attendance = attendances.sorted('hour_to')[2]
                scheduled_minutes = attendance.hour_to
                if rec.early_time:
                    rec.early_duration = scheduled_minutes - rec.early_time - 12.0
            elif rec.day_period == 'morning':
                attendance = attendances.sorted('hour_to')[0]
                scheduled_minutes = attendance.hour_to
                if rec.early_time:
                    rec.early_duration = scheduled_minutes - rec.early_time

    @api.ondelete(at_uninstall=False)
    def _user_record_deletion(self):
        if self.env.user.has_group('request.request_admin'):
            return

        if any(record.status in ['approved', 'compensated'] for record in self):
            raise UserError("You cannot delete an approved or compensated record.")

    @api.depends('late_time', 'early_time')
    def _compute_display_time(self):
        for rec in self:
            # Fallback logic: Use Field A if present, otherwise Field B, otherwise empty string
            rec.display_time = rec.late_time or rec.early_time or ""



    def add_compensatory_details(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Compensatory Details',
            'res_model': 'employee.request.compensate',
            'view_mode': 'tree',
            'view_id': self.env.ref('request.employee_request_compensate_tree').id,
            'target': 'new',
            'domain': [
                ('employee_request_id', '=', self.id),
            ],
            'context': {
                'default_employee_request_id': self.id,
            }
        }


    def button_compensated(self):
        #validates and changes status of the record
        for rec in self:
            compensation_records = self.env[
                'employee.request.compensate'
            ].search([
                ('employee_request_id', '=', rec.id),
            ])

            total_compensated = sum(
                compensation_records.mapped('total_compensated')
            )
            required_duration = rec.early_duration or rec.late_duration

            if required_duration and total_compensated < required_duration:
                raise UserError("Compensated time is not enough")

            else:
                rec.status = 'compensated'

    @api.depends('compensate_line_ids.total_compensated')
    def _compute_total_compensated(self):
        #sum total compensated time added by user
        for rec in self:
            rec.total_compensated = sum(
                rec.compensate_line_ids.mapped('total_compensated')
            )

    def _compute_is_request_admin(self):
        for record in self:
            # Checks if the current user belongs to your custom admin group
            record.is_request_admin = self.env.user.has_group('request.request_admin')