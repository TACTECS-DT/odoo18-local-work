# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiQuailty(http.Controller):
#     @http.route('/surgi_quailty/surgi_quailty/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_quailty/surgi_quailty/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_quailty.listing', {
#             'root': '/surgi_quailty/surgi_quailty',
#             'objects': http.request.env['surgi_quailty.surgi_quailty'].search([]),
#         })

#     @http.route('/surgi_quailty/surgi_quailty/objects/<model("surgi_quailty.surgi_quailty"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_quailty.object', {
#             'object': obj
#         })
