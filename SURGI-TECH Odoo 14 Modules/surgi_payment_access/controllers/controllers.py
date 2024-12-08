# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiPurchaseAccess(http.Controller):
#     @http.route('/surgi_payment_access/surgi_payment_access/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_payment_access/surgi_payment_access/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_payment_access.listing', {
#             'root': '/surgi_payment_access/surgi_payment_access',
#             'objects': http.request.env['surgi_payment_access.surgi_payment_access'].search([]),
#         })

#     @http.route('/surgi_payment_access/surgi_payment_access/objects/<model("surgi_payment_access.surgi_payment_access"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_payment_access.object', {
#             'object': obj
#         })
