# -*- coding: utf-8 -*-
{
    'name': 'Custom Time Off Mail',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Override default time off email with custom mail template',
    'description': """
        This module overrides the default email sent when a time off request
        is created in Odoo 17 Community. It suppresses the standard notification
        and sends a custom email template instead.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['hr_holidays'],
    'data': [
        'data/email_template.xml',
        'views/hr_leave_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
