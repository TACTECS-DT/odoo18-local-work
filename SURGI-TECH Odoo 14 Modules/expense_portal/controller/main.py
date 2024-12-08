# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, date
from pytz import timezone
from odoo import http, fields, exceptions,_
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
import base64

import werkzeug
import json
from werkzeug.utils import redirect
# class WebsiteFormInherit(WebsiteForm):
class WebsiteFormExpense(http.Controller):

    @http.route(['/expense/request/form'], type='http', method="POST", auth="public", website=True)
    def expense_request_form(self, **kwargs):
        user = request.env.user
        if not user.expense_portal_access:
            return redirect('/my/access-denied')

        vals = self.get_default_vals(kwargs)
        return request.render("expense_portal.expense_portal_request_form",vals)

    @http.route(['''/expense/request/edit/<model('hr.expense'):expense>'''], type='http', auth="user", website=True, methods=['POST','GET'])
    def portal_my_salary_request_edit(self,expense, **kw):
        user = request.env.user
        if not user.expense_portal_access:
            return redirect('/my/access-denied')

        vals = self.get_default_vals(kw)
        vals.update({'expense':expense,'surgeon':expense.partner_surgeon_id.display_name,'product_id':expense.product_id.display_name,
                     'analytic_account_id':expense.analytic_account_id.display_name,

                     })
        return request.render(
            "expense_portal.edit_expense_portal_request_form", vals)


    @http.route(['/my/expense/requests'], type='http', method="POST", auth="public", website=True)
    def my_expense_requests(self, **kwargs):
        user = request.env.user
        if not user.expense_portal_access:
            return redirect('/my/access-denied')

        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        my_requests = self.get_my_requests()
        return request.render("expense_portal.my_expense_requests",
                              {'my_requests': my_requests})

    @http.route(['/expense/request/create'], type='http', method="POST", auth="public", website=True)
    def portal_expense_request_insert(self, **kwargs):
        user = request.env.user
        if not user.expense_portal_access:
            return redirect('/my/access-denied')

        try:
            emp = int(kwargs.get('employee'))
            emp = request.env['hr.employee'].browse(emp)
            operation_type =  request.env['operation.operation'].browse(int(kwargs.get('sales_id'))) if int(kwargs.get('sales_id')) else False
            account = request.env['product.product'].sudo().browse(int(kwargs.get('product')))
            tags = request.httprequest.form.getlist('product_categ_ids[]')
            taxes = request.httprequest.form.getlist('tax_ids[]')

            com_list =[]
            for com in tags:
                com_list.append(int(com))
            tax_list =[]

            for tax in taxes:
                tax_list.append(int(tax))

            expense = request.env['hr.expense'].sudo().create({
                                                   'name': kwargs.get('description'),
                                                   'expense_type': kwargs.get('expense_type'),
                                                   'account_id': account.property_account_expense_id.id,
                                                    'analytic_account_id': int(kwargs.get('analytic_account')) if int(kwargs.get('analytic_account')) else False,
                                                   'date': kwargs.get('date'),
                                                   'unit_amount': float(kwargs.get('unit_price')),
                                                   'employee_id': emp.id,
                                                   'product_id':int(kwargs.get('product')) ,
                                                   'quantity':int(kwargs.get('quantity')),
                                                    'operations_type':operation_type.operation_type.id,
                                                    'sales_id': int(kwargs.get('sales_id')) if int(kwargs.get('sales_id')) else False,
                                                    'partner_surgeon_id': int(kwargs.get('partner_surgeon_id')) if kwargs.get('partner_surgeon_id') else False,
                                                   'payment_mode':'company_account',
                                                    'analytic_tag_ids': [(6, 0, com_list)],
                                                    'tax_ids': [(6, 0, tax_list)],

            })
            attachments = request.httprequest.files.get('attachment_ids')
            if attachments:
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': attachments.filename,
                    'datas': base64.b64encode(attachments.read()),
                    'res_model': 'hr.expense',
                    'res_id': expense.id,
                })

        except Exception as e:
            warn = str(self.prepare_error_msg(e))
            vals = self.get_default_vals(kwargs)
            vals.update({'warn_message':warn})
            return request.render("expense_portal.expense_portal_request_form",vals)
        vals = self.get_default_vals({})
        vals.update({'pass_message': True,'expense_request_id': expense})
        return request.render("expense_portal.expense_portal_request_form",vals)
        # return request.render("custody_portal.request_created", {'expense_request_id': custody})

    @http.route(["/expense/request/<int:expense_request_id>"], type='http', auth="public", website=True)
    def expense_request_view(self, expense_request_id=None, **kw):
        user = request.env.user
        if not user.expense_portal_access:
            return redirect('/my/access-denied')

        expense_request_id = request.env['hr.expense'].browse(int(expense_request_id))
        attachments = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'hr.expense'),
            ('res_id', '=', expense_request_id.id)
        ])
        return request.render("expense_portal.requests_followup", {'expense_request_id': expense_request_id, 'attachments': attachments})


    def prepare_error_msg(self, e):
        msg = ''
        if hasattr(e, 'name'):
            msg += e.name
        elif hasattr(e, 'msg'):
            msg += e.msg
        elif hasattr(e, 'args'):
            msg += e.args[0]
        return msg


    def get_op_domain(self):
        today_date = date.today()
        current_year = datetime.now().year
        start_date_str = '{}-01-01 00:00:00'.format(current_year)
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone('UTC'))
        operation_rec = []
        try:
            operation_rec = request.env['operation.operation'].search([('create_date', '>=', start_date)])
        except Exception as e:
            # Log the exception
            print(f"Error in fetching operation records: {str(e)}")

        expiration_rec = []
        try:
            expiration_rec = request.env['hr.expense.expiration'].sudo().search([], limit=1)
        except Exception as e:
            # Log the exception
            print(f"Error in fetching expiration record: {str(e)}")

        print(expiration_rec)
        sales_list = []

        for rec in operation_rec:
            if rec.start_datetime:
                date_order = datetime.strptime(str(rec.start_datetime).split(".")[0],
                                               '%Y-%m-%d %H:%M:%S').date()

                if expiration_rec and int(str((today_date - date_order).days)) <= expiration_rec.num_day_expire:
                    sales_list.append(rec.id)
        return {
            'domain': {'sales_id': [('id', 'in', sales_list)]}
        }

    def get_default_vals(self,kwargs):
            default_values={}
            employee = self.get_employees()
            products = self.get_products()
            domain_dict = self.get_op_domain()
            currency = request.env['res.currency'].sudo().search([])

            default_currency = request.env['res.currency'].sudo().search([('name','ilike','EGP')],limit=1)
            sales_domain = domain_dict['domain']['sales_id']
            current_year = datetime.now().year
            start_date = '{}-01-01 00:00:00'.format(current_year)
            domain = [('create_date', '>=', start_date)] + sales_domain
            operations = request.env['operation.operation'].search(domain)
            taxes = request.env['account.tax'].sudo().search(
                [('company_id', '=', request.env.user.company_id.id), ('type_tax_use', '=', 'purchase')])
            analytic_account = request.env['account.analytic.account'].sudo().search(
                ['|', ('company_id', '=', request.env.user.company_id.id), ('company_id', '=', False)])
            analytic_account_tag = request.env['account.analytic.tag'].sudo().search(
                ['|', ('company_id', '=', request.env.user.company_id.id), ('company_id', '=', False)])
            surgeons = http.request.env['res.partner'].sudo().search([('is_surgeon', '=', True)])

            if kwargs != {}:
                default_values['date'] = kwargs.get('date')
                default_values['description'] = kwargs.get('description')
                default_values['quantity'] = int(kwargs.get('quantity')) if kwargs.get('quantity') else 1
                default_values['unit_price'] = kwargs.get('unit_price')
                default_values['total'] = kwargs.get('total')
                employee = employee
                product = products.browse(int(kwargs.get('product')))

            else:
                default_values['date'] = fields.date.today()
                default_values['unit_price'] = products[0].standard_price if products[0] else 0
                default_values['quantity'] = 1
                default_values['total'] = products[0].standard_price if products[0] else 0.0
                product = request.env['product.product'].search([("can_be_expensed", "=", True)])

            return {
                   'employees': employee,
                   'employee': employee,
                   'products': products,
                   'product': product,
                   'default_currency': default_currency,
                    'operations':operations,
                    'analytic_account':analytic_account,
                    'surgeons':surgeons,
                    'analytic_account_tag':analytic_account_tag,
                    'taxes':taxes,
                    'currency':currency,
                   'default_values': default_values}
    def get_employees(self):
        return request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)],limit=1)
    def get_products(self):
        return request.env['product.product'].sudo().search([('can_be_expensed','=',True)])

    def get_my_requests(self):
        return request.env['hr.expense'].sudo().search([('employee_id.user_id', '=', request.env.user.id)],
                                                       order='create_date desc')

    @http.route('/submit-manager/<int:exp_id>', type='http', auth='public', website=True, methods=['GET'])
    def submit_sheet_to_manager(self, exp_id, **kwargs):
        user = request.env.user
        if not user.expense_portal_access:
            return redirect('/my/access-denied')

        exp = http.request.env['hr.expense'].sudo().browse(exp_id)
        if exp:
            exp.sheet_id.action_submit_sheet()
        return http.request.redirect('/expense/request/' + str(exp.id))
    @http.route('/create-report/<int:exp_id>', type='http', auth='public', website=True, methods=['GET'])
    def create_exp_report(self, exp_id, **kwargs):
        user = request.env.user
        if not user.expense_portal_access:
            return redirect('/my/access-denied')

        exp = http.request.env['hr.expense'].sudo().browse(exp_id)
        if exp:
            exp.action_submit_expenses()
        return http.request.redirect('/expense/request/' + str(exp.id))


    @http.route('/search_exp_operations', type='json', auth='public')
    def search_expense_operation(self, query):
        domain_dict = self.get_op_domain()
        sales_domain = domain_dict['domain']['sales_id']
        current_year = datetime.now().year
        start_date = '{}-01-01 00:00:00'.format(current_year)
        domain = [('create_date', '>=', start_date)] + sales_domain
        domain = [('name', 'ilike', query)] + domain
        operations = request.env['operation.operation'].search(domain,limit=100, order='name')
        return [{'id': s.id, 'name': s.display_name} for s in operations]

    @http.route('/search_exp_products', type='json', auth='public')
    def search_products(self, query):
        domain = ['|',('default_code','ilike',query),('name', 'ilike', query), ('can_be_expensed','=',True)]
        products = http.request.env['product.product'].sudo().search(domain, limit=100, order='name')
        return [{'id': s.id, 'name': s.display_name} for s in products]

    @http.route('/search_analytic_account', type='json', auth='public')
    def search_analytics(self, query):
        domain = ['|',('code','ilike',query),('name', 'ilike', query)]
        analytics = http.request.env['account.analytic.account'].sudo().search(domain, limit=100, order='name')
        print(analytics)
        return [{'id': s.id, 'name': s.display_name} for s in analytics]

    @http.route('/attachment/add', type='http', auth='public', methods=['POST'], website=True)
    def attachment_expense_add(self, name, file, res_model, res_id, access_token=None, **kwargs):
        IrAttachment = http.request.env['ir.attachment']
        attachment = IrAttachment.sudo().create({
            'name': name,
            'datas': base64.b64encode(file.read()),
            'res_model': res_model,
            'res_id': res_id,
        })
        return http.request.make_response(
            data=json.dumps({'id': attachment.id}),
            headers=[('Content-Type', 'application/json')]
        )