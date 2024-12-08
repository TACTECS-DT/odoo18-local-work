# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiPurchaseStartScan(http.Controller):
#     @http.route('/surgi_purchase_start_scan/surgi_purchase_start_scan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_purchase_start_scan/surgi_purchase_start_scan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_purchase_start_scan.listing', {
#             'root': '/surgi_purchase_start_scan/surgi_purchase_start_scan',
#             'objects': http.request.env['surgi_purchase_start_scan.surgi_purchase_start_scan'].search([]),
#         })

#     @http.route('/surgi_purchase_start_scan/surgi_purchase_start_scan/objects/<model("surgi_purchase_start_scan.surgi_purchase_start_scan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_purchase_start_scan.object', {
#             'object': obj
#         })
