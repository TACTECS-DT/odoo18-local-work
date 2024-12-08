# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiInventoryChangesCustom(http.Controller):
#     @http.route('/surgi_inventory_changes_custom/surgi_inventory_changes_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_inventory_changes_custom/surgi_inventory_changes_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_inventory_changes_custom.listing', {
#             'root': '/surgi_inventory_changes_custom/surgi_inventory_changes_custom',
#             'objects': http.request.env['surgi_inventory_changes_custom.surgi_inventory_changes_custom'].search([]),
#         })

#     @http.route('/surgi_inventory_changes_custom/surgi_inventory_changes_custom/objects/<model("surgi_inventory_changes_custom.surgi_inventory_changes_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_inventory_changes_custom.object', {
#             'object': obj
#         })
