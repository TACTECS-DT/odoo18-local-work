# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiAccountingTracks(http.Controller):
#     @http.route('/surgi_accounting_tracks/surgi_accounting_tracks/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_accounting_tracks/surgi_accounting_tracks/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_accounting_tracks.listing', {
#             'root': '/surgi_accounting_tracks/surgi_accounting_tracks',
#             'objects': http.request.env['surgi_accounting_tracks.surgi_accounting_tracks'].search([]),
#         })

#     @http.route('/surgi_accounting_tracks/surgi_accounting_tracks/objects/<model("surgi_accounting_tracks.surgi_accounting_tracks"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_accounting_tracks.object', {
#             'object': obj
#         })
