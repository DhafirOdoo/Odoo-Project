{
    'name': 'My Financial Report',
    'version': '1.0',
    'depends': ['account', 'sale', 'account_check_printing',
                'base_account_budget', 'analytic','base_accounting_kit','base','report_xlsx'],
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'wizard/balance_sheet_report_view.xml',
        'report/balance_sheet_report_template.xml',
        'report/report.xml',
    ]
}