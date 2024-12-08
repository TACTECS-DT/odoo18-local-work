import pytz
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY,make_aware, datetime_to_string, string_to_datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

class AttendanceSheet_Inhert(models.Model):
    _inherit = ['attendance.sheet']

    needReview=fields.Boolean(string="Need Review")
    
    def action_req_overtime(self):
        print("x")

    def get_attendances(self):
        print("x")

        res=super(AttendanceSheet_Inhert,self).get_attendances()
        if self.contract_id.random_shift:
            defaultcotract=self.contract_id.resource_calendar_id
            for x in  self.line_ids:
                if x.resource_calendar_id==defaultcotract and  x.ac_sign_in > 0 and x.getReviewed!= True and x.worked_hours >  1.5 :
                    self.needReview=True
                    x.needReview=True
                    x.getReviewed=False
                    #break
        print("yy")
class AttenendenceSheetLine_inhert(models.Model):
    _inherit=['attendance.sheet.line']
    needReview=fields.Boolean("Need Review")
    getReviewed=fields.Boolean("Get Reviewed")
    emp_id = fields.Many2one('hr.employee', string='Partner', related='att_sheet_id.employee_id')
    # def action_req_overtime(self):
    #     print("y")
    
#     @api.onchange('needReview')
#     def needreview_action(self):
#         if self.needReview:
#                 self.getReviewed=False
#         else:
#            self.getReviewed=True
            

    
