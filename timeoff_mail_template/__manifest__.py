{
    'name': 'Custom Time Off Mail Template',
    'version': '17.0.1.0.1',
    'depends': ['mail', 'hr_holidays'],
    'installable': True,
    'author': 'Dhafir Technologies',
    'summary': 'Custom Mail Template For Leave Request E-mail',
    'data': [
        'data/mail_template_data.xml',
        'data/allocation_mail_template_data.xml',
        'views/timeoff_form_view_inherit.xml',
        'views/hr_leave_allocation_form.xml',
    ],

}
