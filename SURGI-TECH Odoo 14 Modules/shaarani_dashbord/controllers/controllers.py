# -*- coding: utf-8 -*-
# from odoo import http


# class ShaaraniDashbord(http.Controller):
#     @http.route('/shaarani_dashbord/shaarani_dashbord/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shaarani_dashbord/shaarani_dashbord/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shaarani_dashbord.listing', {
#             'root': '/shaarani_dashbord/shaarani_dashbord',
#             'objects': http.request.env['shaarani_dashbord.shaarani_dashbord'].search([]),
#         })

#     @http.route('/shaarani_dashbord/shaarani_dashbord/objects/<model("shaarani_dashbord.shaarani_dashbord"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shaarani_dashbord.object', {
#             'object': obj
#         })
