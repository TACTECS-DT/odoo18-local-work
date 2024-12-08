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


class DailyPlan(CustomerPortal):

    @http.route(['/daily/plan', '/daily/plan/page/<int:page>'], type='http', auth="user", website=True)
    def portal_all_daily_plan(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                              groupby='none',
                              **kw):
        user = request.env.user
        if not user.daily_plan_portal_access:
            return redirect('/my/access-denied')


        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        plan_pool = request.env['surgi.outdoor.attendance']

        # domain = [('employee_id', '=', request.env.user.employee_id.id)]

        domain = ['|',('op_start_date','>=',(fields.Date.today()).strftime('%Y-%m-%d') ),('op_start_today','=',(fields.Date.today()).strftime('%Y-%m-%d'))]

        searchbar_sortings = {
            'ref': {'label': _('Name'), 'order': 'ref desc'},
            'op_start_datetime': {'label': _('Start Datetime'), 'op_start_datetime': 'op_start_datetime desc'},
        }

        # default sortby order
        if not sortby:
            sortby = 'ref'

        sort_order = searchbar_sortings[sortby]['order']
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state_employee': {'input': 'state_employee', 'label': _('State Employee')},
            'section_id': {'input': 'section_id', 'label': _('Section')},
            'parent_id': {'input': 'parent_id', 'label': _('Manager')},
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

        #        archive_groups = self._get_archive_groups('surgi.outdoor.attendance')
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # count for pager
        plan_count = plan_pool.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/daily/plan",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=plan_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        plan = plan_pool.search(domain, order=sort_order, limit=self._items_per_page,
                                offset=pager['offset'])
        request.session['my_plan_history'] = plan.ids[:100]
        if groupby == 'state_employee':
            grouped_plans = [request.env['surgi.outdoor.attendance'].concat(*g) for k, g in
                             groupbyelem(plan, itemgetter('state_employee'))]
        elif groupby == 'section_id':
            grouped_plans = [request.env['surgi.outdoor.attendance'].concat(*g) for k, g in
                             groupbyelem(plan, itemgetter('section_id'))]
        elif groupby == 'parent_id':
            grouped_plans = [request.env['surgi.outdoor.attendance'].concat(*g) for k, g in
                             groupbyelem(plan, itemgetter('parent_id'))]
        else:
            grouped_plans = [plan]
        print(grouped_plans)
        values.update({
            'date': date_begin,
            'plan': plan.sudo(),
            'page_name': 'plan',
            'grouped_plans': grouped_plans,
            'pager': pager,
            #            'archive_groups': archive_groups,
            'default_url': '/daily/plan',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'filterby': filterby,
            'sortby': sortby,
            'groupby': groupby,
            'title': 'Employee | Daily Plan',

        })

        return request.render("daily_plan_portal.daily_plan_portal_view", values)

    def _daily_plan_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'daily_plan': order,
            'token': access_token,
            'return_url': '/daily/plan',
            'bootstrap_formatting': True,
            'partner_id': request.env.user.partner_id.id,
        }

        history = request.session.get('my_plan_history', [])
        values.update(get_records_pager(history, order))

        return values

    @http.route(['/daily/plan/<int:request_id>'], type='http', auth="public", website=True)
    def portal_daily_plan_page(self, request_id, report_type=None, access_token=None, message=False, download=False, **kw):
        user = request.env.user
        if not user.daily_plan_portal_access:
            return redirect('/my/access-denied')


        try:
            request_sudo = self._document_check_access('surgi.outdoor.attendance', request_id,
                                                       access_token=access_token)
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
                    "surgi.outdoor.attendance",
                    request_sudo.id,
                    body,
                    token=request_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=request_sudo.user_id.sudo().partner_id.ids,
                )

        values = self._daily_plan_get_page_view_values(request_sudo, access_token, **kw)
        values['message'] = message
        print(values)
        return request.render('daily_plan_portal.requests_followup', values)



    @http.route(['/daily/plan/new'], type='http', auth="user", website=True)
    def portal_new_daily_plan(self, **post):
        user = request.env.user
        if not user.daily_plan_portal_access:
            return redirect('/my/access-denied')


        request_date = fields.Date.today()
        daily_plan = request.env['surgi.outdoor.attendance'].sudo().search([]).operation_id.ids
        domain = [
            '|', ('responsible', '=', request.env.user.id), ('operation_type.is_tender', '=', True),
            ("state", "in", ['confirm']),
            ('id', 'not in', daily_plan),
            ('start_datetime', '>=', fields.Date.context_today(request.env['operation.operation']).strftime("%Y-%m-%d 00:00:00")), '|',
            ('start_datetime', '<=', fields.Date.context_today(request.env['operation.operation']).strftime("%Y-%m-%d 23:59:59")), '&',
            ('start_datetime', '>=',
            (fields.Date.context_today(request.env['operation.operation']) + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")),
            ('start_datetime', '<=',
            (fields.Date.context_today(request.env['operation.operation']) + timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")),
        ]
        obj = request.env['operation.operation'].sudo().search(domain)

        vals = {
            'operations': obj,
            'title': 'New Daily Plan'

        }
        return request.render("daily_plan_portal.daily_plan_new_request_portal_view", vals
                              )

    @http.route(['/daily/plan/create'], type='http', method="POST", auth="public", website=True)
    def portal_daily_plan_request_insert(self, **kwargs):
        user = request.env.user
        if not user.daily_plan_portal_access:
            return redirect('/my/access-denied')


        try:

            datetime_str = kwargs.get('op_start_datetime')
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            odoo_datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
            daily_plan = request.env['surgi.outdoor.attendance'].sudo().create({
                'employee_name': request.env.user.id,
                'state_employee': kwargs.get('state_employee'),
                'operation_id': int(kwargs.get('operation_id')) if kwargs.get(
                    'operation_id') else False,
                'op_start_datetime':odoo_datetime_str

            })


        except Exception as e:
            daily_plan = request.env['surgi.outdoor.attendance'].sudo().search([]).operation_id.ids
            domain = [
                '|', ('responsible', '=', request.env.user.id), ('operation_type.is_tender', '=', True),
                ("state", "in", ['confirm']),
                ('id', 'not in', daily_plan),
                ('start_datetime', '>=',
                 fields.Date.context_today(request.env['operation.operation']).strftime("%Y-%m-%d 00:00:00")), '|',
                ('start_datetime', '<=',
                 fields.Date.context_today(request.env['operation.operation']).strftime("%Y-%m-%d 23:59:59")), '&',
                ('start_datetime', '>=',
                 (fields.Date.context_today(request.env['operation.operation']) + timedelta(days=1)).strftime(
                     "%Y-%m-%d 00:00:00")),
                ('start_datetime', '<=',
                 (fields.Date.context_today(request.env['operation.operation']) + timedelta(days=1)).strftime(
                     "%Y-%m-%d 23:59:59")),
            ]
            obj = request.env['operation.operation'].sudo().search(domain)



            warn = str(self.prepare_error_msg(e))
            return request.render("daily_plan_portal.daily_plan_new_request_portal_view", {'warn_message': warn,  'operations': obj,
                'title': 'New Daily Plan'})
        return request.redirect('/daily/plan/' + str(daily_plan.id))

    def prepare_error_msg(self, e):
        msg = ''
        if hasattr(e, 'name'):
            msg += e.name
        elif hasattr(e, 'msg'):
            msg += e.msg
        elif hasattr(e, 'args'):
            msg += e.args[0]
        return msg

