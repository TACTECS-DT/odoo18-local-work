# -*- coding: utf-8 -*-
# from odoo import http


# class AhHrAttendenceSheet(http.Controller):
#     @http.route('/ah_hr_attendence_sheet/ah_hr_attendence_sheet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ah_hr_attendence_sheet/ah_hr_attendence_sheet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ah_hr_attendence_sheet.listing', {
#             'root': '/ah_hr_attendence_sheet/ah_hr_attendence_sheet',
#             'objects': http.request.env['ah_hr_attendence_sheet.ah_hr_attendence_sheet'].search([]),
#         })

#     @http.route('/ah_hr_attendence_sheet/ah_hr_attendence_sheet/objects/<model("ah_hr_attendence_sheet.ah_hr_attendence_sheet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ah_hr_attendence_sheet.object', {
#             'object': obj
#         })
