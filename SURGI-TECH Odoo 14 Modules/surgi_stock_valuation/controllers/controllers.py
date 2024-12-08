# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiStockValuation(http.Controller):
#     @http.route('/surgi_stock_valuation/surgi_stock_valuation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_stock_valuation/surgi_stock_valuation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_stock_valuation.listing', {
#             'root': '/surgi_stock_valuation/surgi_stock_valuation',
#             'objects': http.request.env['surgi_stock_valuation.surgi_stock_valuation'].search([]),
#         })

#     @http.route('/surgi_stock_valuation/surgi_stock_valuation/objects/<model("surgi_stock_valuation.surgi_stock_valuation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_stock_valuation.object', {
#             'object': obj
#         })
