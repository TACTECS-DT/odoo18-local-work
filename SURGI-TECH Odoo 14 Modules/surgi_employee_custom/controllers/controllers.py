# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiEmployeeCustom(http.Controller):
#     @http.route('/surgi_employee_custom/surgi_employee_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_employee_custom/surgi_employee_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_employee_custom.listing', {
#             'root': '/surgi_employee_custom/surgi_employee_custom',
#             'objects': http.request.env['surgi_employee_custom.surgi_employee_custom'].search([]),
#         })

#     @http.route('/surgi_employee_custom/surgi_employee_custom/objects/<model("surgi_employee_custom.surgi_employee_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_employee_custom.object', {
#             'object': obj
#         })
