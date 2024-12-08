# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
import logging
import pytz

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_join

from odoo import api, fields, models, tools, _
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import AccessError
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class InterviewProcess(models.Model):
    _name = 'interview.process'
    _description = 'Interview Process'

    name = fields.Char(default='New')
    job_ids = fields.Many2many('hr.job',string='Job Position',domain="[('job_state','=','gm')]")
    survey_ids = fields.Many2many('survey.survey', string="Applicant's Survey")
    line_ids = fields.One2many('interview.process.line','interview_id')


    @api.constrains('job_ids')
    def _constrains_job(self):
        for rec in self:
            history = self.env['interview.process'].sudo().search(
                [('id', '!=', rec.id), ('job_ids', 'in', rec.job_ids.ids)])
            if history:
                raise ValidationError(_('"The Job already select in interview process!"'))


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('interview.process') or '/'
        return super().create(values)


class InterviewProcessLine(models.Model):
    _name = 'interview.process.line'

    name = fields.Char('Sequence',required=1)
    stage_id = fields.Many2one('hr.recruitment.stage')
    user_id = fields.Many2one('res.users',string='Recruiter')
    survey_ids = fields.Many2many('survey.survey', 'process_line_rel', 'process_line_id', 'survey_id',string='Recruiter Surveys')
    applicant_survey_ids = fields.Many2many('survey.survey',string='Applicant Surveys')
    interview_id = fields.Many2one('interview.process')
    type = fields.Selection([
        ('zoom', 'Zoom'),
        ('physically ', 'Physically')
    ], string='Interview Type')
    reviewer_ids = fields.Many2many('res.users', string='Reviewers')


