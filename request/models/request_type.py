from odoo import api, models, fields
from odoo.exceptions import ValidationError

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

    @api.constrains('is_late','is_early')
    def _check_request_type(self):
        for rec in self:
            if rec.is_late and rec.is_early:
                raise ValidationError(
                    "You cannot select both Late Login and Early Exit."
                )