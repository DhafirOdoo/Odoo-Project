{
    'name': 'General Ledger Account Filter',
    'depends': ['account','base','base_accounting_kit'],
    'summary': 'Enable Account Filter for General Ledger Report',
    'installable': True,
    'application': True,
    'data': [
        'views/general_ledger_account_filter_views.xml',
    ]
}