# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSalesExtend(http.Controller):
#     @http.route('/surgi_sales_extend/surgi_sales_extend', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sales_extend/surgi_sales_extend/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sales_extend.listing', {
#             'root': '/surgi_sales_extend/surgi_sales_extend',
#             'objects': http.request.env['surgi_sales_extend.surgi_sales_extend'].search([]),
#         })

#     @http.route('/surgi_sales_extend/surgi_sales_extend/objects/<model("surgi_sales_extend.surgi_sales_extend"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sales_extend.object', {
#             'object': obj
#         })
