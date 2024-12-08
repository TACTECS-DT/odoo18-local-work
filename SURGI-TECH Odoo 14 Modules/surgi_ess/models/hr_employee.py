from odoo import models, fields, api, _
import base64


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    # personal_device_mac_address = fields.Char(string='Mac Address-Mobile',)
    # office_device_mac_address = fields.Char(string='Mac Address-Office',)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # personal_device_mac_address = fields.Char(string='Mac Address-Mobile',)
    # office_device_mac_address = fields.Char(string='Mac Address-Office',)

    def action_unfollow(self):
        pass


    def action_employee_add_attachment(self):
        return {
                'name': _('Add Attachment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'employee.profile.attachment.wizard',
                'target': 'new',
                'context': {'default_employee_id': self.id}
            }



# class HrhiringReq(models.Model):
#     _inherit = 'hiring.request'

# class Grade(models.Model):
#     _inherit = 'grade.grade'
