{
    'name': 'Time Off Cancel Request',
    'version': '17.0.1.0.0',
    'depends': ['base', 'hr'],
    'installable': True,
    'author': 'Dhafir Technologies',
    'summary': 'Time off Cancel Access to Admin Only',
    'data': [
        'data/time_off_cancel_request_mail_template.xml',
        'data/time_off_cancellation_activity_data.xml',
        'security/ir.model.access.csv',
        'security/timeoff_cancel_security.xml',
        'views/timeoff_cancel_button.xml',
        'wizard/time_off_cancel_request_wizard_view.xml',
        'views/timeoff_cancel_request_menu.xml'
    ]

}
