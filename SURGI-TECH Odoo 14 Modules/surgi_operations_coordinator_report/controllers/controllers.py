# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiOperationsCoordinatorReport(http.Controller):
#     @http.route('/surgi_operations_coordinator_report/surgi_operations_coordinator_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_operations_coordinator_report/surgi_operations_coordinator_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_operations_coordinator_report.listing', {
#             'root': '/surgi_operations_coordinator_report/surgi_operations_coordinator_report',
#             'objects': http.request.env['surgi_operations_coordinator_report.surgi_operations_coordinator_report'].search([]),
#         })

#     @http.route('/surgi_operations_coordinator_report/surgi_operations_coordinator_report/objects/<model("surgi_operations_coordinator_report.surgi_operations_coordinator_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_operations_coordinator_report.object', {
#             'object': obj
#         })
