from odoo import http
from odoo.http import request


class LeaveActionController(http.Controller):

    @http.route('/leave/approve/<int:leave_id>', type='http', auth='user')
    def approve_leave(self, leave_id, **kwargs):
        leave = request.env['hr.leave'].sudo().browse(leave_id)

        if leave.exists():
            leave.action_approve()


        return request.redirect(
            f'/web#id={leave.id}&model=hr.leave&view_type=form'
        )

    @http.route('/leave/refuse/<int:leave_id>', type='http', auth='user')
    def refuse_leave(self, leave_id, **kwargs):
        leave = request.env['hr.leave'].sudo().browse(leave_id)

        if leave.exists():
            leave.action_refuse()

        return request.redirect(
            f'/web#id={leave.id}&model=hr.leave&view_type=form'
        )