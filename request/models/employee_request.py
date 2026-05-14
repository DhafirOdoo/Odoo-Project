from docutils.nodes import option

from odoo import api, fields, models
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
                ('status', '=', 'approved'),
            ]
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
