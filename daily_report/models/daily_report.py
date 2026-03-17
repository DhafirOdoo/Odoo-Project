from odoo import fields, models
from odoo.exceptions import UserError


class DailyReport(models.Model):
    _name = 'daily.report'
    _description = 'Daily Report'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env.user.employee_id.id,
        readonly=True,
        required=True
    )
    report_date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=True,
        tracking=True
    )
    line_ids = fields.One2many(
        'daily.report.line',
        'daily_report_id',
        string='Lines',
        required=True,
        tracking=True
    )
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ],
    default='draft',
    tracking=True
    )


    def button_submit(self):
        for rec in self:
            if not rec.line_ids:
                 raise UserError('Add At Least One Work Activity.')

            rec.status = 'submitted'

    def button_reset(self):
        for rec in self:
            rec.status = 'draft'