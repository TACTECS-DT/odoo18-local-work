# -*- coding: utf-8 -*-
# from odoo import http


# class surgi_sales_discount(http.Controller):
#     @http.route('/surgi_sales_discount/surgi_sales_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sales_discount/surgi_sales_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sales_discount.listing', {
#             'root': '/surgi_sales_discount/surgi_sales_discount',
#             'objects': http.request.env['surgi_sales_discount.surgi_sales_discount'].search([]),
#         })

#     @http.route('/surgi_sales_discount/surgi_sales_discount/objects/<model("surgi_sales_discount.surgi_sales_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sales_discount.object', {
#             'object': obj
#         })
