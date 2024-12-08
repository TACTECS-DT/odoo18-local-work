import base64
import functools
import json
import logging
import math
import re

from werkzeug import urls

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    @route()
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key]
                          for key in self.MANDATORY_BILLING_FIELDS}
                values.update(
                    {key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})

                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                values.update({
                    'error': {},
                    'error_message': [],
                    'success': 'Details updated Successfully'
                })

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
            'dashboard_class': 'active',
            'title': 'CRM | User Profile'
        })

        response = request.render("portal_custom.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        user = request.env.user
        user_employee = user.employee_id
        get_days_all_request = request.env['hr.leave.type'].sudo().get_days_all_request()

        return request.render("portal_custom.portal_custom_dashboard",
                              {"user_infos": [user_employee.image_1920, user_employee.name,
                                              user_employee.identification_id, user_employee.job_title,
                                              user_employee.department_id.name],
                               'timeoffs': get_days_all_request,

                               }
                              )

    @route('/portal/contactus')
    def contactus_form(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error_message = False
            if post['name'] == '' or post['email'] == '' or post['phone'] == '' or post['subject'] == '' or post[
                'service'] == '' or post['comment'] == '':
                error_message = ['Please fill out all fields marked *']
                values.update({'error': {}, 'error_message': error_message})
                values.update(post)
            if not error_message:
                contact_name = post['name']
                values = {
                    'name': post['subject'],
                    'contact_name': contact_name,
                    'email_from': post['email'],
                    'partner_name': post['partner_name'],
                    'phone': post['phone'],
                    'stage_id': 1,
                    'type': 'lead',
                    'description': post['comment'],
                    'service_id': post['service'],
                }

                request.env['crm.lead'].sudo().create(values)
                values.update({
                    'error': {},
                    'error_message': [],
                    'success': 'Contact Us Form Submitted Successfully'
                })

        services = request.env['product.template'].sudo().search(
            [
                ('type', '=', 'service'),
                ('company_id', '=', 1),

            ])

        values.update({
            'partner': partner,
            'redirect': redirect,
            'page_name': 'portal_contact_us',
            'services': services,
            'dashboard_class': 'active',
            'title': 'CRM | Contact Us',
        })

        response = request.render("portal_custom.portal_contactus", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/my/profile'], type='http', auth="user", website=True)
    def my_profile(self, **kw):
        values = self._prepare_portal_layout_values()
        employee = request.env.user.employee_id
        scholarships = request.env['emp.scholarship'].sudo().search([('name', '=', employee.id)])
        scholarships_stage = request.env['scholarship.stage'].sudo().search([])

        values.update({
            'emp': employee,
            'scholarships': scholarships,
            'scholarships_stage': scholarships_stage,
            'page_name': 'portal_my_profile',
            'dashboard_class': 'active',
            'title': 'Portal | My Profile',
        })

        return request.render("portal_custom.my_profile", values)

    @http.route('/my/access-denied', type='http', auth='public', website=True)
    def access_denied(self, **kw):
        return http.request.render('portal_custom.access_denied_template')




