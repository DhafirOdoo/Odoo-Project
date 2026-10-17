from odoo import api, fields, models



class EmployeeRequestCompensate(models.Model):
    _name = 'employee.request.compensate'
    _description = 'Employee Request Compensate'


    date = fields.Date(string='Compensated Date')
    from_time = fields.Float(string='From Time')
    to_time = fields.Float(string='To Time')
    total_compensated = fields.Float(string='Total Compensated', compute='_compute_total_compensated')
    employee_request_id = fields.Many2one('employee.request')


    @api.depends('from_time', 'to_time')
    def _compute_total_compensated(self):
        for rec in self:
            if rec.to_time or rec.from_time:
                rec.total_compensated = rec.to_time - rec.from_time
            else:
                rec.total_compensated = 0.0