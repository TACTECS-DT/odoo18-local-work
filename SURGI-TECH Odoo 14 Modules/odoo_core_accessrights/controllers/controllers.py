# -*- coding: utf-8 -*-
# from odoo import http


# class OdooCoreAccessrights(http.Controller):
#     @http.route('/odoo_core_accessrights/odoo_core_accessrights/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_core_accessrights/odoo_core_accessrights/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_core_accessrights.listing', {
#             'root': '/odoo_core_accessrights/odoo_core_accessrights',
#             'objects': http.request.env['odoo_core_accessrights.odoo_core_accessrights'].search([]),
#         })

#     @http.route('/odoo_core_accessrights/odoo_core_accessrights/objects/<model("odoo_core_accessrights.odoo_core_accessrights"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_core_accessrights.object', {
#             'object': obj
#         })
