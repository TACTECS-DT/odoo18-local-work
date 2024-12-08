from odoo import models, fields, api
from datetime import date,datetime,time,timedelta
from dateutil.relativedelta import relativedelta

class HRExpenseExpiration(models.Model):
    _name = 'hr.expense.expiration'
    _rec_name = 'num_day_expire'
    _description = 'HR Expense Expiration'

    num_day_expire = fields.Integer(string="Number OF Days", required=True, )

