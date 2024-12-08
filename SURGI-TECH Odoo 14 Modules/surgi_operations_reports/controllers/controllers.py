# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiOperationsReports(http.Controller):
#     @http.route('/surgi_operations_reports/surgi_operations_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_operations_reports/surgi_operations_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_operations_reports.listing', {
#             'root': '/surgi_operations_reports/surgi_operations_reports',
#             'objects': http.request.env['surgi_operations_reports.surgi_operations_reports'].search([]),
#         })

#     @http.route('/surgi_operations_reports/surgi_operations_reports/objects/<model("surgi_operations_reports.surgi_operations_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_operations_reports.object', {
#             'object': obj
#         })
