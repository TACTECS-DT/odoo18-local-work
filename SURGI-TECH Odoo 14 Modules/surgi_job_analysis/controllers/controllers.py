# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSurveys(http.Controller):
#     @http.route('/surgi_job_analysis/surgi_job_analysis/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_job_analysis/surgi_job_analysis/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_job_analysis.listing', {
#             'root': '/surgi_job_analysis/surgi_job_analysis',
#             'objects': http.request.env['surgi_job_analysis.surgi_job_analysis'].search([]),
#         })

#     @http.route('/surgi_job_analysis/surgi_job_analysis/objects/<model("surgi_job_analysis.surgi_job_analysis"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_job_analysis.object', {
#             'object': obj
#         })
