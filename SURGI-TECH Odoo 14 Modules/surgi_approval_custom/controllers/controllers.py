# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiApprovalCustom(http.Controller):
#     @http.route('/surgi_approval_custom/surgi_approval_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_approval_custom/surgi_approval_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_approval_custom.listing', {
#             'root': '/surgi_approval_custom/surgi_approval_custom',
#             'objects': http.request.env['surgi_approval_custom.surgi_approval_custom'].search([]),
#         })

#     @http.route('/surgi_approval_custom/surgi_approval_custom/objects/<model("surgi_approval_custom.surgi_approval_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_approval_custom.object', {
#             'object': obj
#         })
