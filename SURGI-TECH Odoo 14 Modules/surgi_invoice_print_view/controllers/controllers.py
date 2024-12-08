# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiInvoicePrintView(http.Controller):
#     @http.route('/surgi_invoice_print_view/surgi_invoice_print_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_invoice_print_view/surgi_invoice_print_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_invoice_print_view.listing', {
#             'root': '/surgi_invoice_print_view/surgi_invoice_print_view',
#             'objects': http.request.env['surgi_invoice_print_view.surgi_invoice_print_view'].search([]),
#         })

#     @http.route('/surgi_invoice_print_view/surgi_invoice_print_view/objects/<model("surgi_invoice_print_view.surgi_invoice_print_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_invoice_print_view.object', {
#             'object': obj
#         })
