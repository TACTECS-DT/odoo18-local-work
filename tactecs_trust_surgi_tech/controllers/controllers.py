# -- coding: utf-8 --
# from odoo import http


# class tactecs_trust_surgi_tech(http.Controller):
#     @http.route('/tactecs_trust_surgi_tech/tactecs_trust_surgi_tech/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tactecs_trust_surgi_tech/tactecs_trust_surgi_tech/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tactecs_trust_surgi_tech.listing', {
#             'root': '/tactecs_trust_surgi_tech/tactecs_trust_surgi_tech',
#             'objects': http.request.env['tactecs_trust_surgi_tech.tactecs_trust_surgi_tech'].search([]),
#         })

#     @http.route('/tactecs_trust_surgi_tech/tactecs_trust_surgi_tech/objects/<model("tactecs_trust_surgi_tech.tactecs_trust_surgi_tech"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tactecs_trust_surgi_tech.object', {
#             'object': obj
#         })