{
    'name': 'Default Receivable Account',
    'depends': ['base','account','base_accounting_kit','base_account_budget'],
    'installable': True,
    'application': True,
    'data': [
        'views/res_config_settings_view.xml',
    ]
}