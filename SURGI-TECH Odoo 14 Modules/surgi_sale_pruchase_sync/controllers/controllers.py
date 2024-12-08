# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSalePruchaseSync(http.Controller):
#     @http.route('/surgi_sale_pruchase_sync/surgi_sale_pruchase_sync/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sale_pruchase_sync/surgi_sale_pruchase_sync/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sale_pruchase_sync.listing', {
#             'root': '/surgi_sale_pruchase_sync/surgi_sale_pruchase_sync',
#             'objects': http.request.env['surgi_sale_pruchase_sync.surgi_sale_pruchase_sync'].search([]),
#         })

#     @http.route('/surgi_sale_pruchase_sync/surgi_sale_pruchase_sync/objects/<model("surgi_sale_pruchase_sync.surgi_sale_pruchase_sync"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sale_pruchase_sync.object', {
#             'object': obj
#         })
