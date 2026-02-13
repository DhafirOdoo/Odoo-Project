{
    'name': 'General Ledger Account Filter',
    'depends': ['account','base','base_accounting_kit'],
    'summary': 'Account Filter for General Ledger Report',
    'installable': True,
    'application': True,
    'summary': 'Enable General Ledger Account Filter',
    'data': [
        'views/general_ledger_account_filter_views.xml',
    ]
}