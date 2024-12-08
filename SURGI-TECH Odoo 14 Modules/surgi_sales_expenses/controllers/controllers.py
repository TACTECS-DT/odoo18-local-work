# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSalesExpenses(http.Controller):
#     @http.route('/surgi_sales_expenses/surgi_sales_expenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sales_expenses/surgi_sales_expenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sales_expenses.listing', {
#             'root': '/surgi_sales_expenses/surgi_sales_expenses',
#             'objects': http.request.env['surgi_sales_expenses.surgi_sales_expenses'].search([]),
#         })

#     @http.route('/surgi_sales_expenses/surgi_sales_expenses/objects/<model("surgi_sales_expenses.surgi_sales_expenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sales_expenses.object', {
#             'object': obj
#         })
