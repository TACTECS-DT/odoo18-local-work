# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiOperationExtend(http.Controller):
#     @http.route('/surgi_operation_extend/surgi_operation_extend', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_operation_extend/surgi_operation_extend/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_operation_extend.listing', {
#             'root': '/surgi_operation_extend/surgi_operation_extend',
#             'objects': http.request.env['surgi_operation_extend.surgi_operation_extend'].search([]),
#         })

#     @http.route('/surgi_operation_extend/surgi_operation_extend/objects/<model("surgi_operation_extend.surgi_operation_extend"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_operation_extend.object', {
#             'object': obj
#         })
