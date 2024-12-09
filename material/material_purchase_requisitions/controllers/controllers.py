# -*- coding: utf-8 -*-
# from odoo import http


# class MaterialPurchaseRequisitions(http.Controller):
#     @http.route('/material_purchase_requisitions/material_purchase_requisitions', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/material_purchase_requisitions/material_purchase_requisitions/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('material_purchase_requisitions.listing', {
#             'root': '/material_purchase_requisitions/material_purchase_requisitions',
#             'objects': http.request.env['material_purchase_requisitions.material_purchase_requisitions'].search([]),
#         })

#     @http.route('/material_purchase_requisitions/material_purchase_requisitions/objects/<model("material_purchase_requisitions.material_purchase_requisitions"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('material_purchase_requisitions.object', {
#             'object': obj
#         })

