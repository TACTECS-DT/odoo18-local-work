# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiWaitinglist(http.Controller):
#     @http.route('/surgi_waitinglist/surgi_waitinglist/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_waitinglist/surgi_waitinglist/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_waitinglist.listing', {
#             'root': '/surgi_waitinglist/surgi_waitinglist',
#             'objects': http.request.env['surgi_waitinglist.surgi_waitinglist'].search([]),
#         })

#     @http.route('/surgi_waitinglist/surgi_waitinglist/objects/<model("surgi_waitinglist.surgi_waitinglist"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_waitinglist.object', {
#             'object': obj
#         })
