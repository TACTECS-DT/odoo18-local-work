# -*- coding: utf-8 -*-
# from odoo import http


# class AhTimeOff(http.Controller):
#     @http.route('/ah_time_off/ah_time_off/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ah_time_off/ah_time_off/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ah_time_off.listing', {
#             'root': '/ah_time_off/ah_time_off',
#             'objects': http.request.env['ah_time_off.ah_time_off'].search([]),
#         })

#     @http.route('/ah_time_off/ah_time_off/objects/<model("ah_time_off.ah_time_off"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ah_time_off.object', {
#             'object': obj
#         })
