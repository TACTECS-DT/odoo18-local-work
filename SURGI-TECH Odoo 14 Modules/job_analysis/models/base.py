from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Questionnaire(models.Model):
    _name = 'job.analysis.questionnaire'
    _order = 'code desc'
    _description = 'Questionnaire'

    name = fields.Char()
    code = fields.Char(string='Sequence')
    description = fields.Text()


class JobAnalysisType(models.Model):
    _name = 'job.analysis.type'
    _description = 'Job Analysis Type'

    name = fields.Char()
    code = fields.Char()
