# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


# class attendance_sheet(models.Model):
#     _inherit = 'attendance.sheet'
#
#     _inherit = [ 'mail.thread.cc', 'mail.activity.mixin', 'portal.mixin']
#     def _compute_access_url(self):
#         super(attendance_sheet, self)._compute_access_url()
#         for request in self:
#             request.access_url = '/hr/attendance/sheet/%s' % (request.id)
#
#     def _get_report_base_filename(self):
#         self.ensure_one()
#         return '%s %s' % (_('Attendance Sheet'), self.name)


class ResUser(models.Model):
    _inherit = 'res.users'

    attendance_sheet_portal_access = fields.Boolean('Attendance Sheet portal access')

