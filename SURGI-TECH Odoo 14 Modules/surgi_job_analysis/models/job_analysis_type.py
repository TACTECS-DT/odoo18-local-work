from odoo import models, fields, api
class JobAnalysisType(models.Model):
    _name = 'job.analysis.type'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char()

