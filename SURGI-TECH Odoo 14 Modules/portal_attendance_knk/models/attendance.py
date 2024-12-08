from odoo import api, fields, models, _
import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'


    def convert_float_to_hours_minutes(self,time_in_hours):
        """
        Takes a float representing time in hours and returns the equivalent
        time in hours and minutes as a string.
        """

        # Calculate the total number of minutes as an integer
        total_minutes = int(time_in_hours * 60)

        # Use divmod to get the total number of hours and remaining minutes
        hours, minutes_remaining = divmod(total_minutes, 60)

        # Format the result as a string (using zero-padding where necessary)
        hours_str = f'{hours:02d}'
        minutes_str = f'{minutes_remaining:02d}'

        return f'{hours_str}:{minutes_str}'
class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'
    multi_location_checkin = fields.Many2many(
        comodel_name='res.partner',
        relation='hr_employee_public_rel',  # The name of the relational table
        column1='hr_employee_public_id',  # The name of the column for 'hr.employee.public' in the relational table
        column2='res_partner_id',  # The name of the column for 'res.partner' in the relational table
        string='Additional Checkin Locations'
    )


class ResUser(models.Model):
    _inherit = 'res.users'

    attendance_portal_access = fields.Boolean('Attendance Portal Access')
