# -*- coding: utf-8 -*-
# from odoo import http


# class TactecsTrustModule(http.Controller):
#     @http.route('/tactecs_trust_module/tactecs_trust_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tactecs_trust_module/tactecs_trust_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tactecs_trust_module.listing', {
#             'root': '/tactecs_trust_module/tactecs_trust_module',
#             'objects': http.request.env['tactecs_trust_module.tactecs_trust_module'].search([]),
#         })

#     @http.route('/tactecs_trust_module/tactecs_trust_module/objects/<model("tactecs_trust_module.tactecs_trust_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tactecs_trust_module.object', {
#             'object': obj
#         })

