from werkzeug.exceptions import Forbidden
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, Response, content_disposition
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
import werkzeug
from datetime import datetime, date, timezone
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
from odoo.tools import float_compare
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import json
from werkzeug.utils import redirect
from odoo.exceptions import ValidationError, UserError
import base64
import logging


class WarehousePortal(CustomerPortal):

    @http.route(['/admin/warehouse', '/admin/warehouse/page/<int:page>'], type='http', auth="user", website=True)
    def portal_all_warehouse_request(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                                     groupby='none',
                                     **kw):
        user = request.env.user
        if not user.admin_request_portal_access:
            return redirect('/my/access-denied')


        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        wherehouse_pool = request.env['admin.warehouse']

        domain = [('employee_id', '=', request.env.user.employee_id.id)]

        #        domain = []

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name desc'},
            'date': {'label': _('Date'), 'order': 'date desc'},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'

        sort_order = searchbar_sortings[sortby]['order']
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state': {'input': 'state', 'label': _('State')},
        }

        today = fields.Date.today()
        this_week_end_date = fields.Date.to_string(fields.Date.from_string(today) + timedelta(days=7))
        week_ago = datetime.today() - timedelta(days=7)
        month_ago = (datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
        starting_of_year = datetime.now().date().replace(month=1, day=1)
        ending_of_year = datetime.now().date().replace(month=12, day=31)

        def sd(date):
            return fields.Datetime.to_string(date)

        def previous_week_range(date):
            start_date = date + timedelta(-date.weekday(), weeks=-1)
            end_date = date + timedelta(-date.weekday() - 1)
            return {'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S')}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'),
                      'domain': [('create_date', '>=', datetime.strftime(date.today(), '%Y-%m-%d 00:00:00')),
                                 ('create_date', '<=', datetime.strftime(date.today(), '%Y-%m-%d 23:59:59'))]},
            'yesterday': {'label': _('Yesterday'), 'domain': [
                ('create_date', '>=', datetime.strftime(date.today() - timedelta(days=1), '%Y-%m-%d 00:00:00')),
                ('create_date', '<=', datetime.strftime(date.today(), '%Y-%m-%d 23:59:59'))]},
            'week': {'label': _('This Week'),
                     'domain': [('create_date', '>=', sd(datetime.today() + relativedelta(days=-today.weekday()))),
                                ('create_date', '<=', this_week_end_date)]},
            'last_seven_days': {'label': _('Last 7 Days'),
                                'domain': [('create_date', '>=', sd(week_ago)),
                                           ('create_date', '<=', sd(datetime.today()))]},
            'last_week': {'label': _('Last Week'),
                          'domain': [('create_date', '>=', previous_week_range(datetime.today()).get('start_date')),
                                     ('create_date', '<=', previous_week_range(datetime.today()).get('end_date'))]},

            'last_month': {'label': _('Last 30 Days'),
                           'domain': [('create_date', '>=', month_ago), ('create_date', '<=', sd(datetime.today()))]},
            'month': {'label': _('This Month'),
                      'domain': [
                          ("create_date", ">=", sd(today.replace(day=1))),
                          ("create_date", "<",
                           (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))
                      ]
                      },
            'year': {'label': _('This Year'),
                     'domain': [
                         ("create_date", ">=", sd(starting_of_year)),
                         ("create_date", "<=", sd(ending_of_year)),
                     ]
                     }
        }
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        #        archive_groups = self._get_archive_groups('admin.warehouse')
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # count for pager
        wherehouse_count = wherehouse_pool.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/admin/warehouse",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=wherehouse_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        wherehouse = wherehouse_pool.search(domain, order=sort_order, limit=self._items_per_page,
                                            offset=pager['offset'])
        request.session['my_wherehouse_history'] = wherehouse.ids[:100]
        if groupby == 'state':
            grouped_warehouses = [request.env['admin.warehouse'].concat(*g) for k, g in
                                  groupbyelem(wherehouse, itemgetter('state'))]
        else:
            grouped_warehouses = [wherehouse]

        values.update({
            'date': date_begin,
            'wherehouse': wherehouse.sudo(),
            'page_name': 'wherehouse',
            'grouped_wherehouse': grouped_warehouses,
            'pager': pager,
            #            'archive_groups': archive_groups,
            'default_url': '/admin/warehouse',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'filterby': filterby,
            'sortby': sortby,
            'groupby': groupby,
        })
        return request.render("admin_warehouse_portal.admin_wherehouse_portal_view", values)

    def _admin_warehouse_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'admin_request': order,
            'token': access_token,
            'return_url': '/admin/warehouse',
            'bootstrap_formatting': True,
            'partner_id': order.employee_id.user_id.partner_id.id,
        }
        if order.company_id:
            values['res_company'] = order.company_id

        history = request.session.get('my_wherehouse_history', [])
        values.update(get_records_pager(history, order))

        return values

    @http.route(['/admin/warehouse/<int:request_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, request_id, report_type=None, access_token=None, message=False, download=False, **kw):
        user = request.env.user
        if not user.admin_request_portal_access:
            return redirect('/my/access-denied')


        try:
            request_sudo = self._document_check_access('admin.warehouse', request_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my/home')

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if request_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_request_%s' % request_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_request_%s' % request_sudo.id] = now
                body = _('Request viewed by Employee %s', request_sudo.employee_id.name)
                _message_post_helper(
                    "admin.warehouse",
                    request_sudo.id,
                    body,
                    token=request_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=request_sudo.user_id.sudo().partner_id.ids,
                )

        values = self._admin_warehouse_get_page_view_values(request_sudo, access_token, **kw)
        values['message'] = message
        print(values)
        return request.render('admin_warehouse_portal.requests_followup', values)

    @http.route(['/admin/warehouse/new'], type='http', auth="user", website=True)
    def portal_new_request(self, **post):
        user = request.env.user
        if not user.admin_request_portal_access:
            return redirect('/my/access-denied')


        request_date = fields.Date.today()
        obj = request.env['product.product'].sudo().search([('product_group', 'ilike', 'Admin')])
        res = []
        for rec in obj:
            res.append(rec.categ_id.id)
        domain = [('id', 'in', res)]
        product_category = request.env['product.category'].sudo().search(domain)
        vals = {
            'request_date': request_date,
            'product_category': product_category,

        }
        return request.render("admin_warehouse_portal.admin_wherehouse_new_request_portal_view", vals
                              )

    @http.route(['/admin/warehouse/create'], type='http', method="POST", auth="public", website=True)
    def portal_admin_request_request_insert(self, **kwargs):
        user = request.env.user
        if not user.admin_request_portal_access:
            return redirect('/my/access-denied')


        try:
            categ = request.httprequest.form.getlist('ProductCategory')
            product_ids = request.httprequest.form.getlist('product_id')
            qty = request.httprequest.form.getlist('quantity')
            reason = request.httprequest.form.getlist('reason')

            print(categ)
            service_lines = []
            for idx, product_ids in enumerate(product_ids):

                    service_lines.append((0, 0, {
                        'ProductCategory': float(categ[idx]),
                        'product_id': product_ids,
                        'quantity': int(qty[idx]),
                        'reason': str(reason[idx]),

                    }))

            admin_request = request.env['admin.warehouse'].sudo().create({
                'employee_id': request.env.user.employee_id.id,
                'user_id': request.env.user.employee_id.parent_id.user_id.id,
                'company_id': request.env.user.company_id.id,
                'date': fields.Date.today(),
                'lines_ids': service_lines,

            })


        except Exception as e:
            warn = str(self.prepare_error_msg(e))
            return request.render("admin_warehouse_portal.admin_wherehouse_new_request_portal_view", {'warn_message': warn})
        return  request.redirect('/admin/warehouse/' + str(admin_request.id))
    def prepare_error_msg(self, e):
        msg = ''
        if hasattr(e, 'name'):
            msg += e.name
        elif hasattr(e, 'msg'):
            msg += e.msg
        elif hasattr(e, 'args'):
            msg += e.args[0]
        return msg
    @http.route('/admin/warehouse/submit-manager/<int:exp_id>', type='http', auth='public', website=True, methods=['GET'])
    def submit_sheet_to_manager(self, exp_id, **kwargs):
        user = request.env.user
        if not user.admin_request_portal_access:
            return redirect('/my/access-denied')


        exp = http.request.env['admin.warehouse'].sudo().browse(exp_id)
        if exp:
            exp.action_submit()
        return http.request.redirect('/admin/warehouse/' + str(exp.id))