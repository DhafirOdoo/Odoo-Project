from odoo import models, api


class GeneralLedgerAccountFilterReport(models.AbstractModel):
    _inherit = 'report.base_accounting_kit.report_general_ledger'

    @api.model
    def _get_report_values(self, docids, data=None):
        result = super()._get_report_values(docids, data=data)

        wizard = self.env[self.env.context.get('active_model')].browse(
            self.env.context.get('active_ids', [])
        )

        if wizard.account_ids:
            accounts = wizard.account_ids

            init_balance = data['form'].get('initial_balance', True)
            sortby = data['form'].get('sortby', 'sort_date')
            display_account = data['form']['display_account']

            accounts_res = self.with_context(
                data['form'].get('used_context', {})
            )._get_account_move_entry(
                accounts, init_balance, sortby, display_account
            )

            result['Accounts'] = accounts_res

        return result
