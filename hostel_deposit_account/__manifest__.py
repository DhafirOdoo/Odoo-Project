{
    'name': 'Hostel Deposit Account',
    'version': '17.0.1.0.0',
    'depends': ['dev_hostel_management'],
    'installable': True,
    'summary': "Default Deposit Account for Hostel Deposit Payments From Customers",
    'author':"Dhafir Technologies",
    'data': [
        'views/hostel_settings_view.xml',
        'wizard/create_deposit_wizard_view_inherit.xml',
    ]
}