# -*- coding: utf-8 -*-
# from odoo import http


# class Faked-items(http.Controller):
#     @http.route('/faked-items/faked-items/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/faked-items/faked-items/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('faked-items.listing', {
#             'root': '/faked-items/faked-items',
#             'objects': http.request.env['faked-items.faked-items'].search([]),
#         })

#     @http.route('/faked-items/faked-items/objects/<model("faked-items.faked-items"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('faked-items.object', {
#             'object': obj
#         })
