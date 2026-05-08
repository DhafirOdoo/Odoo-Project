from odoo import api,fields, models



class BalanceSheetXlsx(models.AbstractModel):
    _name = 'report.my_financial_report.balance_sheet_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, docs):

        sheet = workbook.add_worksheet('Balance Sheet')

        # Formats
        right = workbook.add_format({'align': 'right', 'bg_color': '#f2f2f2'})
        group_total = workbook.add_format({'align': 'right', 'bold': True, 'bg_color': '#bcbcbc'})
        profit_loss_total = workbook.add_format({'bold': True, 'bg_color': '#999999'})
        main = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#bcbcbc',
                                       'font_size': 20})
        date_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#bcbcbc',
                                       })
        header = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                      'bg_color': '#999999', 'font_size': 17})
        sub_header = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                      'bg_color': '#999999'})
        balance_sheet = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                      'bg_color': '#999999'})
        group = workbook.add_format({'bold': True, 'bg_color': '#bcbcbc'})
        normal = workbook.add_format({'bg_color': '#f2f2f2'})
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 11, 30)
        sheet.set_row(1,30)
        sheet.set_row(3, 20)
        # Get report data (REUSE SQL LOGIC)
        report = self.env['report.my_financial_report.balance_sheet_template']
        report_data = report._get_report_values(docs.ids, data)
        wizard = report_data['docs']
        date_from = wizard.date_from
        date_to  = wizard.date_to
        show_dc = report_data.get('show_debit_credit')

        assets = report_data['final_assets']
        liabilities = report_data['final_liabilities']
        equity = report_data['final_equity']
        profit_loss = report_data['profit_loss']
        asset_total = report_data['total_assets']
        liabilities_total = report_data['total_liabilities']
        equity_total = report_data['total_equity']
        total_liabilities_final  =report_data['total_liabilities_final']


        sheet.merge_range('B2:E2', 'Balance Sheet', main)
        sheet.merge_range('B3:C3', f'From: {date_from}', date_format)
        sheet.merge_range('D3:E3', f'To: {date_to}', date_format)
        sheet.merge_range('B4:E4','' ,date_format )

        # Headers
        sheet.merge_range('B5:C5', 'Liabilities', header)
        sheet.merge_range('D5:E5', 'Assets', header)
        sheet.merge_range('B7:C7', 'Equity', sub_header)

        row = 6

        left_row = row
        right_row = row

        # ------------------------
        #  LEFT SIDE (LIABILITIES)
        # ------------------------

        left_row += 1

        for group_data in equity:
            sheet.write(left_row, 1, group_data['type'], group)
            sheet.write(left_row, 2, group_data['total'], group_total)
            left_row += 1

            for line in group_data['accounts']:
                sheet.write(left_row, 1, line['name'], normal)
                sheet.write(left_row, 2, line['balance'], right)
                left_row += 1

        sheet.write(left_row, 1, 'Total Equity', group)
        sheet.write(left_row, 2, equity_total, group_total)
        left_row += 1

        # Profit & Loss
        sheet.write(left_row, 1, 'Profit & Loss Account', profit_loss_total)
        sheet.write(left_row, 2, profit_loss, profit_loss_total)
        left_row += 1

        # Liabilities
        for group_data in liabilities:
            sheet.write(left_row, 1, group_data['type'], group)
            sheet.write(left_row, 2, group_data['total'], group_total)
            left_row += 1

            for line in group_data['accounts']:
                sheet.write(left_row, 1, line['name'], normal)
                sheet.write(left_row, 2, line['balance'], right)
                left_row += 1

        sheet.write(left_row, 1, 'Total Liabilities', group)
        sheet.write(left_row, 2, liabilities_total, group_total)
        left_row += 1

        # ------------------------
        # RIGHT SIDE (ASSETS)
        # ------------------------

        for group_data in assets:
            sheet.write(right_row, 3, group_data['type'], group)
            sheet.write(right_row, 4, group_data['total'], group_total)
            right_row += 1

            for line in group_data['accounts']:
                sheet.write(right_row, 3, line['name'], normal)
                sheet.write(right_row, 4, line['balance'], right)
                right_row += 1

        final_row = max(left_row, right_row)
        sheet.set_row(final_row, 20)
        sheet.write(final_row, 1, 'Total Liabilities + Equity', balance_sheet)
        sheet.write(final_row, 2, total_liabilities_final, balance_sheet)

        sheet.write(final_row, 3, 'Total Assets', balance_sheet)
        sheet.write(final_row, 4, asset_total, balance_sheet)

