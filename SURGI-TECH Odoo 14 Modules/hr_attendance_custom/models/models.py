from odoo import models, api

class CustomHrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def button_attendance_action(self):
        # domain = [('employee_id.user_id', '=', self.env.user.id)]

        if self.env.user.has_group('hr_attendance.group_hr_attendance_user'):
            return {
                'name': 'Attendances',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.attendance',
                'type': 'ir.actions.act_window',
                'domain': [],
            }
