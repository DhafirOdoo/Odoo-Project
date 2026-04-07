from odoo import fields, models

class DailyReportLine(models.Model):
    _name = 'daily.report.line'
    _description = 'Daily Report Line'
    _rec_name = 'activity_id'

    daily_report_id = fields.Many2one('daily.report', string='Daily Report')
    activity_id = fields.Many2one('daily.activity', string='Activity', required=True)
    count = fields.Integer(string='Count', default=1, required=True)
    work_time = fields.Float(string='Work Time', default=1, required=True)


