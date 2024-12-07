# -*- coding: utf-8 -*-
# from odoo import http


# class Mmm(http.Controller):
#     @http.route('/mmm/mmm', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mmm/mmm/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mmm.listing', {
#             'root': '/mmm/mmm',
#             'objects': http.request.env['mmm.mmm'].search([]),
#         })

#     @http.route('/mmm/mmm/objects/<model("mmm.mmm"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mmm.object', {
#             'object': obj
#         })

