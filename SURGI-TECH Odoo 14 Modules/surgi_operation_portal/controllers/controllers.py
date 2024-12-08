# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
from odoo.addons.portal.controllers.mail import _message_post_helper

from odoo import http, _, fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, MissingError
from odoo.http import request ,Response
from odoo.tools import date_utils
from odoo.osv.expression import AND, OR
from odoo.fields import Datetime
import werkzeug
import binascii
import json
from odoo import http, _
from operator import itemgetter
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time
from collections import OrderedDict
from collections import namedtuple
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime , timedelta
from odoo.tools import groupby as groupbyelem
from werkzeug.utils import secure_filename, redirect
class PortalOperation(CustomerPortal):

    # ------------------------------------------------------------
    # Hr Portal operations
    # ------------------------------------------------------------

    def _operation_get_page_view_values(self, operation_operation, access_token, **kwargs):
        values = {
            'page_name': 'operation_operation',
            'operation_operation': operation_operation,
        }
        return self._get_page_view_values(operation_operation, access_token, values, 'my_operation_history', False,
                                          **kwargs)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if request.env.user._is_admin():
            domain = []
        else:
            domain = [('responsible', '=', request.env.user.id)]
        counters.append('operation_count')
        if 'operation_count' in counters:
            operation_count = request.env['operation.operation'].search_count(domain) \
                if request.env['operation.operation'].check_access_rights('read', raise_exception=False) else 0
            if not operation_count:
                operation_count = '0'
            values['operation_count'] = operation_count
        return values

    def _get_searchbar_op_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Operation')},
            'operation_type': {'input': 'operation_type', 'label': _('Operation Type')},
            'patient_id': {'input': 'patient_id', 'label': _('Patient')},
            'hospital_id': {'input': 'hospital_id', 'label': _('Hospital')},
            'surgeon_id': {'input': 'surgeon_id', 'label': _('Surgeon')},
            'state': {'input': 'state', 'label': _('Status')},
            'start_datetime': {'input': 'start_datetime', 'label': _('Search in Date Start')},
        }

    def _get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('name', 'all'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        if search_in in ('operation_type', 'all'):
            search_domain = OR([search_domain, [('operation_type.name', 'ilike', search)]])
        if search_in in ('patient_id', 'all'):
            search_domain = OR([search_domain, [('patient_id.name', 'ilike', search)]])
        if search_in in ('hospital_id', 'all'):
            search_domain = OR([search_domain, [('hospital_id.name', 'ilike', search)]])
        if search_in in ('surgeon_id', 'all'):
            search_domain = OR([search_domain, [('surgeon_id.name', 'ilike', search)]])
        if search_in in ('state', 'all'):
            search_domain = OR([search_domain, [('state', 'ilike', search)]])
        if search_in in ('start_datetime', 'all'):
            search_domain = OR([search_domain, [('start_datetime', 'ilike', search)]])
        return search_domain

    def _get_searchbar_op_sortings(self):
        return {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc', 'sequence': 1},
            'start_datetime': {'label': _('Operation Start'), 'order': 'start_datetime desc', 'sequence': 2},
            'operation_type': {'label': _('Operation Type'), 'order': 'operation_type', 'sequence': 3},
            'name': {'label': _('Operation'), 'order': 'operation', 'sequence': 4},
            'state': {'label': _('Status'), 'order': 'state', 'sequence': 5},
        }

    def _get_searchbar_op_groupby(self):
        values = {
            'none': {'input': 'none', 'label': _('None'),'order': 1},
            'operation_type': {'input': 'operation_type', 'label': _('Operation Type'),'order': 2},
            'state': {'input': 'state', 'label': _('Status'),'order': 3},
            'hospital_id': {'input': 'hospital_id', 'label': _('Hospital'),'order': 4},
            'surgeon_id': {'input': 'surgeon_id', 'label': _('Surgeon'),'order': 5},
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_groupby_mapping(self):
        return {
            'operation_type': 'operation_type',
            'state': 'state',
            'hospital_id': 'hospital_id',
            'surgeon_id': 'surgeon_id',
        }

    def _get_order(self, order, groupby):
        groupby_mapping = self._get_groupby_mapping()
        field_name = groupby_mapping.get(groupby, '')
        if not field_name:
            return order
        return '%s, %s' % (field_name, order)

    @http.route(['/my/operation', '/my/operation/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_operation(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        values = self._prepare_portal_layout_values()
        operation = request.env['operation.operation'].sudo()
        _items_per_page = 100

        if request.env.user._is_admin():
            domain = []
        else:
            domain = [('responsible', '=', request.env.user.id)]
            # ('employee_id', '=', request.env.user.employee_id.id)
        searchbar_sortings = self._get_searchbar_op_sortings()
        searchbar_groupby = self._get_searchbar_op_groupby()
        searchbar_inputs = self._get_searchbar_op_inputs()
        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'knee': {'label': _('Knee Operation'), 'domain': [('operation_type.name','like','Knee Operation')]},
            'hip': {'label': _('Hip Operation'), 'domain': [('operation_type.name','like','Hip Operation')]},
            'new_recon': {'label': _('New Recon Operation'), 'domain': [('operation_type.name','like','New Recon Operation')]},
            'trauma': {'label': _('Trauma Operation'), 'domain': [('operation_type.name','like','Trauma Operation')]},
            'spine': {'label': _('Spine Operation'), 'domain': [('operation_type.name','like','Spine Operation')]},
            'tender_knee': {'label': _('Tender Primary Knee'), 'domain': [('operation_type.name','like','Tender Primary Knee')]},
            'bipolar': {'label': _('Tender Bipolar'), 'domain': [('operation_type.name','like','Tender Bipolar')]},
            'shoulder': {'label': _('SHOULDER'), 'domain': [('operation_type.name','like','SHOULDER')]},
            'acl': {'label': _('ACL'), 'domain': [('operation_type.name','like','ACL')]},
            'biologic': {'label': _('Biologic Operation'), 'domain': [('operation_type.name','like','Biologic Operation')]},
            'today': {'label': _('Today'), 'domain': [("create_date", ">=", Datetime.to_string(
                Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))), ("create_date", "<=",
                                                                                      Datetime.to_string(
                                                                                          Datetime.now().replace(
                                                                                              hour=23, minute=59,
                                                                                              second=59,
                                                                                              microsecond=59)))]},
            'week': {'label': _('This week'), 'domain': [('create_date', '>=', date_utils.start_of(today, "week")),
                                                         ('create_date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'month')),
                                                           ('create_date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'year')),
                                                         ('create_date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'),
                        'domain': [('create_date', '>=', quarter_start), ('create_date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'),
                          'domain': [('create_date', '>=', date_utils.start_of(last_week, "week")),
                                     ('create_date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'),
                           'domain': [('create_date', '>=', date_utils.start_of(last_month, 'month')),
                                      ('create_date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'),
                          'domain': [('create_date', '>=', date_utils.start_of(last_year, 'year')),
                                     ('create_date', '<=', date_utils.end_of(last_year, 'year'))]},
        }

        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        if not groupby:
            groupby = 'none'

        if search and search_in:
            domain += self._get_search_domain(search_in, search)

        operation_count = operation.search_count(domain)

        pager = portal_pager(
            url="/my/operation",
            url_args={'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby,
                      'sortby': sortby},
            total=operation_count,
            page=page,
            step=_items_per_page
        )

        order = self._get_order(order, groupby)
        operations = operation.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        print('operations',operations)

        request.session['my_operation_history'] = operations.ids[:100]

        groupby_mapping = self._get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_operations = [operation.concat(*g) for k, g in groupbyelem(operations, itemgetter(group))]
        else:
            grouped_operations = [operations]

        print('grouped_operations',grouped_operations)
        values.update({
            'grouped_operations': grouped_operations,
            'page_name': 'operation_operation',
            'pager': pager,
            'default_url': '/my/operation',
            'search_in': search_in,
            'search': search,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'title': 'Operations',
        })
        return request.render("surgi_operation_portal.portal_my_operations", values)

    #
    # @http.route(['/my/operation/<int:attendance_id>'], type='http', auth="public", website=True)
    # def portal_my_operation_detail(self, attendance_id, access_token=None, report_type=None, download=False, **kw):
    #     try:
    #         operation_operation = self._document_check_access('hr.attendance', attendance_id, access_token)
    #     except (AccessError, MissingError):
    #         return request.redirect('/my')
    #
    #     # if report_type in ('html', 'pdf', 'text'):
    #     #     return self._show_report(model=operation_operation, report_type=report_type, report_ref='account.account_invoices', download=download)
    #
    #     values = self._attendance_get_page_view_values(operation_operation, access_token, **kw)
    #     acquirers = values.get('acquirers')
    #     if acquirers:
    #         country_id = values.get('partner_id') and values.get('partner_id')[0].country_id.id
    #         values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(operation_operation.amount_residual, operation_operation.currency_id, country_id)
    #
    #     return request.render("portal_attendance_knk.portal_attendance_page", values)

    # @http.route(['''/my/operation/<model('operation.operation'):op>'''], type='http', auth="user", website=True)
    # def portal_my_op(self, op, **kw):
    #     user = request.env.user
    #     if not user.operation_portal_access:
    #         return redirect('/my/access-denied')
    #     emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
    #     operationQuantities=http.request.env['stock.quant'].sudo().search([("id",'=',op.id),('location_id', '=', op.location_id.id), ('quantity', '>', 0)],limit=100)
    #     print('operationsssssssss')
    #     print(op)
    #     return request.render(
    #         "surgi_operation_portal.portal_my_operations_view", {
    #             'operation': op,
    #              "operationQuantities":operationQuantities,
    #             'page_name': 'operation_operation',
    #         })

    @http.route(['/my/operation/<int:request_id>'], type='http', auth="public", website=True)
    def portal_operation_page(self, request_id, report_type=None, access_token=None, message=False,
                              download=False, **kw):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        try:
            request_sudo = self._document_check_access('operation.operation', request_id,
                                                       access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my/home')

        if request_sudo and self._should_log_view(request_sudo, access_token):
            self._log_request_view(request_sudo, access_token)

        values = self._operation_get_page_view_values(request_sudo, access_token, **kw)
        values['message'] = message
        return request.render('surgi_operation_portal.portal_my_operations_view', values)

    def _should_log_view(self, request_sudo, access_token):
        now = fields.Date.today().isoformat()
        session_obj_date = request.session.get('view_request_%s' % request_sudo.id)
        return session_obj_date != now and request.env.user.share and access_token

    def _log_request_view(self, request_sudo, access_token):
        request.session['view_request_%s' % request_sudo.id] = fields.Date.today().isoformat()
        body = _('Request viewed by Employee %s', request_sudo.employee_id.name)
        _message_post_helper(
            "operation.operation",
            request_sudo.id,
            body,
            token=request_sudo.access_token,
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=request_sudo.responsible.sudo().partner_id.ids,
        )

    def _operation_get_page_view_values(self, order, access_token, **kwargs):
        operationQuantities = http.request.env['stock.quant'].sudo().search(
            [("id", '=', order.id), ('location_id', '=', order.location_id.id), ('quantity', '>', 0)], limit=100)

        values = {
            'operation': order,
            'token': access_token,
            'return_url': '/my/operation',
            'bootstrap_formatting': True,
            'partner_id': request.env.user.partner_id.id,
            "operationQuantities": operationQuantities,

        }

        history = request.session.get('my_operation_history', [])
        values.update(get_records_pager(history, order))

        # Convert the date fields from order to Python datetime objects if needed

        return values

    @http.route(['''/my/operation/edit/<model('operation.operation'):op>'''], type='http', auth="user", website=True,
                methods=['POST', 'GET'])
    def portal_my_op_edit(self, op, **post):
        print(post)
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')
        if post:
            # Update the operation with the submitted data
            attachment_pre = request.httprequest.files.get('attachment_pre')
            attachment_after = request.httprequest.files.get('attachment_after')
            attachment_patient = request.httprequest.files.get('attachment_patient')
            product_add_ids = request.httprequest.form.getlist('op_add_more_product_id')
            # internals = request.httprequest.form.getlist('internal')
            internals = request.httprequest.form.getlist('internal_hidden')
            externals = request.httprequest.form.getlist('external_hidden')
            replacements = request.httprequest.form.getlist('replacement_hidden')

            # Convert the values to boolean
            internals = [True if x == 'True' else False for x in internals]
            externals = [True if x == 'True' else False for x in externals]
            replacements = [True if x == 'True' else False for x in replacements]
            if 'op_add_more_product_id' in request.params:
                del post['op_add_more_product_id']
            if 'internal' in request.params:
                del post['internal']
            if 'external' in request.params:
                del post['external']
            if 'prod_replacement' in request.params:
                del post['prod_replacement']

            # product_more_lines = []
            product_tuples = []
            for idx, product_id in enumerate(product_add_ids):
                internal_value =  internals[idx]
                external_value = externals[idx]
                replacement_value =  replacements[idx]
                product_tuples.append((int(product_id), internal_value, external_value, replacement_value))
            product_more_lines = [(0, 0, {'product_id': tpl[0],
                                          'internal': tpl[1],
                                          'external': tpl[2],
                                          'prod_replacement': tpl[3],
                                          }) for tpl in product_tuples]

            component_ids = request.httprequest.form.getlist('component_ids[]')
            com_list =[]
            for com in component_ids:
                com_list.append(int(com))
            product_ids = request.httprequest.form.getlist('op_add_product_id')
            quantities = request.httprequest.form.getlist('quantity')
            if 'op_add_product_id' in request.params:
                del post['op_add_product_id']
            if 'product_id' in request.params:
                del post['product_id']
            if 'quantity' in request.params:
                del post['quantity']
            product_lines = []
            for idx, product_id in enumerate(product_ids):
                product_lines.append((0, 0, {
                    'product_id': int(product_id),
                    'quantity': float(quantities[idx]),
                }))

            op.write({
                # ...
                'product_lines': [(5, 0, 0)],  # remove existing product lines
                'product_qunat_tab': [(5, 0, 0)]  # remove existing product lines
            })

            op.write({
                'patient_id': post.get('patient_id'),
                'patient_name': post.get('patient_name'),
                'patient_gender': post.get('patient_gender'),
                'patient_national_id': post.get('patient_national_id'),
                'operation_type':int(post.get('operation_type')),
                'op_type': post.get('op_type'),
                'start_datetime': post.get('start_datetime'),
                'side': post.get('side'),
                'op_sales_area': post.get('op_sales_area'),
                'hospital_id':int(post.get('hospital_id')),
                'authority': post.get('authority'),
                'surgeon_id': int(post.get('surgeon_id')),
                'DoctorPhoneNum': post.get('DoctorPhoneNum'),
                'payment_methods': post.get('payment_methods'),
                'paitent_joint_pre_company': post.get('paitent_joint_pre_company'),
                'warehouse_id': int(post.get('warehouse_id')),
                'location_id': int(post.get('location_id')),
                'component_ids': [(6, 0, com_list)],
                'notes': post.get('op_notes'),  # added op_notes field
                'hospital_additional_notes': post.get('hospital_additional_notes'),
                # added hospital_additional_notes field
                'product_lines': product_lines,
                'product_qunat_tab': product_more_lines
            })


            # Save input files to the operation record
            if attachment_pre:
                try:
                    op.write({'attachment_pre': binascii.a2b_base64(attachment_pre.read())})
                except binascii.Error as e:
                    return request.make_response("Error decoding attachment_pre: {}".format(str(e)),
                                                 headers=[('Content-Type', 'text/plain')])
            if attachment_after:
                try:
                    op.write({'attachment_after': binascii.a2b_base64(attachment_after.read())})
                except binascii.Error as e:
                    return request.make_response("Error decoding attachment_after: {}".format(str(e)),
                                                 headers=[('Content-Type', 'text/plain')])
            if attachment_patient:
                try:
                    op.write({'attachment_patient': binascii.a2b_base64(attachment_patient.read())})
                except binascii.Error as e:
                    return request.make_response("Error decoding attachment_patient: {}".format(str(e)),
                                                 headers=[('Content-Type', 'text/plain')])

            # Redirect to the updated operation's details page
            return request.redirect('/my/operation/%d' % op.id)

        if not post:
            patients = http.request.env['res.partner'].sudo().search([('is_patient', '=', True)],limit=100)
            surgeons = http.request.env['res.partner'].sudo().search([('is_surgeon', '=', True)],limit=100)
            hospitals = http.request.env['res.partner'].sudo().search([('is_hospital', '=', True)],limit=100)
            warehouses = http.request.env['stock.warehouse'].sudo().search([],limit=100)
            locations = http.request.env['stock.location'].sudo().search([],limit=100)
            operation_type_id = http.request.env['product.operation.type'].sudo().search([])#,limit=100)
            operations_teams = http.request.env['crm.team'].sudo().search([],limit=100)
            operationQuantities=http.request.env['stock.quant'].sudo().search([("id",'=',op.id),('location_id', '=', op.location_id.id), ('quantity', '>', 0)],limit=100)
            component = http.request.env['product.product'].sudo().search([('operation_component', '=', True)],)
            #component=None

            products = http.request.env['product.product'].sudo().search([('purchase_ok', '=', True)],limit=100)
            print('edit my operation')
            return request.render("surgi_operation_portal.portal_my_operations_edit",
                                  {'operation': op, 'products': products,
                                   'operation_type': operation_type_id,
                                   'operations_teams': operations_teams,
                                   'hospitals': hospitals,
                                   'surgeons': surgeons,
                                   'warehouses': warehouses,
                                   'locations': locations,
                                   'components': component,
                                   'patients': patients,
                                   "operationQuantities":operationQuantities,
                                   'page_name': 'operation_operation_edit'})

    @http.route(['''/my/operation/product/line/delete/<model('product.operation.line'):rl>'''], type='http', methods=['GET'], auth="user",
                website=True,
                csrf=False)
    def portal_my_operation_product_line_delete(self, rl, **kw):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        pr_link = "/my/operation/edit/%s" % (rl.operation_id.id)
        rl.sudo().unlink()
        return werkzeug.utils.redirect(pr_link)
    @http.route(['''/my/operation/product/line/more/delete/<model('stock.items'):rl>'''], type='http', methods=['GET'], auth="user",
                website=True,
                csrf=False)
    def portal_my_operation_product_line_more_delete(self, rl, **kw):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        pr_link = "/my/operation/edit/%s" % (rl.operation_id.id)
        rl.sudo().unlink()
        return werkzeug.utils.redirect(pr_link)
    @http.route(['/my/operation/new'], type='http', auth="user", website=True)
    def portal_my_op_new(self, **post):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        if not post:

            # patients = http.request.env['waiting.list.patients'].sudo().search([('is_active', '=', True)],limit=100)
            # surgeons = http.request.env['res.partner'].sudo().search([('is_surgeon', '=', True)],limit=100)
            # hospitals = http.request.env['res.partner'].sudo().search([('is_hospital', '=', True)],limit=100)
            # warehouses = http.request.env['stock.warehouse'].sudo().search([],limit=100)
            # locations = http.request.env['stock.location'].sudo().search([],limit=100)
            operation_type_id = http.request.env['product.operation.type'].sudo().search([])
            operations_teams = http.request.env['crm.team'].sudo().search([],limit=100)
            currentteam=http.request.env['crm.team'].sudo().search([('id','=',http.request.env.user.sale_team_id.id)],limit=1)
            component = []#http.request.env['product.product'].sudo().search([('operation_component', '=', True)],)

            products = http.request.env['product.product'].sudo().search([('purchase_ok', '=', True)])
            print('edit my operation')
            return request.render("surgi_operation_portal.portal_my_operations_new",
                                  {'products': products,
                                   'operation_type': operation_type_id,
                                   'operations_teams': operations_teams,
                                   # 'hospitals': hospitals,
                                   # 'surgeons': surgeons,
                                   # 'warehouses': warehouses,
                                   # 'locations': locations,
                                   'components': component,
                                   'currentteam':currentteam,
                                   # 'patients': patients,
                                   'page_name': 'operation_operation_new'})



    @http.route('/get_initial_surgeons', type='json', auth='public')
    def get_initial_surgeons(self, **kwargs):
        surgeons = request.env['res.partner'].sudo().search([('is_surgeon', '=', True)], limit=5)
        return [{'id': surgeon.id, 'name': surgeon.name} for surgeon in surgeons]

    # @http.route('/search_surgeons', type='json', auth='public')
    # def search_surgeons(self, query):
    #     domain = [('name', 'ilike', query), ('is_surgeon', '=', True)]
    #     surgeons = http.request.env['res.partner'].sudo().search(domain, limit=100, order='name')
    #     return [{'id': s.id, 'name': s.name} for s in surgeons]
    #

    @http.route('/search_patients', type='json', auth='public', methods=['POST'])
    def search_patients(self, query="", **kw):
        patients = http.request.env['res.partner'].sudo().search([('is_patient', '=', True), ('name', 'ilike', query)], limit=100)
        return [{"id": patient.id, "name": patient.name} for patient in patients]


    @http.route('/search_surgeons', type='json', auth='public')
    def search_surgeons(self, query, hospital_id=None):
        # if hospital_id:
        #     hospital_id = int(hospital_id)
        #
        # hospital = request.env['res.partner'].sudo().browse(hospital_id) if hospital_id else None

        domain = [('name', 'ilike', query), ('is_surgeon', '=', True)]

        # if hospital and hospital.authority in ['open', 'open_approval']:
        #     op_sales_area = request.env['crm.team'].search(
        #         ['|', ('user_id', '=', request.env.user.id), ('member_ids', '=', request.env.user.id)],
        #         limit=1
        #     )
        #     op_sales_area = op_sales_area.id if op_sales_area else False
        #     domain += [
        #         '|', '|',
        #         ('team_id', '=', op_sales_area),
        #         ('user_id', '=', request.env.user.id),
        #         ('direct_sales_users', '=', request.env.user.id)
        #     ]

        surgeons = request.env['res.partner'].sudo().search(domain, limit=100, order='name')

        return [{'id': s.id, 'name': s.name} for s in surgeons]

    @http.route('/search_hospitals', type='json', auth='public', methods=['POST'])
    def search_hospitals(self, query="", include_activation=True, **kw):
        domain = [
            ('is_hospital', '=', True),
            '|', '|',
            ('name', 'ilike', query),
            ('phone', 'ilike', query),
            ('mobile', 'ilike', query)
        ]

        if include_activation:
            domain.insert(1, ('hospital_activation', '=', True))

        hospitals = request.env['res.partner'].sudo().search(domain, limit=100)
        return [{"id": hospital.id, "name": hospital.name} for hospital in hospitals]

    def addOperatoin(self,vals):
        return request.env['operation.operation'].createOP(vals)
    @http.route(['/my/operation/new/submit'], type='http', auth="user", website=True, methods=['POST'])
    def portal_my_op_new_submit(self, **post):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        try:
            if post:
                product_more_lines = []
                for i in range(1, 100):  # Adjust the range as needed
                    product_key = f'op_add_more_product_id{i}'
                    internal_key = f'internal{i}'
                    external_key = f'external{i}'
                    replacement_key = f'empties{i}'

                    if product_key in post:
                        product_id = int(post.get(product_key, 0))
                        internal = post.get(internal_key, 'off') == 'on'
                        external = post.get(external_key, 'off') == 'on'
                        empties = post.get(replacement_key, 'off') == 'on'

                        product_line = {
                            'product_id': product_id,
                            'internal': internal,
                            'external': external,
                            'prod_replacement': empties,
                        }
                        product_more_lines.append((0, 0, product_line))

                component_ids = request.httprequest.form.getlist('component_ids[]')
                #
                com_list =[]
                for com in component_ids:
                    com_list.append(int(com))
                product_lines = []
                for i in range(1, 100):
                    product_key = f'op_add_product_id{i}'
                    if product_key in post:
                        product_line = {
                            'product_id': int(post.get(product_key, 0)),
                            'quantity': float(post.get(f'quantity{i}', 0)),
                        }
                        product_lines.append((0, 0, product_line))

                #raise Warning(post.get('start_datetime'))
                if post.get('start_datetime'):
                    start_datetime = str(datetime.strptime(str(post.get('start_datetime')+":00"), '%y-%m-%d %H:%M:%S'))
                else:
                    start_datetime = False
                #raise Warning(str(com_list))
                #raise Warning(str( [(6, 0, com_list)]))
                vals = {
                    'patient_id': post.get('patient_id', False),
                    'patient_name': post.get('patient_name', False),
                    'patient_gender': post.get('patient_gender', False),
                    'patient_national_id': post.get('patient_national_id', False),
                    'operation_type': int(post.get('operation_type')) if post.get('operation_type') else 0,
                    'op_type': post.get('op_type', False),
                    'start_datetime': start_datetime if start_datetime else False,
                    'side': post.get('side', False),
                    'op_sales_area': int(post.get('op_sales_area')) if post.get('op_sales_area') else 0,
                    'hospital_id': int(post.get('hospital_id')) if post.get('hospital_id') else 0,
                    'authority': post.get('authority', False),
                    'surgeon_id': int(post.get('surgeon_id')) if post.get('surgeon_id') else 0,
                    'DoctorPhoneNum': post.get('DoctorPhoneNum', False),
                    'payment_methods': post.get('payment_methods', False),
                    'paitent_joint_pre_company': post.get('paitent_joint_pre_company', False),
                    'component_ids': [(6, 0, com_list)] if com_list else False,
                    'notes': post.get('op_notes', False),  # added op_notes field
                    'hospital_additional_notes': post.get('hospital_additional_notes', False),
                    'product_lines': product_lines if product_lines else False,
                    'product_qunat_tab': product_more_lines if product_more_lines else False,
                    'operation_delivery_type': post.get('delivery_type', False),
                    'sale_order_id': post.get('sale_order_id', False),
                }

                # fields = (str(list(vals.keys()))[1:-1])
                # values = (str(list(vals.values()))[1:-1])

                # columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in vals.keys())
                # values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in vals.values())
                # sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('operation_operation', columns, values)
                # sql = sql.replace ( "`","")
                # request.cr.execute(sql)
                # request.cr.execute('''SELECT max(id) from operation_operation''')

                # data = request.cr.fetchone()
                # raise Warning(str(data))
                # op=http.request.env['operation.operation'].sudo().search([('id','=',data[0])])
                #raise UserWarning(vals)
                op=self.addOperatoin(vals)
                #op = http.request.env['operation.operation'].sudo().create(vals)
                #op.env.cr.commit()
                #for comlist in com_list:
                    #query = "insert into operation_operation_product_product_rel (operation_operation_id,product_product_id) values ("+str(op.id)+","+str(comlist)+")"
                    #aise Warning(query)
                    #request.cr.execute(query)
                    #op.component_ids.create({'product_product_id':com_list})
                # raise UserWarning(op.id)
                # for x in op:
                #     for i in com_list:
                #         x.component_ids.write({'product_product_id':i})
                    #http.request.env['operation_operation_product_product_rel'].sudo().create(vals)
                # Save input files to the operation record
                attachment_after = request.httprequest.files.get('attachment_after')
                attachment_patient = request.httprequest.files.get('attachment_paitent')
                attachment_pre = request.httprequest.files.get('attachment_pre')
                additional_file = request.httprequest.files.get('additional_file')
                attachment = post.get('base64', '')
                file_name = post.get('file_name2', '')
                if attachment:

                    op.write({'patient_national_id_image': attachment,'patient_national_id_image_file_name':file_name})

                # patient_national_id_image = request.httprequest.files.get('patient_national_id_image')
                if attachment_pre:
                    file_content = attachment_pre.read()  # Read the file's binary content
                    op.write({'attachment_pre': file_content})  # Directly write to the binary field

                # if patient_national_id_image:
                #     file_content = patient_national_id_image.read()  # Read the file's binary content
                #     op.write({'patient_national_id_image': file_content})  # Directly write to the binary field


                if additional_file:
                    file_content = additional_file.read()  # Read the file's binary content
                    op.write({'additional_file': file_content})  # Directly write to the binary field

                if attachment_after:
                    file_content = attachment_after.read()  # Read the file's binary content
                    op.write({'attachment_after': file_content})  # Directly write to the binary field

                if attachment_patient:
                    file_content = attachment_patient.read()  # Read the file's binary content
                    op.write({'attachment_paitent': file_content})  # Directly write to the binary field

                # Redirect to the updated operation's details page
                # return request.redirect('/my/operation/%d' % op.id)
                return json.dumps({'id': op.id})
        except Exception as e:  # Catch all exceptions
            error_msg = self.prepare_error_msg(e)
            return Response(
                json.dumps({'error': True, 'message': error_msg}),
                content_type='application/json;charset=utf-8',
                status=500
            )
    @http.route(['''/my/operation/getcomponent/'''], type='json', auth="user", website=True,
                methods=[ 'GET','POST'])
    def portal_get_components(self, op_type, **post):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        print(op_type)
        query = "select product_template_id from product_operation_type_product_template_rel where product_operation_type_id="+op_type
        request.cr.execute(query)
        components_ids=request.cr.fetchall()
        components=http.request.env['product.product'].sudo().search([("product_tmpl_id","in",components_ids)])#.component.search([])
        print('components',components)
        print('query',query)
        #components.operation_type.search([])
        l=[]
        for comp in components:
            l.append({'id':comp.id,'name':comp.name})
        return l
        pass
    @http.route(['''/my/operation/getSalesOrders/'''], type='json', auth="user", website=True,
                methods=[ 'GET','POST'])
    def portal_get_SaleOredser(self, sale_order, **post):

        query = "select id,name from sale_order where name like '"+sale_order+"%' limit 100"

        #from odoo.exceptions import UserError, ValidationError
        #return query

        request.cr.execute(query)
        sales_order=request.cr.fetchall()
        #components=http.request.env['product.template'].sudo().search([("id","in",components_ids)])#.component.search([])
        #components.operation_type.search([])
        l=[]
        if sales_order:
            for sale_order in sales_order:
                l.append({'id':sale_order[0],'name':sale_order[1]})
        return l
        pass

    @http.route('/search_patients', type='json', auth='public', methods=['POST'])
    def search_patients(self, query="", **kw):
        patients = http.request.env['res.partner'].sudo().search([('is_patient', '=', True), ('name', 'ilike', query)], limit=100)
        return [{"id": patient.id, "name": patient.name} for patient in patients]

    @http.route('/odoo/rpc/for/get_products', type='json', auth='public', website=True, csrf=False)
    def get_products_search(self, **params):

        search_term = params.get('search_term', '')
        records = request.env['product.product'].sudo().search([('purchase_ok', '=', True),
            '|',  ('name', 'ilike', search_term), ('default_code', 'ilike', search_term)
        ], limit=30)
        return [{'id': r.id, 'display_name': r.display_name} for r in records]


    @http.route(['''/my/operation/freez/<model('operation.operation'):op>'''], type='http', auth="user", website=True,
                methods=[ 'GET','POST'])
    def portal_freez(self, op, **post):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        #operation=http.request.env['operation.operation'].sudo().search(['id','=',op],limit=1)
        op.set_operation_location_freeze_from_operation()

        pass
    @http.route(['''/my/operation/createsool/<model('operation.operation'):op>'''], type='http', auth="user", website=True,
                methods=[ 'GET','POST'])
    def portal_createSol(self, op, **post):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        #operation=http.request.env['operation.operation'].sudo().search(['id','=',op],limit=1)
        op.create_delivery_sales_order()
        pass
    @http.route(['''/my/operation/quantitems/'''], type='http', auth="user", website=True,
                methods=[ 'GET','POST'])
    def portal_quantitems(self, freezed_items, **post):
        user = request.env.user
        if not user.operation_portal_access:
            return redirect('/my/access-denied')

        #operation=http.request.env['operation.operation'].sudo().search(['id','=',op],limit=1)
        quantitems=http.request.env['stock.quant'].sudo().search([('id', 'in', freezed_items)])
        pass
    def prepare_error_msg(self, e):
        msg = ''
        if hasattr(e, 'name'):
            msg += e.name
        elif hasattr(e, 'msg'):
            msg += e.msg
        elif hasattr(e, 'args'):
            msg += e.args[0]
        return msg
    @http.route('/my/operation/get_operation_type', type='json', auth="public")
    def get_operation_type(self, operation_type_id):
        operation_type = request.env['product.operation.type'].browse(int(operation_type_id))
        return {
            'id': operation_type.id,
            'is_molnlycke': operation_type.is_molnlycke,
        }