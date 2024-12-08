from ast import excepthandler
from calendar import month
from odoo import models, fields, api
import socket
import json 
import psycopg2
import sys
from datetime import datetime, timedelta
import googlemaps
from googlegeocoder import GoogleGeocoder
from geopy.geocoders import Nominatim
from odoo.exceptions import UserError
import requests
import re
import datetime
import pytz
class HolidaysRequestInhert(models.Model):
    _inherit="hr.leave"
    request_unit_checklocation=fields.Boolean('Check Location',  store=True, readonly=False)
    checkin_location=fields.Char("Check In Location")
    checkout_location=fields.Char("Check Out Location")
    checkin_lat=fields.Char(string="Latitude")
    checkin_long=fields.Char(string="Longtitude")
    checkout_lat=fields.Char(string="Latitude")
    checkout_long=fields.Char(string="longtitude")
    def todraft(self):
        for rec in self:
            rec.action_refuse()
            rec.action_draft()
    # @api.model
    def adjusthrtime(self):
        for rec in self:
            tz = pytz.timezone(rec.employee_id.tz)
            datefrom=rec.date_from.replace(hour=00, minute=00).replace(tzinfo=tz).astimezone(
            pytz.utc).replace(tzinfo=None)+timedelta(minutes=5)
            rec.date_from=datefrom
            dateto=rec.date_to.replace(hour=23, minute=59).replace(tzinfo=tz).astimezone(
            pytz.utc).replace(tzinfo=None)+timedelta(minutes=5)
            rec.date_to=dateto
 
    @api.onchange('request_unit_checklocation')
    def checin_loc(self):
        if self.checkin_location:
            self.request_unit_half=False
            self.request_unit_hours=False
    def action_approve(self):
        if self.request_unit_checklocation and  (not self.checkin_location or not self.checkout_location ):
           raise UserError('This Request Need CheckIn and CheckOut Location')
        super(HolidaysRequestInhert,self).action_approve()        
            
    @api.model_create_multi
    def create(self,args):
        emp=args[0]['employee_id']
        holiday=args[0]['holiday_status_id']
        employee=self.env['hr.employee'].search([('id','=',emp)])
        holiday=self.env['hr.leave.type'].search([('id','=',holiday)])
        if holiday.isrestrectemp or holiday.isrestrectdep:
                
                if employee not in holiday.restrictedemp and  employee.department_id not in holiday.restricteddep:
                   raise UserError('This Employee not authorized to take this type of timeoff')

        return super(HolidaysRequestInhert,self).create(args)


    # @api.depends('number_of_days')
    # def _compute_number_of_hours_display(self):
       
    #     print("yy")
    #     res=super(HolidaysRequestInhert,self)._compute_number_of_hours_display()
    #     # for holiday in self:
    #     #     calendar = holiday._get_calendar()
    #     #     if holiday.date_from and holiday.date_to:
    #     #         # Take attendances into account, in case the leave validated
    #     #         # Otherwise, this will result into number_of_hours = 0
    #     #         # and number_of_hours_display = 0 or (#day * calendar.hours_per_day),
    #     #         # which could be wrong if the employee doesn't work the same number
    #     #         # hours each day
    #     #         if holiday.state == 'validate':
    #     #             start_dt = holiday.date_from
    #     #             end_dt = holiday.date_to
    #     #             if not start_dt.tzinfo:
    #     #                 start_dt = start_dt.replace(tzinfo=UTC)
    #     #             if not end_dt.tzinfo:
    #     #                 end_dt = end_dt.replace(tzinfo=UTC)
    #     #             resource = holiday.employee_id.resource_id
    #     #             intervals = calendar._attendance_intervals_batch(start_dt, end_dt, resource)[resource.id] \
    #     #                         - calendar._leave_intervals_batch(start_dt, end_dt, None)[False]  # Substract Global Leaves
    #     #             number_of_hours = sum((stop - start).total_seconds() / 3600 for start, stop, dummy in intervals)
    #     #         else:
    #     #             number_of_hours = holiday._get_number_of_days(holiday.date_from, holiday.date_to, holiday.employee_id.id)['hours']
    #     #         holiday.number_of_hours_display = number_of_hours or (holiday.number_of_days * (calendar.hours_per_day or HOURS_PER_DAY))
    #     #     else:
    #     #         holiday.number_of_hours_display = 0
    # @api.depends('number_of_hours_display', 'number_of_days_display')
    # def _compute_duration_display(self):
        
    #     print("x")
    #     res=super(HolidaysRequestInhert,self)._compute_duration_display()
    #     # for leave in self:
    #     #     leave.duration_display = '%g %s' % (
    #     #         (float_round(leave.number_of_hours_display, precision_digits=2)
    #     #         if leave.leave_type_request_unit == 'hour'
    #     #         else float_round(leave.number_of_days_display, precision_digits=2)),
    #     #         _('hours') if leave.leave_type_request_unit == 'hour' else _('days'))


    # @api.depends('date_from', 'date_to', 'employee_id')
    # def _compute_number_of_days(self):
    #     print("x")
    #     res=super(HolidaysRequestInhert,self)._compute_number_of_days()
    #     # for holiday in self:
    #     #     if holiday.date_from and holiday.date_to:
    #     #         holiday.number_of_days = holiday._get_number_of_days(holiday.date_from, holiday.date_to, holiday.employee_id.id)['days']
    #     #     else:
    #     #         holiday.number_of_days = 0
    @api.model
    def check_in_mission_loc(self, *kwargs):
        
        active_id=kwargs[0]['active_id']
        active_leave=self.env['hr.leave'].search([('id','=',active_id)])
        
        res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        script_key = res_config.google_api_key
        if ('lat' or 'long') in kwargs[0]:
            lati = kwargs[0]['lat']
            longti = kwargs[0]['long']
            geocoder = GoogleGeocoder(str(script_key))
            geolocator = Nominatim(user_agent=str(script_key))
            reverse = geolocator.reverse((lati, longti))
            address = str(reverse[0])
            if active_leave.checkin_location:
                active_leave.checkout_location=address
                active_leave.checkout_lat=lati
                active_leave.checkout_long=longti
                currenttime=datetime.datetime.now()
                currenttime=currenttime.replace(second=0,microsecond=0)
                duration=round((currenttime-active_leave.date_from).total_seconds() /3600,2)
                calendar = active_leave._get_calendar()
                nodays=round((duration/calendar.hours_per_day),1)
                self.env.cr.execute("""UPDATE hr_leave SET date_to='"""+str(currenttime)+"""',number_of_days="""+str(nodays)+""",duration_display="""+str(duration)+"""  WHERE id=%d"""%active_leave.id)
            else:
                active_leave.checkin_location=address
                active_leave.checkin_lat=lati
                active_leave.checkin_long=longti
                currenttime=datetime.datetime.now()
                currenttime=currenttime.replace(second=0,microsecond=0)
                self.env.cr.execute("""UPDATE hr_leave SET date_from='"""+str(currenttime)+"""' ,date_to='"""+str(currenttime)+"""',number_of_days=0,duration_display=0  WHERE id=%d"""%active_leave.id)
            
            print("")
            # dfrom=datetime.timedelta(
            #     year=datetime.datetime.now().,
            #     month=datetime.datetime.now().month,
            #     days=datetime.datetime.now().day,
            #     hours=datetime.datetime.now().hour,
            #     minutes=datetime.datetime.now().minute)
            
            # try:
            #     active_leave.sudo().write({'date_from': currenttime})
            #     active_leave.date_to=currenttime
                
            # except psycopg2.Error:
            #     UserError(psycopg2.Error)
            # except psycopg2.IntregrityError:
            #     UserError(psycopg2.IntregrityError)
             
            
            
class AhHrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    _description = 'leavetypes'
    isrestrectemp=fields.Boolean(string="Restricted By Emp.")
    #restrictedemp=fields.One2many(string="Employees",comodel_name="hr.employee",inverse_name="empleavetyperestriction")
    restrictedemp=fields.Many2many(string="Employees",comodel_name="hr.employee")
    
    isrestrectdep=fields.Boolean(string="Restricted By Dep.")
   # restricteddep=fields.One2many(string="Departments",comodel_name="hr.department",inverse_name="depleavetyperestriction")
    restricteddep=fields.Many2many(string="Departments",comodel_name="hr.department")


 
          
            


        
