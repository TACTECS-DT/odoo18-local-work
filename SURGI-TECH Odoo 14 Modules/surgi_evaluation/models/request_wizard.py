from odoo import models, fields, api
class RequestWizard(models.TransientModel):
    _name = 'request.wizard'

    start_date = fields.Date(string="Start Date", required=False, )
    end_date = fields.Date(string="End Date", required=False, )
    employee_ids = fields.Many2many(comodel_name="hr.employee",string="Employee", )

    def request_create(self):
        for rec in self.employee_ids:
            redundancy_rec=self.env['request.relegation'].sudo().create({
                'employee_id':rec.id,
                'date_start':self.start_date,
                'date_end':self.end_date,
            })
            redundancy_rec.get_employee_grad()