{
    'name': 'Employee Request',
    'depends': ['base', 'mail', 'hr'],
    'summary':'Employee can submit requests',
    'author':'Dhafir Technologies',
    'installable': True,
    'application': True,
    'data': [
        'security/request_groups.xml',
        'security/request_security.xml',
        'security/ir.model.access.csv',
        'views/employee_request_view.xml',
        'views/request_type_view.xml',
        'views/request_menus.xml'
    ]

}
