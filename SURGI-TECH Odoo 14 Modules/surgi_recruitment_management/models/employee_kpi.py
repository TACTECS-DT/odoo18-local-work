from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_join
from datetime import datetime


class EmployeeKPI(models.Model):
    _name = 'hr.employee.kpi'

    name = fields.Char()
    total_score = fields.Float('Total Score')
    job_id = fields.Many2one('hr.job')
    employee_id = fields.Many2one('hr.employee')
    date_from = fields.Date()
    date_to = fields.Date()

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('employee.kpi') or '/'
        return super().create(values)