# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSalesOrderLinesReport(http.Controller):
#     @http.route('/surgi_sales_order_lines_report/surgi_sales_order_lines_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sales_order_lines_report/surgi_sales_order_lines_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sales_order_lines_report.listing', {
#             'root': '/surgi_sales_order_lines_report/surgi_sales_order_lines_report',
#             'objects': http.request.env['surgi_sales_order_lines_report.surgi_sales_order_lines_report'].search([]),
#         })

#     @http.route('/surgi_sales_order_lines_report/surgi_sales_order_lines_report/objects/<model("surgi_sales_order_lines_report.surgi_sales_order_lines_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sales_order_lines_report.object', {
#             'object': obj
#         })
