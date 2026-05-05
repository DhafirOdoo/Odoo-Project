from odoo import api,fields,models



class BalanceSheetReport(models.TransientModel):
    _name = 'balance.sheet.report'
    _description = "Balance Sheet Report"


    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    only_with_balance = fields.Boolean('Entries With Balance')
    target_move = fields.Selection([
        ('posted', 'Posted Entries'),
        ('all', 'All Entries')
    ], default='posted', string="Target Moves")
    show_debit_credit = fields.Boolean(string="Show Debit & Credit Columns")


    # def action_print_report(self):
    #
    #     return self.env.ref('my_financial_report.balance_sheet_pdf_report_action').report_action(self)


    def action_view_report(self):

        return self.env.ref('my_financial_report.balance_sheet_report_action').report_action(self)


    def action_xlsx_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

        return self.env.ref('my_financial_report.balance_sheet_xlsx_report_action').report_action(self, data=data)