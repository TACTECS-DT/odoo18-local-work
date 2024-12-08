# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiRegularity(http.Controller):
#     @http.route('/surgi_regularity/surgi_regularity/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_regularity/surgi_regularity/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_regularity.listing', {
#             'root': '/surgi_regularity/surgi_regularity',
#             'objects': http.request.env['surgi_regularity.surgi_regularity'].search([]),
#         })

#     @http.route('/surgi_regularity/surgi_regularity/objects/<model("surgi_regularity.surgi_regularity"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_regularity.object', {
#             'object': obj
#         })
