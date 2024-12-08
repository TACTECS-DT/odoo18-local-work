# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiHelpDeskCategory(http.Controller):
#     @http.route('/surgi_help_desk_category/surgi_help_desk_category/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_help_desk_category/surgi_help_desk_category/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_help_desk_category.listing', {
#             'root': '/surgi_help_desk_category/surgi_help_desk_category',
#             'objects': http.request.env['surgi_help_desk_category.surgi_help_desk_category'].search([]),
#         })

#     @http.route('/surgi_help_desk_category/surgi_help_desk_category/objects/<model("surgi_help_desk_category.surgi_help_desk_category"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_help_desk_category.object', {
#             'object': obj
#         })
