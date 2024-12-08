# -*- coding: utf-8 -*-
# from odoo import http


# class HrAttendanceCustom(http.Controller):
#     @http.route('/hr_attendance_custom/hr_attendance_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_attendance_custom/hr_attendance_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_attendance_custom.listing', {
#             'root': '/hr_attendance_custom/hr_attendance_custom',
#             'objects': http.request.env['hr_attendance_custom.hr_attendance_custom'].search([]),
#         })

#     @http.route('/hr_attendance_custom/hr_attendance_custom/objects/<model("hr_attendance_custom.hr_attendance_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_attendance_custom.object', {
#             'object': obj
#         })
