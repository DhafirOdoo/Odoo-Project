{
    'name': 'Employee Request',
    'version': '17.0.1.0.0',
    'depends': ['base', 'mail', 'hr'],
    'summary':'Employee Can Submit Various Requests',
    'author':'Dhafir Technologies',
    'installable': True,
    'application': True,
    'data': [
        'security/request_groups.xml',
        'security/request_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'views/employee_request_view.xml',
        'views/request_type_view.xml',
        'views/request_menus.xml'
    ]

}
