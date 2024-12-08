# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class OpenVacanciesSituationReport(models.Model):
    _name = "open.vacancies.situation.report"
    _description = "Open Vacancies Situation Report"
    _auto = False


    job_id = fields.Many2one('hr.job', readonly=True)
    open_date = fields.Date('Opening Date',readonly=True)
    close_date = fields.Date('Closing Date',readonly=True)
    user_id = fields.Many2one('res.users', string='Recruiter',readonly=True)
    name = fields.Char('Applicant Name', readonly=True)
    source_id = fields.Many2one('hr.recruitment.source',readonly=True)
    applicant_state = fields.Selection([
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('shortlisted', 'Shortlisted'),
        ('no_show', 'No Show'),
        ('offering', 'Offering')
    ], string='Status',readonly=True)
    offering_date= fields.Date('Offering Date', readonly=True)
    offering_state = fields.Selection([
        ('new', 'New'),
        ('progress', 'In Progress'),
        ('to_employee', 'Gigven to Employee'),('accepted', 'Accepted'),('refused', 'Refused')], string='Offering Status',readonly=True)
    availability = fields.Date('Availability Date',readonly=True)
    hr_hiring_date = fields.Date('HR Hiring Date',readonly=True)
    employee_date = fields.Date('Create Employee Date',readonly=True)
    create_date = fields.Date(readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)



    def _query(self, fields='', from_clause=''):
        select_ = """
                a.id as id,
                a.user_id,
                a.name,
                a.source_id,
                a.company_id,
                a.job_id,
                a.open_date,
                a.close_date,
                a.applicant_state,
                a.offering_date,
                a.offering_state,
                a.availability,
                a.hr_hiring_date,
                a.create_date,
                a.employee_date
                %s
        """ % fields

        from_ = """
                hr_applicant a
                %s
        """ % from_clause

        return '(SELECT %s FROM %s)' % (select_, from_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
