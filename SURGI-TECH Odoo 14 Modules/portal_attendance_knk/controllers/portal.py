# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import http, _, fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request
from odoo.tools import date_utils
from odoo.osv.expression import AND, OR
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.fields import Datetime
from werkzeug.utils import secure_filename ,redirect


class PortalMyAttendance(http.Controller):

    @http.route('/attendance', type='http', auth='user', website=True)
    def portal_my_attendance(self):
        vals = {}
        user = request.env.user
        if not user.attendance_portal_access:
            return redirect('/my/access-denied')

        return request.render('portal_attendance_knk.my_attendance_panel', vals)


class PortalAttendance(CustomerPortal):

    # ------------------------------------------------------------
    # Hr Portal Attendances
    # ------------------------------------------------------------

    def _attendances_get_page_view_values(self, hr_attendance, access_token, **kwargs):
        values = {
            'page_name': 'hr_attendance',
            'hr_attendance': hr_attendance,
        }
        return self._get_page_view_values(hr_attendance, access_token, values, 'my_attendances_history', False, **kwargs)

    def _get_searchbar_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Search in All')},
            'check_in': {'input': 'check_in', 'label': _('Search in Check In')},
            'check_out': {'input': 'check_out', 'label': _('Search in Check Out')},
        }

    def _get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('check_in', 'all'):
            search_domain = OR([search_domain, [('check_in', 'ilike', search)]])
        if search_in in ('check_out', 'all'):
            search_domain = OR([search_domain, [('check_out', 'ilike', search)]])
        return search_domain

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendance(self, page=1, date_begin=None, date_end=None, filterby=None, search=None, search_in='all', **kw):
        user = request.env.user
        if not user.attendance_portal_access:
            return redirect('/my/access-denied')

        HrAttendance = request.env['hr.attendance'].sudo()
        values = self._prepare_portal_layout_values()
        # domain = request.env['hr.attendance']._attendance_get_portal_domain()
        domain = [('employee_id.user_id.id', '=', request.env.user.id)]
        _items_per_page = 100

        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Description'), 'order': 'name'},
        }

        searchbar_inputs = self._get_searchbar_inputs()

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("create_date", ">=", Datetime.to_string(Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))), ("create_date", "<=", Datetime.to_string(Datetime.now().replace(hour=23, minute=59, second=59, microsecond=59)))]},
            'week': {'label': _('This week'), 'domain': [('create_date', '>=', date_utils.start_of(today, "week")), ('create_date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'month')), ('create_date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('create_date', '>=', date_utils.start_of(today, 'year')), ('create_date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('create_date', '>=', quarter_start), ('create_date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('create_date', '>=', date_utils.start_of(last_week, "week")), ('create_date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('create_date', '>=', date_utils.start_of(last_month, 'month')), ('create_date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('create_date', '>=', date_utils.start_of(last_year, 'year')), ('create_date', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])
        # import pdb;pdb.set_trace()
        if search and search_in:
            domain += self._get_search_domain(search_in, search)

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        attendances_count = HrAttendance.search_count(domain)
        # count for pager
        # pager
        pager = portal_pager(
            url="/my/attendance",
            url_args={'search_in': search_in, 'search': search, 'filterby': filterby},
            total=attendances_count,
            page=page,
            step=_items_per_page
        )
        # content according to pager and archive selected
        attendances = HrAttendance.search(domain, limit=self._items_per_page, offset=pager['offset'])
        for a in attendances:
            round(a.worked_hours, 2)
        request.session['my_attendances_history'] = attendances.ids[:100]

        values.update({
            # 'date': date_begin,
            'attendances': attendances,
            'page_name': 'hr_attendance',
            'pager': pager,
            'default_url': '/my/attendance',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'searchbar_inputs': searchbar_inputs,
        })
        return request.render("portal_attendance_knk.portal_my_attendances", values)

    @http.route(['/my/attendance/<int:attendance_id>'], type='http', auth="public", website=True)
    def portal_my_attendance_detail(self, attendance_id, access_token=None, report_type=None, download=False, **kw):
        user = request.env.user
        if not user.attendance_portal_access:
            return redirect('/my/access-denied')

        try:
            hr_attendance = self._document_check_access('hr.attendance', attendance_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=hr_attendance, report_type=report_type, report_ref='account.account_invoices', download=download)

        values = self._attendance_get_page_view_values(hr_attendance, access_token, **kw)
        acquirers = values.get('acquirers')
        if acquirers:
            country_id = values.get('partner_id') and values.get('partner_id')[0].country_id.id
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(hr_attendance.amount_residual, hr_attendance.currency_id, country_id)

        return request.render("portal_attendance_knk.portal_attendance_page", values)
