# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrRecruitmentReport(models.Model):
    _inherit = "hr.recruitment.report"

    stage_id = fields.Many2one('hr.recruitment.stage', readonly=True)
    ceiling = fields.Integer('# Ceiling', readonly=True)
    emp_count = fields.Integer('Current Employee', readonly=True)
    vacancies_count = fields.Integer('Current Vacancies', readonly=True)
    pipeline_count = fields.Integer('Current Pipeline', group_operator="sum", readonly=True)
    rejected = fields.Integer('Rejected', group_operator="sum", readonly=True)
    accepted = fields.Integer('Accepted', group_operator="sum", readonly=True)
    shortlisted = fields.Integer('Shortlisted', group_operator="sum", readonly=True)

    def _query(self, fields='', from_clause=''):
        fields += """
            ,a.stage_id as stage_id,
            job.ceiling_count as ceiling,
            job.no_of_employee as emp_count,
            job.no_of_recruitment as vacancies_count,
            CASE WHEN a.applicant_state = 'rejected' THEN 1 ELSE 0 END as rejected,
            CASE WHEN a.applicant_state = 'accepted' THEN 1 ELSE 0 END as accepted,
            CASE WHEN a.applicant_state = 'shortlisted' THEN 1 ELSE 0 END as shortlisted
            """
        from_clause += """JOIN hr_job job ON job.id = a.job_id"""
        return super(HrRecruitmentReport, self)._query(fields, from_clause)
