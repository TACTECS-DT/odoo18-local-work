# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiCompinedProducts(http.Controller):
#     @http.route('/surgi_compined__products/surgi_compined__products/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_compined__products/surgi_compined__products/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_compined__products.listing', {
#             'root': '/surgi_compined__products/surgi_compined__products',
#             'objects': http.request.env['surgi_compined__products.surgi_compined__products'].search([]),
#         })

#     @http.route('/surgi_compined__products/surgi_compined__products/objects/<model("surgi_compined__products.surgi_compined__products"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_compined__products.object', {
#             'object': obj
#         })
