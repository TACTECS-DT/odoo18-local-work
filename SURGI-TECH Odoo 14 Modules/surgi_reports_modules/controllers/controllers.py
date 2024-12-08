# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiReportsModules(http.Controller):
#     @http.route('/surgi_reports_modules/surgi_reports_modules/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_reports_modules/surgi_reports_modules/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_reports_modules.listing', {
#             'root': '/surgi_reports_modules/surgi_reports_modules',
#             'objects': http.request.env['surgi_reports_modules.surgi_reports_modules'].search([]),
#         })

#     @http.route('/surgi_reports_modules/surgi_reports_modules/objects/<model("surgi_reports_modules.surgi_reports_modules"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_reports_modules.object', {
#             'object': obj
#         })
