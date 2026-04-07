from odoo import fields, models

class DailyActivity(models.Model):
    _name = 'daily.activity'
    _description = 'Daily Activity'
    _rec_name = 'activity_name'

    activity_name = fields.Char(string='Activity Name', required=True)
