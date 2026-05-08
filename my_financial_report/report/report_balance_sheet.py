from odoo import api,fields,models



class ReportBalanceSheet(models.AbstractModel):
    _name = 'report.my_financial_report.balance_sheet_template'

    def _get_report_values(self, docids, data=None):
        wizard = self.env['balance.sheet.report'].browse(docids)
        date_from = wizard.date_from
        date_to = wizard.date_to

        move_filter = ""
        if wizard.target_move == 'posted':
            move_filter= "AND l.parent_state = 'posted'"

        query = f"""
            SELECT 
                a.account_type,
                a.name->>'en_US' AS name,
                SUM(l.debit) AS debit,
                SUM(l.credit) AS credit,
                SUM(l.debit - l.credit) AS balance
            FROM account_account a
            JOIN account_move_line l ON l.account_id = a.id
            WHERE a.account_type IN ('asset_cash','asset_receivable','asset_current','asset_non_current','asset_fixed','asset_prepayments')
            AND l.date BETWEEN %s AND %s
            {move_filter}
            GROUP BY a.account_type, a.name
            ORDER BY a.account_type, a.name
        """

        self.env.cr.execute(query, (date_from, date_to))
        assets = self.env.cr.dictfetchall()

        if wizard.only_with_balance:
            assets = [a for a in assets if a['balance'] != 0]

        grouped_assets = {}
        for row in assets:
            acc_type = row['account_type']

            if acc_type not in grouped_assets:
                grouped_assets[acc_type] = []

            grouped_assets[acc_type].append({
                'name': row['name'],
                'debit': row['debit'],
                'credit': row['credit'],
                'balance': row['balance'],
            })
        type_map = {
            'asset_fixed': 'Fixed Assets',
            'asset_current': 'Current Assets',
            'asset_non_current': 'Non-Current Assets',
            'asset_cash': 'Bank And Cash',
            'asset_receivable': 'Receivables',
            'asset_prepayments': 'Prepayments'
        }
        final_assets = []

        for key in type_map:
            if key in grouped_assets:
                final_assets.append({
                    'type': type_map[key],
                    'accounts': grouped_assets[key]
                })

        for group in final_assets:
            group['total'] = sum(acc['balance'] or 0 for acc in group['accounts'])


        query = f"""
            SELECT 
            a.account_type,
            a.name->>'en_US' AS name,
            SUM(l.debit) AS debit,
            SUM(l.credit) AS credit,
            SUM(l.credit - l.debit) AS balance
            FROM account_account a
            JOIN account_move_line l ON l.account_id = a.id
            JOIN account_move m ON l.move_id = m.id
            WHERE a.account_type IN ('liability_current', 'liability_non_current','liability_payable','liability_credit_card')
            AND l.date BETWEEN %s AND %s
            {move_filter}
            GROUP BY a.account_type, a.name
            ORDER BY a.account_type, a.name
        """
        self.env.cr.execute(query, (date_from, date_to))
        liabilities = self.env.cr.dictfetchall()

        if wizard.only_with_balance:
            liabilities = [a for a in liabilities if a['balance'] != 0]

        grouped_liabilities = {}
        for row in liabilities:
            acc_type = row['account_type']

            if acc_type not in grouped_liabilities:
                grouped_liabilities[acc_type] = []

            grouped_liabilities[acc_type].append({
                'name': row['name'],
                'debit': row['debit'],
                'credit': row['credit'],
                'balance': row['balance'],
            })
        type_map = {
            'liability_current': 'Current Liabilities',
            'liability_non_current': 'Non-Current Liabilities',
            'liability_payable': 'Payables',
            'liability_credit_card': 'Credit Cards',
        }
        final_liabilities = []

        for key in type_map:
            if key in grouped_liabilities:
                final_liabilities.append({
                    'type': type_map[key],
                    'accounts': grouped_liabilities[key]
                })

        for group in final_liabilities:
            group['total'] = sum(acc['balance'] or 0 for acc in group['accounts'])

        query = f"""
                SELECT 
                a.account_type,
                a.name->>'en_US' AS name,
                SUM(l.debit) AS debit,
                SUM(l.credit) AS credit,
                SUM(l.credit - l.debit) AS balance
                FROM account_account a
                JOIN account_move_line l ON l.account_id = a.id
                WHERE a.account_type IN ('equity', 'equity_unaffected')
                AND l.date BETWEEN %s AND %s
                {move_filter}
                GROUP BY a.account_type, a.name
                ORDER BY a.account_type, a.name
            """

        self.env.cr.execute(query, (date_from, date_to))
        equity = self.env.cr.dictfetchall()

        if wizard.only_with_balance:
            equity = [a for a in equity if a['balance'] != 0]

        grouped_equity = {}
        for row in equity:
            acc_type = row['account_type']

            if acc_type not in grouped_equity:
                grouped_equity[acc_type] = []

            grouped_equity[acc_type].append({
                'name': row['name'],
                'debit': row['debit'],
                'credit': row['credit'],
                'balance': row['balance'],
            })
        type_map = {
            'equity': 'Equity',
            'equity_unaffected': 'Current Year Earnings',
        }
        final_equity = []

        for key in type_map:
            if key in grouped_equity:
                final_equity.append({
                    'type': type_map[key],
                    'accounts': grouped_equity[key]
                })

        for group in final_equity:
            group['total'] = sum(acc['balance'] or 0 for acc in group['accounts'])



        self.env.cr.execute("""
            SELECT 
                SUM(l.credit - l.debit) AS balance
            FROM account_move_line l
            JOIN account_account a ON l.account_id = a.id
            WHERE a.account_type IN ('income','income_other' ,'expense')
            AND l.date BETWEEN %s AND %s
            AND l.parent_state = 'posted'
        """, (date_from,date_to,))

        pl_result = self.env.cr.fetchone()
        profit_loss = pl_result[0] or 0

        total_assets = sum(a['balance'] or 0 for a in assets)
        total_liabilities = sum(l['balance'] or 0 for l in liabilities)
        total_equity = sum(e['balance'] or 0 for e in equity)
        total_liabilities_final = (
                total_liabilities +
                total_equity +
                profit_loss
        )

        return {
            'docs': wizard,
            'final_assets': final_assets,
            'final_liabilities': final_liabilities,
            'final_equity': final_equity,
            'profit_loss': profit_loss,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'total_liabilities_final': total_liabilities_final,
            'show_debit_credit': wizard.show_debit_credit

        }

# class ReportBalanceSheetPdf(models.AbstractModel):
#     _name = 'report.my_financial_report.balance_sheet_pdf_template'
#     _inherit = 'report.my_financial_report.balance_sheet_template'
#
#     def _get_report_values(self, docids, data=None):
#         res = super()._get_report_values(docids, data)
#
#         return res

