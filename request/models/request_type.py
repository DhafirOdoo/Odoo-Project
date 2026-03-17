from odoo import models, fields

class RequestType(models.Model):
    _name = 'request.type'
    _description = 'Request Type'
    _rec_name = 'request_name'


    request_name = fields.Char(string='Request Name', required=True)
    approver_id = fields.Many2one(
        'hr.employee',
        string='Approver',
        required=True
    )
    is_late = fields.Boolean(string='Is Late Login')
    is_early = fields.Boolean(string='Is Early Exit')