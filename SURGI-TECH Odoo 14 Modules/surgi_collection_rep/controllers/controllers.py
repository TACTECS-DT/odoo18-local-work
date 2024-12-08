# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiCollectionRep(http.Controller):
#     @http.route('/surgi_collection_rep/surgi_collection_rep/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_collection_rep/surgi_collection_rep/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_collection_rep.listing', {
#             'root': '/surgi_collection_rep/surgi_collection_rep',
#             'objects': http.request.env['surgi_collection_rep.surgi_collection_rep'].search([]),
#         })

#     @http.route('/surgi_collection_rep/surgi_collection_rep/objects/<model("surgi_collection_rep.surgi_collection_rep"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_collection_rep.object', {
#             'object': obj
#         })
