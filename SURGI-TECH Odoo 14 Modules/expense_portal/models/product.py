# -*- coding: utf-8 -*-
from odoo import models,fields, api,_
from odoo.exceptions import AccessError
import base64
from odoo.exceptions import UserError

class Product(models.Model):
    _inherit = 'product.product'

    def get_product_details(self):
        arr=[]
        arr.append(self.standard_price or 0)

        return arr


class Expencies(models.Model):
    _inherit = 'hr.expense'
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    def action_submit_expenses_custom(self):
        try:
            sheet = self._create_sheet_from_expenses()
            summary_name = "Summary Report: " + ", ".join(self.mapped('name'))
            sheet.sudo().write({'name': summary_name})  # Updating the name
            if sheet:
                return {
                    'success': True,
                    'name': sheet.name,
                    'message': _("New Expense Report Created"),
                }
        except UserError as e:
            return {
                'success': False,
                'message': str(e),
            }

    @api.model
    def create_expense_record(self, values):
        user = self.env.user
        if not user.expense_portal_access:
            raise AccessError("You do not have the necessary permissions.")

        print("vals",values)
        emp = self.env['hr.employee'].browse(self.env.user.employee_id.id)
        operation_type = self.env['operation.operation'].browse(int(values.get('sales_id'))) if values.get('sales_id') else False
        account = self.env['product.product'].sudo().browse(int(values.get('product')))

        com_list = [int(com) for com in values.get('analytic_tag_ids', [])]
        tax_list = [int(tax) for tax in values.get('tax_ids', [])]

        print(com_list, tax_list)
        expense = self.env['hr.expense'].sudo().create({
            'name': values.get('description'),
            'expense_type': values.get('expense_type'),
            'account_id': account.property_account_expense_id.id,
            'analytic_account_id': int(values.get('analytic_account')) if values.get('analytic_account') else False,
            'date': values.get('date'),
            'unit_amount': float(values.get('unit_price')),
            'employee_id': emp.id,
            'product_id': int(values.get('product')),
            'quantity': int(values.get('quantity')),
            'operations_type': operation_type.operation_type.id if operation_type else False,
            'sales_id': int(values.get('sales_id')) if values.get('sales_id') else False,
            'currency_id': int(values.get('currency_id')) if values.get('currency_id') else False,
            'partner_surgeon_id': int(values.get('partner_surgeon_id')) if values.get('partner_surgeon_id') else False,
            'payment_mode': 'company_account',
            'analytic_tag_ids': [(6, 0, com_list)],
            'tax_ids': [(6, 0, tax_list)],
        })

        attachments = values.get('attachment_ids')
        if attachments:
            self.env['ir.attachment'].sudo().create({
                'name': attachments.filename,
                'datas': base64.b64encode(attachments.read()),
                'res_model': 'hr.expense',
                'res_id': expense.id,
            })

        return {'id': expense.id}
    @api.model
    def edit_expense_record(self, values):
        user = self.env.user
        if not user.expense_portal_access:
            raise AccessError("You do not have the necessary permissions.")

        print("vals",values)
        emp = self.env['hr.employee'].browse(self.env.user.employee_id.id)
        operation_type = self.env['operation.operation'].browse(int(values.get('sales_id'))) if values.get('sales_id') else False
        account = self.env['product.product'].sudo().browse(int(values.get('product')))

        expense = self.env['hr.expense'].sudo().browse(int(values['expense_id'])).write({
            'name': values.get('description'),
            'expense_type': values.get('expense_type'),
            'account_id': account.property_account_expense_id.id,
            'analytic_account_id': int(values.get('analytic_account')) if values.get('analytic_account') else False,
            'date': values.get('date'),
            'unit_amount': float(values.get('unit_price')),
            'employee_id': emp.id,
            'product_id': int(values.get('product')),
            'quantity': int(values.get('quantity')),
            'operations_type': operation_type.operation_type.id if operation_type else False,
            'sales_id': int(values.get('sales_id')) if values.get('sales_id') else False,
            'currency_id': int(values.get('currency_id')) if values.get('currency_id') else False,
            'partner_surgeon_id': int(values.get('partner_surgeon_id')) if values.get('partner_surgeon_id') else False,
            'payment_mode': 'company_account',
        })
        expense = self.env['hr.expense'].sudo().browse(int(values['expense_id']))


        return {'id': expense.id}
