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


class HrAttendanceSheetPortal(CustomerPortal):

    @http.route(['/hr/attendance/sheet', '/hr/attendance/sheet/page/<int:page>'], type='http', auth="user", website=True)
    def portal_all_attendance_sheet(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                              groupby='none',
                              **kw):
        user = request.env.user
        if not user.attendance_sheet_portal_access:
            return redirect('/my/access-denied')

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        attendance_sheet_pool = request.env['attendance.sheet']

        domain = [('employee_id', '=', request.env.user.employee_id.id)]

        # domain = []
        searchbar_sortings = {
            'date_to': {'label': _('End Date'), 'order': 'date_to desc'},
            'date_from': {'label': _('Date From'), 'order': 'date_from desc'},
            'create_date': {'label': _('Create Date'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name desc'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date_to'

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

        #        archive_groups = self._get_archive_groups('attendance.sheet')
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # count for pager
        attendance_sheet_count = attendance_sheet_pool.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/hr/attendance/sheet",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=attendance_sheet_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        attendance_sheet = attendance_sheet_pool.search(domain, order=sort_order, limit=self._items_per_page,
                                offset=pager['offset'])
        request.session['my_attendance_sheet_history'] = attendance_sheet.ids[:100]
        if groupby == 'state':
            grouped_attendance_sheets = [request.env['attendance.sheet'].concat(*g) for k, g in
                             groupbyelem(attendance_sheet, itemgetter('state'))]

        else:
            grouped_attendance_sheets = [attendance_sheet]
        print(grouped_attendance_sheets)
        values.update({
            'date': date_begin,
            'attendance_sheet': attendance_sheet.sudo(),
            'page_name': 'attendance_sheet',
            'grouped_attendance_sheet': grouped_attendance_sheets,
            'pager': pager,
            #            'archive_groups': archive_groups,
            'default_url': '/hr/attendance/sheet',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'filterby': filterby,
            'sortby': sortby,
            'groupby': groupby,
            'title': 'Employee | Attendance Sheet',

        })

        return request.render("hr_attendance_sheet_portal.portal_attendance_sheet", values)

    def _hr_attendance_sheet_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'attendance_sheet': order,
            'token': access_token,
            'return_url': '/hr/attendance/sheet',
            'bootstrap_formatting': True,
            'partner_id': request.env.user.partner_id.id,
        }

        history = request.session.get('my_attendance_sheet_history', [])
        values.update(get_records_pager(history, order))

        # Convert the date fields from order to Python datetime objects if needed

        return values


    @http.route(['/hr/attendance/sheet/<int:request_id>'], type='http', auth="public", website=True)
    def portal_hr_attendance_sheet_page(self, request_id, report_type=None, access_token=None, message=False, download=False, **kw):
        user = request.env.user
        if not user.attendance_sheet_portal_access:
            return redirect('/my/access-denied')

        try:
            request_sudo = self._document_check_access('attendance.sheet', request_id,
                                                       access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my/home')

        if request_sudo and self._should_log_view(request_sudo, access_token):
            self._log_request_view(request_sudo, access_token)

        values = self._hr_attendance_sheet_get_page_view_values(request_sudo, access_token, **kw)
        values['message'] = message
        return request.render('hr_attendance_sheet_portal.requests_followup', values)

    def _should_log_view(self, request_sudo, access_token):
        now = fields.Date.today().isoformat()
        session_obj_date = request.session.get('view_request_%s' % request_sudo.id)
        return session_obj_date != now and request.env.user.share and access_token

    def _log_request_view(self, request_sudo, access_token):
        request.session['view_request_%s' % request_sudo.id] = fields.Date.today().isoformat()
        body = _('Request viewed by Employee %s', request_sudo.employee_id.name)
        _message_post_helper(
            "attendance.sheet",
            request_sudo.id,
            body,
            token=request_sudo.access_token,
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=request_sudo.employee_id.user_id.sudo().partner_id.ids,
        )



    def prepare_error_msg(self, e):
        msg = ''
        if hasattr(e, 'name'):
            msg += e.name
        elif hasattr(e, 'msg'):
            msg += e.msg
        elif hasattr(e, 'args'):
            msg += e.args[0]
        return msg

