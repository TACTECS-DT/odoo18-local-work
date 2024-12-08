# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
RULE = {'weekend':'weekend','holiday':'holiday','workday':'workday'}


def make_aware(dt):
    """ Return ``dt`` with an explicit timezone, together with a function to
        convert a datetime to the same (naive or aware) timezone as ``dt``.
    """
    if dt.tzinfo:
        return dt, lambda val: val.astimezone(dt.tzinfo)
    else:
        return dt.replace(tzinfo=utc), lambda val: val.astimezone(utc).replace(tzinfo=None)


def string_to_datetime(value):
    """ Convert the given string value to a datetime in UTC. """
    return utc.localize(fields.Datetime.from_string(value))


def datetime_to_string(dt, tz):
    """ Convert the given datetime (converted in UTC) to a string value. """
    return fields.Datetime.to_string(dt.astimezone(tz))


def float_to_time(c_time):
    """ Convert a number of hours into a time object. """
    minutes = int((c_time - int(c_time)) * 100)
    hours = int(c_time)
    if minutes > 0:
        minutes += 1
    return time(hours, minutes, 0)


def convert_time_percentage(c_time):
    minutes = c_time - int(c_time)
    hours = int(c_time)
    minutes = (minutes * 100) / 60
    return hours + minutes


def _boundaries(intervals, opening, closing):
    """ Iterate on the boundaries of intervals. """
    for start, stop, recs in intervals:
        if start < stop:
            yield (start, opening, recs)
            yield (stop, closing, recs)


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'
    hr_calculation_start = fields.Date("hr calculation start")
    hr_calculation_end = fields.Date("hr calculation End")

    overtime_ids = fields.Many2many('hr.overtime')

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super(PayslipOverTime, self).get_inputs(contracts, date_to, date_from)
        overtime_type = self.env.ref('ohrms_overtime.hr_salary_rule_overtime')
        contract = self.contract_id
        overtime_id = self.env['hr.overtime'].search([('employee_id', '=', self.employee_id.id),
                                                      ('contract_id', '=', self.contract_id.id),
                                                      ('state', '=', 'approved'), ('payslip_paid', '=', False)])
        hrs_amount = overtime_id.mapped('cash_hrs_amount')
        day_amount = overtime_id.mapped('cash_day_amount')
        cash_amount = sum(hrs_amount) + sum(day_amount)
        if overtime_id:
            self.overtime_ids = overtime_id
            input_data = {
                'name': overtime_type.name,
                'code': overtime_type.code,
                'amount': cash_amount,
                'contract_id': contract.id,
            }
            res.append(input_data)
        return res

    def get_overtime_hours(self):
        self.ensure_one()
        overtime_ids = self.env['hr.overtime'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                       ('contract_id', '=', self.contract_id.id),
                                                       ('state', '=', 'f_approved'), ('payslip_paid', '=', False),('date_from','>',self.hr_calculation_start),('date_to','<',self.hr_calculation_end)])
        hours = 0
        #Edit Abd Al Aziz N_of_days = (hours / self._get_worked_day_lines_hours_per_day()) if self._get_worked_day_lines_hours_per_day() != 0 else 0

        for ovt in overtime_ids:
            if ovt.overtime_type_id.type == 'cash':
                tz = timezone(self.employee_id.tz)
                date_from = datetime.strptime(str(ovt.date_from), "%Y-%m-%d %H:%M:%S").astimezone(tz)
                time_string = str(datetime_to_string(date_from, tz)[11:16])
                date_from = float(time_string.replace(":", "."))
                print()
                if ovt.public_holiday:
                    rule = ovt.overtime_type_id.rule_line_ids.filtered(
                        lambda rule: rule.name == 'holiday')
                elif ovt.is_weekend:
                    rule = ovt.overtime_type_id.rule_line_ids.filtered(
                        lambda rule: rule.name == 'weekend')
                else:
                    rule = ovt.overtime_type_id.rule_line_ids.filtered(
                        lambda rule: rule.from_hrs <= date_from and rule.to_hrs >= date_from)
                if rule[0] and rule[0].hrs_amount > 0.0:
                    hours += ovt.days_no_tmp * rule[0].hrs_amount
                else:
                    hours += ovt.days_no_tmp
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'OT100')], limit=1)
        if not work_entry_type:
            raise UserError(_('You must set a Overtime Work type.'))
        if self._get_worked_day_lines_hours_per_day() < 0.0:
            raise UserError(_('You must add Average Hour per Day on Working Hours.'))
        N_of_days = (hours / self._get_worked_day_lines_hours_per_day()) if self._get_worked_day_lines_hours_per_day() != 0 else 0    
        self.worked_days_line_ids = [(0, 0, {
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': N_of_days,
            'number_of_hours': hours,
        })]

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id:  # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        lang = employee.sudo().address_home_id.lang or self.env.user.lang
        context = {'lang': lang}
        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        del context

        self.name = '%s - %s - %s' % (
            payslip_name,
            self.employee_id.name or '',
            format_date(self.env, self.date_from, date_format="MMMM y", lang_code=lang)
        )

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %(start)s to %(end)s.",
                start=date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1),
                end=date_to,
            )
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()
        self.get_overtime_hours()
