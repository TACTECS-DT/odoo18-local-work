# -*- coding: utf-8 -*-
# from odoo import http


# class PortalCustomExtend(http.Controller):
#     @http.route('/portal_custom_extend/portal_custom_extend', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/portal_custom_extend/portal_custom_extend/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('portal_custom_extend.listing', {
#             'root': '/portal_custom_extend/portal_custom_extend',
#             'objects': http.request.env['portal_custom_extend.portal_custom_extend'].search([]),
#         })

#     @http.route('/portal_custom_extend/portal_custom_extend/objects/<model("portal_custom_extend.portal_custom_extend"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('portal_custom_extend.object', {
#             'object': obj
#         })
