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


class EmployeeEvaluation(CustomerPortal):

    @http.route(['/hr/evaluation', '/hr/evaluation/page/<int:page>'], type='http', auth="user", website=True)
    def portal_all_hr_evaluation(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                              groupby='none',
                              **kw):
        user = request.env.user
        if not user.evaluation_portal_access:
            return redirect('/my/access-denied')
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        evaluation_pool = request.env['evaluation.evaluation']

        domain = [('employee_id', '=', request.env.user.employee_id.id)]

        # domain = []
        searchbar_sortings = {
            'create_date': {'label': _('Create Date'), 'order': 'create_date desc'},
            'name': {'label': _('Evaluation'), 'order': 'name desc'},
        }

        # default sortby order
        if not sortby:
            sortby = 'create_date'

        sort_order = searchbar_sortings[sortby]['order']
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state': {'input': 'state', 'label': _('Status')},
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

        #        archive_groups = self._get_archive_groups('evaluation.evaluation')
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # count for pager
        evaluation_count = evaluation_pool.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/hr/evaluation",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=evaluation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        evaluation = evaluation_pool.search(domain, order=sort_order, limit=self._items_per_page,
                                offset=pager['offset'])
        request.session['my_evaluation_history'] = evaluation.ids[:100]
        if groupby == 'state':
            grouped_evaluations = [request.env['evaluation.evaluation'].concat(*g) for k, g in
                             groupbyelem(evaluation, itemgetter('state'))]

        else:
            grouped_evaluations = [evaluation]
        print(grouped_evaluations)
        values.update({
            'date': date_begin,
            'evaluation': evaluation.sudo(),
            'page_name': 'evaluation',
            'grouped_evaluation': grouped_evaluations,
            'pager': pager,
            #            'archive_groups': archive_groups,
            'default_url': '/hr/evaluation',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'filterby': filterby,
            'sortby': sortby,
            'groupby': groupby,
            'title': 'Employee | Evaluation',

        })

        return request.render("hr_evaluation_portal.portal_hr_evaluation", values)

    def _daily_evaluation_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'evaluation': order,
            'token': access_token,
            'return_url': '/hr/evaluation',
            'bootstrap_formatting': True,
            'partner_id': request.env.user.partner_id.id,
        }

        history = request.session.get('my_evaluation_history', [])
        values.update(get_records_pager(history, order))

        # Convert the date fields from order to Python datetime objects if needed
        date_start = order.date_start if isinstance(order.date_start, datetime) else fields.Date.from_string(
            order.date_start)
        date_end = order.date_end if isinstance(order.date_end, datetime) else fields.Date.from_string(order.date_end)

        # Check if today's date is between date_start and date_end
        today = fields.Date.today()
        values['self_evaluation_active'] = date_start <= today <= date_end
        print('evaluation_active',values)
        return values


    @http.route(['/hr/evaluation/<int:request_id>'], type='http', auth="public", website=True)
    def portal_daily_evaluation_page(self, request_id, report_type=None, access_token=None, message=False, download=False, **kw):
        user = request.env.user
        if not user.evaluation_portal_access:
            return redirect('/my/access-denied')
        try:
            request_sudo = self._document_check_access('evaluation.evaluation', request_id,
                                                       access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my/home')

        if request_sudo and self._should_log_view(request_sudo, access_token):
            self._log_request_view(request_sudo, access_token)

        values = self._daily_evaluation_get_page_view_values(request_sudo, access_token, **kw)
        values['message'] = message
        return request.render('hr_evaluation_portal.requests_followup', values)

    def _should_log_view(self, request_sudo, access_token):
        now = fields.Date.today().isoformat()
        session_obj_date = request.session.get('view_request_%s' % request_sudo.id)
        return session_obj_date != now and request.env.user.share and access_token

    def _log_request_view(self, request_sudo, access_token):
        request.session['view_request_%s' % request_sudo.id] = fields.Date.today().isoformat()
        body = _('Request viewed by Employee %s', request_sudo.employee_id.name)
        _message_post_helper(
            "evaluation.evaluation",
            request_sudo.id,
            body,
            token=request_sudo.access_token,
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=request_sudo.employee_id.user_id.sudo().partner_id.ids,
        )


    @http.route(['/hr/evaluation/new'], type='http', auth="user", website=True)
    def portal_new_daily_evaluation(self, **post):
        user = request.env.user
        if not user.evaluation_portal_access:
            return redirect('/my/access-denied')
        request_date = fields.Date.today()
        daily_evaluation = request.env['evaluation.evaluation'].sudo().search([]).operation_id.ids
        domain = [
            '|', ('responsible', '=', request.env.user.id), ('operation_type.is_tender', '=', True),
            ("state", "in", ['confirm']),
            ('id', 'not in', daily_evaluation),
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
            'title': 'New Evaluation'

        }
        return request.render("daily_evaluation_portal.daily_evaluation_new_request_portal_view", vals
                              )

    @http.route(['/hr/evaluation/create'], type='http', method="POST", auth="public", website=True)
    def portal_daily_evaluation_request_insert(self, **kwargs):
        user = request.env.user
        if not user.evaluation_portal_access:
            return redirect('/my/access-denied')
        try:

            datetime_str = kwargs.get('op_start_datetime')
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            odoo_datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
            daily_evaluation = request.env['evaluation.evaluation'].sudo().create({
                'employee_name': request.env.user.id,
                'state_employee': kwargs.get('state_employee'),
                'operation_id': int(kwargs.get('operation_id')) if kwargs.get(
                    'operation_id') else False,
                'op_start_datetime':odoo_datetime_str

            })


        except Exception as e:
            daily_evaluation = request.env['evaluation.evaluation'].sudo().search([]).operation_id.ids
            domain = [
                '|', ('responsible', '=', request.env.user.id), ('operation_type.is_tender', '=', True),
                ("state", "in", ['confirm']),
                ('id', 'not in', daily_evaluation),
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
            return request.render("daily_evaluation_portal.daily_evaluation_new_request_portal_view", {'warn_message': warn,  'operations': obj,
                'title': 'New Evaluation'})
        return request.redirect('/hr/evaluation/' + str(daily_evaluation.id))

    def prepare_error_msg(self, e):
        msg = ''
        if hasattr(e, 'name'):
            msg += e.name
        elif hasattr(e, 'msg'):
            msg += e.msg
        elif hasattr(e, 'args'):
            msg += e.args[0]
        return msg

