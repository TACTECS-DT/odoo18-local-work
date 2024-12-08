# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiAdminWharehouse(http.Controller):
#     @http.route('/surgi_admin_wharehouse/surgi_admin_wharehouse/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_admin_wharehouse/surgi_admin_wharehouse/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_admin_wharehouse.listing', {
#             'root': '/surgi_admin_wharehouse/surgi_admin_wharehouse',
#             'objects': http.request.env['surgi_admin_wharehouse.surgi_admin_wharehouse'].search([]),
#         })

#     @http.route('/surgi_admin_wharehouse/surgi_admin_wharehouse/objects/<model("surgi_admin_wharehouse.surgi_admin_wharehouse"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_admin_wharehouse.object', {
#             'object': obj
#         })
