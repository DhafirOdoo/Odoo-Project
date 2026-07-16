from odoo import api, fields,models


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'


    can_edit = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        template = self.env.ref('timeoff_mail_template.allocation_request_mail')
        for record in records:
            if record.state == 'confirm' and record.allocation_type == 'regular':
                template.send_mail(record.id, force_send=True)
                record.can_edit = False
        return records