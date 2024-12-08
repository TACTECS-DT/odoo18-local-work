from odoo import models, fields, api, _


class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    is_accept = fields.Boolean()