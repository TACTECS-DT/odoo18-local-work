# \**
# * ************************************
# * @package    system-one/collect_return_wizard
# * @author     ibralsmn
# * @emil       ibralsmn@gmail.com
# * @copyright  (c) 2022 system-one
# * ************************************
# */
from odoo import fields, models,_
from odoo.exceptions import UserError
from odoo.fields import Date
import base64

class employee_profile_wizard(models.TransientModel):
    _name = 'employee.profile.attachment.wizard'

    attachment = fields.Binary(string="Attachment",attachment=True)
    file_name = fields.Char("File Name")

    employee_id = fields.Many2one('hr.employee')
    def get_profile_attachment(self, attachment,employee_name, employee):
        # file_name = attachment.filename
        data = {
            'res_name': employee_name,
            'res_model': 'hr.employee',
            'res_id': employee,
            'datas': attachment,
            'type': 'binary',
            'name': self.file_name,
        }
        return data

    def submit_attachment(self):
        attachment_obj = self.env['ir.attachment']
        attachments = self.get_profile_attachment(self.attachment, self.employee_id.name,self.employee_id.id)
        attachment_obj.sudo().create(attachments)