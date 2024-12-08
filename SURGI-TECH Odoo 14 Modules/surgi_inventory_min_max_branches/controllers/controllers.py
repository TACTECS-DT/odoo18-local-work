# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiInventoryMinMaxBranches(http.Controller):
#     @http.route('/surgi_inventory_min_max_branches/surgi_inventory_min_max_branches/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_inventory_min_max_branches/surgi_inventory_min_max_branches/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_inventory_min_max_branches.listing', {
#             'root': '/surgi_inventory_min_max_branches/surgi_inventory_min_max_branches',
#             'objects': http.request.env['surgi_inventory_min_max_branches.surgi_inventory_min_max_branches'].search([]),
#         })

#     @http.route('/surgi_inventory_min_max_branches/surgi_inventory_min_max_branches/objects/<model("surgi_inventory_min_max_branches.surgi_inventory_min_max_branches"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_inventory_min_max_branches.object', {
#             'object': obj
#         })
