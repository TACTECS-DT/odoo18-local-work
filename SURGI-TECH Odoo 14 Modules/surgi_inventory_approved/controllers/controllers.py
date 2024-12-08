# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiInventoryApproved(http.Controller):
#     @http.route('/surgi_inventory_approved/surgi_inventory_approved/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_inventory_approved/surgi_inventory_approved/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_inventory_approved.listing', {
#             'root': '/surgi_inventory_approved/surgi_inventory_approved',
#             'objects': http.request.env['surgi_inventory_approved.surgi_inventory_approved'].search([]),
#         })

#     @http.route('/surgi_inventory_approved/surgi_inventory_approved/objects/<model("surgi_inventory_approved.surgi_inventory_approved"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_inventory_approved.object', {
#             'object': obj
#         })
