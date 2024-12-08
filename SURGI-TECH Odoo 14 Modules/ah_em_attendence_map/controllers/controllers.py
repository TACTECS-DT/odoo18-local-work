# -*- coding: utf-8 -*-
# from odoo import http


# class AhEmAttendenceMap(http.Controller):
#     @http.route('/ah_em_attendence_map/ah_em_attendence_map/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ah_em_attendence_map/ah_em_attendence_map/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ah_em_attendence_map.listing', {
#             'root': '/ah_em_attendence_map/ah_em_attendence_map',
#             'objects': http.request.env['ah_em_attendence_map.ah_em_attendence_map'].search([]),
#         })

#     @http.route('/ah_em_attendence_map/ah_em_attendence_map/objects/<model("ah_em_attendence_map.ah_em_attendence_map"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ah_em_attendence_map.object', {
#             'object': obj
#         })
