# -*- coding: utf-8 -*-
from odoo import http

# class ElearningHideCourse(http.Controller):
#     @http.route('/elearning_hide_course/elearning_hide_course/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/elearning_hide_course/elearning_hide_course/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('elearning_hide_course.listing', {
#             'root': '/elearning_hide_course/elearning_hide_course',
#             'objects': http.request.env['elearning_hide_course.elearning_hide_course'].search([]),
#         })

#     @http.route('/elearning_hide_course/elearning_hide_course/objects/<model("elearning_hide_course.elearning_hide_course"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('elearning_hide_course.object', {
#             'object': obj
#         })