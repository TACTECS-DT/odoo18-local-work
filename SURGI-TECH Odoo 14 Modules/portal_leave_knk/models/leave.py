from odoo import fields,models,api,exceptions ,_
from datetime import datetime, date, timedelta, time
from pytz import timezone, UTC
import pytz
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import base64
from odoo.exceptions import UserError
from pytz import timezone, UTC

from odoo.addons.resource.models.resource import float_to_time
import random

class ResUsers(models.Model):
    _inherit = 'res.users'
    is_portal_leave_approve = fields.Boolean('Portal Leave Approve')

    leave_portal_access = fields.Boolean('Leave Portal Access')

class EmpPortalTimeOff(models.Model):
    _inherit = "hr.leave"
    def get_attachment(self,attach,file_name1,res_id):
        file_name = file_name1

        if attach:
            Attachments = self.env['ir.attachment']
            attachment_id = Attachments.create({
                'name': file_name,
                'type': 'binary',
                'datas': attach,
                'res_model': 'hr.leave',
                'res_id': res_id,
            })
            leave_record = self.env['hr.leave'].browse(res_id)
            leave_record.supported_attachment_ids = [(4, attachment_id.id, 0)]
            return attachment_id
    def update_timeoff_portal(self, values):
        dt_from = values['from']
        dt_to = values['to']
        if dt_from:
            dt_from = datetime.strptime(dt_from, DF).date()
        if dt_to:
            dt_to = datetime.strptime(dt_to, DF).date()
        date_from_time_str = str(dt_from) + ' ' + values['request_hour_from']
        date_to_time_str = str(dt_to) + ' ' + values['request_hour_to']
        date_from = False
        date_to = False
        date_from_str = False
        date_to_str = False
        if values['request_hour_to'] and values['request_hour_from']:
            date_from_str = values['request_hour_from']
            date_to_str = values['request_hour_to']
            date_from = values['request_hour_from']
            date_to = values['request_hour_to']
            date_from = float_to_time(float(date_from))
            date_to = float_to_time(float(date_to))
            time_from_string = date_from.strftime("%H:%M:%S")
            date_to_string = date_to.strftime("%H:%M:%S")
            date_from_time_str = str(dt_from) + ' ' + time_from_string
            date_to_time_str = str(dt_to) + ' ' + date_to_string
            req_from = datetime.strptime(date_from_time_str, "%Y-%m-%d %H:%M:%S")
            req_to = datetime.strptime(date_to_time_str, "%Y-%m-%d %H:%M:%S")
        for timeoff in self:
            timeoff_values = {
                'name': values['description'],
                'holiday_status_id': int(values['timeoff_type']),
                'request_date_from': dt_from,
                'request_date_to': dt_to,
                'date_from': dt_from,
                'date_to': dt_to,
                'request_unit_half': values['half_day'],
                'request_unit_hours': values['custom_hours'],
                'request_hour_from': date_from_str,
                'request_hour_to': date_to_str,

            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._compute_date_from_to()
        return True

    @api.model
    def create_timeoff_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        emp = user.employee_id
        self = self.sudo()
        # if not (values['description'] and values['timeoff_type'] and values['from'] and values['to']):
        #     return {
        #         'errors': _('All fields are required !')
        #     }
        date_from = False
        date_to = False
        req_from = False
        req_to = False
        date_from_str = False
        date_to_str = False
        print('ssss',str(values['to']))
        if 'attachment_2' in values:
            attachment_2 = values['attachment_2']
            file_name2 = values['file_name2']


        if values['request_hour_to'] and values['request_hour_from']:
            date_from_str = values['request_hour_from']
            date_to_str = values['request_hour_to']
            date_from = values['request_hour_from']
            date_to = values['request_hour_to']
            date_from = float_to_time(float(date_from))
            date_to = float_to_time(float(date_to))
            time_from_string = date_from.strftime("%H:%M:%S")
            date_to_string = date_to.strftime("%H:%M:%S")
            date_from_time_str = str(values['from']) + ' ' + time_from_string
            date_to_time_str = str(values['to']) + ' ' + date_to_string
            req_from = datetime.strptime(date_from_time_str, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
            req_to = datetime.strptime(date_to_time_str, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)

        values = {
            'name': values['description'],
            # 'employee_ids':  [(4, 0, 5)],
            'employee_id': user.employee_id.id,
            'holiday_status_id': int(values['timeoff_type']),
            'request_date_from': values['from'],
            'request_date_to': values['to'],
            'date_from': values['from'],
            'date_to': values['to'],
            'request_unit_half': values['half_day'],
            'request_unit_hours': values['custom_hours'],
            'request_hour_from': date_from_str,
            'request_hour_to': date_to_str,

        }
        tmp_leave = self.env['hr.leave'].sudo().new(values)
        tmp_leave._compute_tz()
        tmp_leave._compute_tz_mismatch()
        # tmp_leave._compute_number_of_days()
        # tmp_leave._compute_number_of_hours_display()
        # tmp_leave._check_date()
        # tmp_leave._get_number_of_days()
        # tmp_leave.date_from_onchange()
        tmp_leave._compute_date_from_to()
        values = tmp_leave._convert_to_write(tmp_leave._cache)

        print("valus",values)

        mytimeoff = self.env['hr.leave'].sudo().create(values)
        if attachment_2:
            attachment_id = self.get_attachment( attachment_2, file_name2, mytimeoff.id)
        return {
            'id': mytimeoff.id
        }



class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    leave_manager_id = fields.Many2one(
        'res.users', string='Time Off',
        compute='_compute_leave_manager', store=True, readonly=False, domain="[]",
        help='Select the user responsible for approving "Time Off" of this employee.\n'
             'If empty, the approval is done by an Administrator or Approver (determined in settings/users).')


    @api.depends('parent_id')
    def _compute_leave_manager(self):
        for employee in self:
            previous_manager = employee._origin.parent_id.user_id.id
            manager = employee.parent_id.user_id
            if manager and employee.leave_manager_id == previous_manager or not employee.leave_manager_id:
                employee.leave_manager_id = manager
            elif not employee.leave_manager_id:
                employee.leave_manager_id = False

    @api.model
    def create(self, values):
        # Your custom code goes here
        if 'parent_id' in values:
            manager = self.env['hr.employee'].browse(values['parent_id']).user_id
            values['leave_manager_id'] = values.get('leave_manager_id', manager.id)
        if 'leave_manager_id' in values:
            if self.env['res.users'].browse(values['leave_manager_id']).has_group('base.group_portal'):
                pass
        # Call the parent class's method with 'super()'
        return models.Model.create(self, values)

    def write(self, values):
        if 'leave_manager_id' in values:
            if self.env['res.users'].browse(values['leave_manager_id']).has_group('base.group_portal'):
                pass
        if 'parent_id' in values:
            manager = self.env['hr.employee'].browse(values['parent_id']).user_id
            if manager:
                to_change = self.filtered(lambda e: e.leave_manager_id == e.parent_id.user_id or not e.leave_manager_id)
                to_change.write({'leave_manager_id': values.get('leave_manager_id', manager.id)})

        old_managers = self.env['res.users']
        # if 'leave_manager_id' in values:
        #     old_managers = self.mapped('leave_manager_id')
        #     if values['leave_manager_id']:
        #         old_managers -= self.env['res.users'].browse(values['leave_manager_id'])
        #         approver_group = self.env.ref('hr_holidays.group_hr_holidays_responsible', raise_if_not_found=False)
        #         if approver_group:
        #             approver_group.sudo().write({'users': [(4, values['leave_manager_id'])]})

        res = models.Model.write(self, values)
        # remove users from the Responsible group if they are no longer leave managers
        old_managers._clean_leave_responsible_users()

        if 'parent_id' in values or 'department_id' in values:
            today_date = fields.Datetime.now()
            hr_vals = {}
            if values.get('parent_id') is not None:
                hr_vals['manager_id'] = values['parent_id']
            if values.get('department_id') is not None:
                hr_vals['department_id'] = values['department_id']
            holidays = self.env['hr.leave'].sudo().search(
                ['|', ('state', 'in', ['draft', 'confirm']), ('date_from', '>', today_date),
                 ('employee_id', 'in', self.ids)])
            holidays.write(hr_vals)
            allocations = self.env['hr.leave.allocation'].sudo().search(
                [('state', 'in', ['draft', 'confirm']), ('employee_id', 'in', self.ids)])
            allocations.write(hr_vals)
        return res


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, values):
        if not values.get('resource_id'):
            resource_vals = {'name': values.get(self._rec_name)}
            tz = (values.pop('tz', False) or
                  self.env['resource.calendar'].browse(values.get('resource_calendar_id')).tz)
            if tz:
                resource_vals['tz'] = tz
            resource = self.env['resource.resource'].create(resource_vals)
            values['resource_id'] = resource.id
        if 'parent_id' in values:
            manager = self.env['hr.employee'].browse(values['parent_id']).user_id
            values['leave_manager_id'] = values.get('leave_manager_id', manager.id)

        # Call the parent class's method with 'super()'
        return super(HrEmployee, self).create(values)
