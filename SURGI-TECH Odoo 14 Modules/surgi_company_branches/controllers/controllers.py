# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiCompanyBranches(http.Controller):
#     @http.route('/surgi_company_branches/surgi_company_branches/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_company_branches/surgi_company_branches/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_company_branches.listing', {
#             'root': '/surgi_company_branches/surgi_company_branches',
#             'objects': http.request.env['surgi_company_branches.surgi_company_branches'].search([]),
#         })

#     @http.route('/surgi_company_branches/surgi_company_branches/objects/<model("surgi_company_branches.surgi_company_branches"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_company_branches.object', {
#             'object': obj
#         })
