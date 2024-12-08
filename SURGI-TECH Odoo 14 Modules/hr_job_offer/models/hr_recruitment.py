from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'hr.contract'

    @api.onchange('employee_id')
    def onchange_employee_offer(self):
        if self.employee_id and self.employee_id.applicant_id:
            for applicant in self.employee_id.applicant_id:
                if applicant.job_offer_id:
                    self.basic_salary = applicant.job_offer_id.basic
                    self.variable_incentive = applicant.job_offer_id.variable_incentive
                    self.car_allow = applicant.job_offer_id.car_allowance
                    self.fuel_allow = applicant.job_offer_id.transport_allowance
                    self.door_type = applicant.job_offer_id.attendance_type
                    self.mobi = applicant.job_offer_id.mobile_package
                    self.grade_id = applicant.job_offer_id.grade_id.id
                    self.rank_id = applicant.job_offer_id.rank_id.id
                    self.rang_id = applicant.job_offer_id.rang_id.id




class HRRecruitment(models.Model):
    _inherit = 'hr.applicant'

    job_offer_id = fields.Many2one('hr.job.offer')
    is_hiring_approved = fields.Boolean(compute='_compute_is_hiring_approved')
    offering_date = fields.Date(related='job_offer_id.date', store=True)
    offering_state = fields.Selection(related='job_offer_id.state', store=True)


    def _compute_is_hiring_approved(self):
        for rec in self:
            if rec.hiring_approval_id:
                if rec.hiring_approval_id.state == 'gm':
                    rec.is_hiring_approved = True
                else:
                    rec.is_hiring_approved = False
            else:
                rec.is_hiring_approved = False

    def action_show_job_offer(self):
        self.ensure_one()
        offer = self.job_offer_id
        action = {
            'name': _('Job Offer'),
            'view_mode': 'form,tree',
            'res_model': 'hr.job.offer',
            'type': 'ir.actions.act_window',
            'context': {'form_view_initial_mode': 'readonly'},
            'res_id': offer.id,
        }
        return action

