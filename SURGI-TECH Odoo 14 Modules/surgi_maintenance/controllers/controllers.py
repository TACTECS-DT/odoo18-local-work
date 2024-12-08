# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiMaintenance(http.Controller):
#     @http.route('/surgi_maintenance/surgi_maintenance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_maintenance/surgi_maintenance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_maintenance.listing', {
#             'root': '/surgi_maintenance/surgi_maintenance',
#             'objects': http.request.env['surgi_maintenance.surgi_maintenance'].search([]),
#         })

#     @http.route('/surgi_maintenance/surgi_maintenance/objects/<model("surgi_maintenance.surgi_maintenance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_maintenance.object', {
#             'object': obj
#         })
