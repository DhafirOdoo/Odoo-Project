# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # ---------------------------------------------------------------
    # Override the method that sends the default confirmation mail
    # when a time off request is created / submitted.
    # ---------------------------------------------------------------

    def _notify_manager(self):
        """
        Completely suppress the default manager-notification e-mail
        that Odoo sends on time-off creation, and send our own custom
        template instead.

        The standard method is defined in hr_holidays/models/hr_leave.py
        and typically calls message_post() or action_notify().
        We override it here to do nothing (effectively blocking it).
        """
        # Do NOT call super() — this stops the default mail.
        return True

    # ---------------------------------------------------------------
    # Hook into the 'confirm' action so we can fire our custom mail
    # right after the leave is confirmed/submitted.
    # ---------------------------------------------------------------

    def action_confirm(self):
        """
        Override action_confirm to:
        1. Run the standard confirmation logic (state changes, activity, etc.)
        2. Skip the default notification e-mail.
        3. Send our own custom e-mail template.
        """
        # Call super() to allow state transitions and activity creation,
        # but the _notify_manager override above will block the default mail.
        result = super().action_confirm()

        # Send our custom mail for every leave that just got confirmed.
        self._send_custom_timeoff_mail()

        return result

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------

    def _send_custom_timeoff_mail(self):
        """
        Find and send the custom e-mail template for each leave record.
        """
        template = self.env.ref(
            'custom_timeoff_mail.email_template_custom_timeoff',
            raise_if_not_found=False,
        )
        if not template:
            _logger.warning(
                'custom_timeoff_mail: email template not found. '
                'Make sure data/email_template.xml is installed correctly.'
            )
            return

        for leave in self:
            try:
                template.send_mail(leave.id, force_send=True)
                _logger.info(
                    'Custom time-off mail sent for leave %s (employee: %s)',
                    leave.name,
                    leave.employee_id.name,
                )
            except Exception as exc:
                _logger.error(
                    'Failed to send custom time-off mail for leave %s: %s',
                    leave.name,
                    exc,
                )


    def action_send_custom_mail_manual(self):
        """
        Button action: manually re-send the custom time-off notification.
        Accessible from the form view (HR Managers only).
        """
        self._send_custom_timeoff_mail()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Email Sent',
                'message': 'Custom time-off notification sent successfully.',
                'sticky': False,
                'type': 'success',
            },
        }


class HrLeaveAllocation(models.Model):
    """
    Optional: if you also want to suppress/replace mails on Allocation
    records, uncomment and adapt the block below.
    """
    _inherit = 'hr.leave.allocation'

    # def action_confirm(self):
    #     result = super().action_confirm()
    #     # send custom allocation mail here if needed
    #     return result
