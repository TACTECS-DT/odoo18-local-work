# -*- coding: utf-8 -*-
# from odoo import http


# class Faked-items(http.Controller):
#     @http.route('/surgi-dummy-items/surgi-dummy-items/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi-dummy-items/surgi-dummy-items/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi-dummy-items.listing', {
#             'root': '/surgi-dummy-items/surgi-dummy-items',
#             'objects': http.request.env['surgi-dummy-items.surgi-dummy-items'].search([]),
#         })

#     @http.route('/surgi-dummy-items/surgi-dummy-items/objects/<model("surgi-dummy-items.surgi-dummy-items"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi-dummy-items.object', {
#             'object': obj
#         })
