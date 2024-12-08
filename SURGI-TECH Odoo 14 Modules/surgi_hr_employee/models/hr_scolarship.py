from odoo import api, _
from odoo import fields
from odoo import models
from odoo.models import _logger
from odoo.exceptions import ValidationError
from dateutil import relativedelta
import datetime

class stage_scholarship(models.Model):
    _name = 'scholarship.stage'
    # _rec_name = 'name'

    name = fields.Char(string="المرحلة الدراسية")

class Employee_relations(models.Model):
    _name ='emp.relations'

    employee_realtion_id = fields.Many2one('hr.employee',string='Employee Relations')
    emp_family_name = fields.Char(string="Name")
    attachment_family = fields.Binary( string="Attachment")

    employee_relation = fields.Selection([('wifes', 'Wife'), ('husbands', 'Husband'), ('sons', 'Son'), ('daughters', 'Daughter')])
    emp_family_gender = fields.Char(compute='_auto_gender_generate', string="Gender",store=True)

    bdate = fields.Date(string="Date Of Birth")
    relation_age = fields.Char(string="Age", compute="_get_age_from_relation", store=True)





    @api.depends("employee_relation")
    def _auto_gender_generate(self):
        for rec in self:
            if rec.employee_relation == "wifes":
                rec.emp_family_gender = 'Female'
            elif rec.employee_relation == "husbands":
                rec.emp_family_gender = 'Male'
            elif rec.employee_relation == "sons":
                rec.emp_family_gender = 'Male'
            elif rec.employee_relation == "daughters":
                rec.emp_family_gender = 'Female'
            else:
                rec.emp_family_gender = "Not Providated...."


    @api.depends("bdate")
    def _get_age_from_relation(self):
        """Age Calculation"""
        today_date = datetime.date.today()
        for stud in self:
            if stud.bdate:
                """
                Get only year.
                """
                # bdate = fields.Datetime.to_datetime(stud.bdate).date()
                # total_age = str(int((today_date - bdate).days / 365))
                # stud.relation_age = total_age


                currentDate = datetime.date.today()

                deadlineDate= fields.Datetime.to_datetime(stud.bdate).date()
                # print (deadlineDate)
                daysLeft = currentDate - deadlineDate
                # print(daysLeft)

                years = ((daysLeft.total_seconds())/(365.242*24*3600))
                yearsInt=int(years)

                months=(years-yearsInt)*12
                monthsInt=int(months)

                days=(months-monthsInt)*(365.242/12)
                daysInt=int(days)

                hours = (days-daysInt)*24
                hoursInt=int(hours)

                minutes = (hours-hoursInt)*60
                minutesInt=int(minutes)

                seconds = (minutes-minutesInt)*60
                secondsInt =int(seconds)

                stud.relation_age = '{0:d} years, {1:d}  months, {2:d}  days,   \
                old.'.format(yearsInt,monthsInt,daysInt,hoursInt)
            else:
                stud.relation_age = "Not Providated...."


class Employee_scholarship(models.Model):
    _name ='emp.scholarship'

    name = fields.Many2one('hr.employee',string='اسم الموظف')
    # employee_scholarship_code = fields.Many2one('hr.employee', related='employee_id.registration_number' ,string='Employee Code')
    employee_scholarship_code = fields.Char(string="كود الموظف",
                                      related='name.registration_number',store=True)
    employee_scholarship_wl = fields.Char(string="منطقة العمل",
                                      related='name.work_location', store=True)
    emp_scholarship_name = fields.Char(string="أسم الابن")
    # attachment_ids = fields.Binary( string="Attachment")
    attachment_brith = fields.Binary( string="شهادة الميلاد")
    attachment_grade = fields.Binary( string="شهادة اخر مرحلة")
    attachment_other = fields.Binary( string="اخري")

    employee_relation = fields.Selection([ ('sons', 'ابن'), ('daughters', 'أبنة')])
    emp_family_gender = fields.Char(compute='_auto_gender_generate', string="النوع",store=True)

    bdate = fields.Date(string="تاريخ الميلاد")
    relation_age = fields.Char(string="السن", compute="_get_age_from_relation", store=True)
    school_type = fields.Selection([ ('ar', 'عربي'),('gr', 'ألماني'), ('fr', 'فرنساوي'), ('en', 'انجليزي'),('co', 'تجاري'),('de', 'تجريبي'),('cr', 'صنايع') ])
    school_stage = fields.Many2one('scholarship.stage' ,string="المرحلة الدراسية")
    school_year = fields.Selection([ ('one', '1'), ('two', '2'),('three', '3'), ('four', '4'),('five', '5'), ('six', '6')])
    school_percentage = fields.Char(string="نسبة النجاح لأخر مرحلة دارسية")


    @api.model
    def create_scholarship_record(self, values):
        values['name'] = self.env.user.employee_id.id
        return self.create(values).id

    @api.model
    def edit_scholarship_record(self, values):
        scholarship_id = values.pop('scholarship_id')
        scholarship = self.browse(scholarship_id)

        if scholarship:
            scholarship.write(values)
        return {'id': scholarship.id}

    @api.depends("employee_relation")
    def _auto_gender_generate(self):
        for rec in self:

            if rec.employee_relation == "sons":
                rec.emp_family_gender = 'ذكر'
            elif rec.employee_relation == "daughters":
                rec.emp_family_gender = 'انثي'
            else:
                rec.emp_family_gender = "Not Providated...."


    @api.depends("bdate")
    def _get_age_from_relation(self):
        """Age Calculation"""
        # today_date = datetime.date.today()
        for stud in self:
            if stud.bdate:
                """
                Get only year.
                """

                currentDate = datetime.date.today()

                deadlineDate= fields.Datetime.to_datetime(stud.bdate).date()
                # print (deadlineDate)
                daysLeft = currentDate - deadlineDate
                # print(daysLeft)

                years = ((daysLeft.total_seconds())/(365.242*24*3600))
                yearsInt=int(years)

                months=(years-yearsInt)*12
                monthsInt=int(months)

                days=(months-monthsInt)*(365.242/12)
                daysInt=int(days)

                hours = (days-daysInt)*24
                hoursInt=int(hours)

                minutes = (hours-hoursInt)*60
                minutesInt=int(minutes)

                seconds = (minutes-minutesInt)*60
                secondsInt =int(seconds)

                stud.relation_age = '{0:d} years, {1:d}  months,   \
                old.'.format(yearsInt,monthsInt,daysInt,hoursInt)
            else:
                stud.relation_age = "Not Providated...."




