# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiPricelists(http.Controller):
#     @http.route('/surgi_pricelists/surgi_pricelists/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_pricelists/surgi_pricelists/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_pricelists.listing', {
#             'root': '/surgi_pricelists/surgi_pricelists',
#             'objects': http.request.env['surgi_pricelists.surgi_pricelists'].search([]),
#         })

#     @http.route('/surgi_pricelists/surgi_pricelists/objects/<model("surgi_pricelists.surgi_pricelists"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_pricelists.object', {
#             'object': obj
#         })
