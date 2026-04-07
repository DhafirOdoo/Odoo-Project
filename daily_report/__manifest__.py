{
    'name': 'Daily Report',
    'version': '17.0.1.0.0',
    'depends': ['base','hr','mail'],
    'installable': True,
    'application': True,
    'summary': 'Employee Daily Work Report Submission',
    'author':'Dhafir Technologies',
    'data': [
        'security/daily_report_groups.xml',
        'security/daily_report_security.xml',
        'security/ir.model.access.csv',
        'views/daily_report_view.xml',
        'views/daily_activity_view.xml',
        'views/daily_report_menus.xml',
    ]
}