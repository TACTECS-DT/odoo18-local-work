# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).


from odoo import http, _
from operator import itemgetter
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time
from collections import OrderedDict
from collections import namedtuple
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime , timedelta
from odoo.tools import groupby as groupbyelem
from werkzeug.utils import secure_filename, redirect

DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')


class PortalLeaveKnk(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if request.env.user._is_admin():
            domain = []
        else:
            domain = [('employee_id', '=', request.env.user.employee_id.id)]
        counters.append('leave_count')
        if 'leave_count' in counters:
            leave_count = request.env['hr.leave'].search_count(domain) \
                if request.env['hr.leave'].check_access_rights('read', raise_exception=False) else 0
            if not leave_count:
                leave_count='0'
            values['leave_count'] = leave_count
        return values
    def _get_searchbar_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Search in All')},
            'employee': {'input': 'employee', 'label': _('Search in Employee')},
            'leave_type': {'input': 'leave_type', 'label': _('Search in Leave Type')},
            'reason': {'input': 'reason', 'label': _('Search in Reason')},
        }

    def _get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('name', 'all'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        if search_in in ('employee', 'all'):
            search_domain = OR([search_domain, [('employee_id', 'ilike', search)]])
        if search_in in ('leave_type', 'all'):
            search_domain = OR([search_domain, [('holiday_status_id', 'ilike', search)]])
        if search_in in ('reason', 'all'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        return search_domain

    def _get_searchbar_sortings(self):
        return {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc', 'sequence': 1},
            'date_from': {'label': _('Start Date'), 'order': 'date_from desc', 'sequence': 2 },
            'date_to': {'label': _('End Date'), 'order': 'date_to desc', 'sequence': 3},
            'leave_type': {'label': _('Leave Type'), 'order': 'holiday_status_id', 'sequence': 4},
            'status': {'label': _('Status'), 'order': 'state', 'sequence': 5},
        }

    def _get_searchbar_groupby(self):
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'leave_type': {'input': 'leave_type', 'label': _('Leave Type'), 'order': 2},
            'status': {'input': 'status', 'label': _('Status'), 'order': 3},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_groupby_mapping(self):
        return {
            'leave_type': 'holiday_status_id',
            'status': 'state',
        }

    def _get_order(self, order, groupby):
        groupby_mapping = self._get_groupby_mapping()
        field_name = groupby_mapping.get(groupby, '')
        if not field_name:
            return order
        return '%s, %s' % (field_name, order)

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_payslip(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        user = request.env.user
        if not user.leave_portal_access:
            return redirect('/my/access-denied')

        values = self._prepare_portal_layout_values()
        Leave = request.env['hr.leave'].sudo()
        _items_per_page = 20

        if request.env.user._is_admin():
            domain = []
        else:
            domain = [('employee_id', '=', request.env.user.employee_id.id)]
        searchbar_sortings = self._get_searchbar_sortings()
        searchbar_groupby = self._get_searchbar_groupby()
        searchbar_inputs = self._get_searchbar_inputs()
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': domain},
            'approved': {'label': _('Approved Time Off'), 'domain': [('state', '=', 'validate')]},
            'to_approve': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
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

        leave_count = Leave.search_count(domain)

        pager = portal_pager(
            url="/my/leaves",
            url_args={'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby, 'sortby': sortby},
            total=leave_count,
            page=page,
            step=_items_per_page
        )

        order = self._get_order(order, groupby)
        leaves = Leave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_leave_history'] = leaves.ids[:100]

        groupby_mapping = self._get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_leaves = [Leave.concat(*g) for k, g in groupbyelem(leaves, itemgetter(group))]
        else:
            grouped_leaves = [leaves]

        allocations = request.env['hr.leave.allocation'].sudo().search([('employee_id', '=', request.env.user.employee_id.id), ('state', '=', 'validate')])
        allocation_data = allocations.holiday_status_id.get_days_all_request()
        leave_allocations = {}
        for data in allocation_data:
            leave_allocations[data[0]] = [data[1]['virtual_remaining_leaves'], data[1]['request_unit']]
        values.update({
            'grouped_leaves': grouped_leaves,
            'page_name': 'leave',
            'pager': pager,
            'default_url': '/my/leaves',
            'search_in': search_in,
            'search': search,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'allocations': leave_allocations,
        })
        return request.render("portal_leave_knk.portal_my_leave_list", values)

    @http.route(['/create/leave'], type='http', auth="user", website=True)
    def apply_leave(self, **post):
        user = request.env.user
        if not user.leave_portal_access:
            return redirect('/my/access-denied')

        employee = request.env.user.employee_id
        domain = ['|', ('allocation_type', '=', 'no'), '&', ('valid', '=', True), '&', ('virtual_remaining_leaves', '>', 0), ('max_leaves', '>', '0')]
        leave_type = request.env['hr.leave.type'].sudo().search(domain)
        values = {
            'employee': employee,
            'leave_types': leave_type,
            'page_name': 'create_leave',
        }
        return request.render("portal_leave_knk.portal_apply_leave", values)

    @http.route(['/save/leave'], type='http', auth="user", website=True)
    def save_leave(self, **post):
        user = request.env.user
        if not user.leave_portal_access:
            return redirect('/my/access-denied')

        field_list = ['start_date', 'end_date', 'reason', 'leave_type']
        value = []
        domain = ['|', ('allocation_type', '=', 'no'), '&', ('valid', '=', True), '&', ('virtual_remaining_leaves', '>', 0), ('max_leaves', '>', '0')]
        leave_type = request.env['hr.leave.type'].sudo().search(domain)
        start_date = datetime.strptime(post.get('start_date'), DF)
        end_date = datetime.strptime(post.get('end_date'), DF)
        employee = request.env.user.employee_id
        for key in post:
            value.append(post[key])
        if any([field not in post.keys() for field in field_list]) or not post:
            post.update({
                'employee': employee,
                'leave_types': leave_type,
                'page_name': 'create_leave',
                'error': 'Some Required Fields are Missing.'
            })
            return request.render("portal_leave_knk.portal_apply_leave", post)
        resource_calendar_id = employee.resource_calendar_id
        domain_1 = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
        attendances = request.env['resource.calendar.attendance'].read_group(domain_1, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)
        attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= start_date.weekday()), attendances[0] if attendances else self.default_value)
        attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= end_date.weekday()), attendances[-1] if attendances else self.default_value)
        hour_from = float_to_time(attendance_from.hour_from)
        hour_to = float_to_time(attendance_to.hour_to)
        start_date = timezone(employee.tz).localize(datetime.combine(start_date.date() , hour_from)).astimezone(UTC).replace(tzinfo=None) - timedelta(hours=1)
        end_date = timezone(employee.tz).localize(datetime.combine(end_date.date(), hour_to)).astimezone(UTC).replace(tzinfo=None) - timedelta(hours=2)

        print("hour_from",hour_from)
        print("hour_to",hour_to)
        print("start_date",start_date)
        print("end_date",end_date)
        # raise UserWarning()
        error = False
        employee = request.env.user.employee_id
        if start_date.date() > end_date.date():
            error = 'The start date must be anterior to the end date.'

        domain = [
            ('date_from', '<', end_date),
            ('date_to', '>', start_date),
            ('employee_id', '=', employee.id),
            ('state', 'not in', ['cancel', 'refuse']),
        ]
        nholidays = request.env['hr.leave'].sudo().search(domain)
        if nholidays:
            error = 'You can not set 2 time off that overlaps on the same day for the same employee.'
        if error:
            post = {'employee': employee,
                    'leave_types': leave_type,
                    'page_name': 'create_leave',
                    'error': error}
            return request.render("portal_leave_knk.portal_apply_leave", post)
        vals = {
            'employee_id': request.env.user.employee_id.id,
            'holiday_status_id': int(post.get('leave_type')),
            'date_from': start_date,
            'request_date_from': start_date,
            'request_date_to': end_date,
            'date_to': end_date,
            'request_unit_half': post.get('request_unit_half') if post.get('request_unit_half') else False,
            'request_unit_hours': post.get('request_unit_hours') if post.get('request_unit_hours') else False,
            'request_hour_from': post.get('request_hour_from') if post.get('request_hour_from') else False,
            'request_hour_to': post.get('request_hour_to') if post.get('request_hour_to') else False,
            'name': post.get('reason'),
        }
        if post.get('request_unit_hours'):
            hour_from = float(post.get('request_hour_from')) -1
            hour_to = float(post.get('request_hour_to')) - 1
            vals.update({'request_hour_from': str(hour_from),'request_hour_to':(hour_to)})
            tmp_leave = request.env['hr.leave'].sudo().new(vals)
            tmp_leave._compute_date_from_to()
            vals = tmp_leave._convert_to_write(tmp_leave._cache)
            mytimeoff = request.env['hr.leave'].sudo().create(vals)
        else:
            mytimeoff = request.env['hr.leave'].sudo().create(vals)

        return request.redirect('/my/leaves')
    @http.route('/approve_leave/<int:leave_id>', type='http', auth='public', website=True, methods=['GET'])
    def approve_leave(self, leave_id, **kwargs):
        user = request.env.user
        if not user.leave_portal_access:
            return redirect('/my/access-denied')

        leave_to_approve = request.env['hr.leave'].sudo().browse(leave_id)
        if leave_to_approve:
            leave_to_approve.action_approve()
        return request.redirect('/my/leaves')

    @http.route('/refuse_leave/<int:leave_id>', type='http', auth='public', website=True, methods=['GET'])
    def refuse_leave(self, leave_id, **kwargs):
        user = request.env.user
        if not user.leave_portal_access:
            return redirect('/my/access-denied')

        leave_to_refuse = http.request.env['hr.leave'].sudo().browse(leave_id)
        if leave_to_refuse:
            leave_to_refuse.action_refuse()
        return http.request.redirect('/my/leaves')


    @http.route(['''/my/leave/<model('hr.leave'):timeoff>'''], type='http', auth="user", website=True)
    def portal_my_timeoff(self, timeoff, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        holiday_domain = ([])
        holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        return request.render(
            "portal_leave_knk.portal_my_leave", {
                'timeoff': timeoff,
                'holiday_types': holiday_type_ids.with_context({'employee_id': emp and emp.id or False}).name_get(),
                'page_name': 'leave',
                'emp_id': emp and emp.id or False
            })
