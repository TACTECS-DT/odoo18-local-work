# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiTrackingUsers(http.Controller):
#     @http.route('/surgi_tracking_users/surgi_tracking_users/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_tracking_users/surgi_tracking_users/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_tracking_users.listing', {
#             'root': '/surgi_tracking_users/surgi_tracking_users',
#             'objects': http.request.env['surgi_tracking_users.surgi_tracking_users'].search([]),
#         })

#     @http.route('/surgi_tracking_users/surgi_tracking_users/objects/<model("surgi_tracking_users.surgi_tracking_users"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_tracking_users.object', {
#             'object': obj
#         })
