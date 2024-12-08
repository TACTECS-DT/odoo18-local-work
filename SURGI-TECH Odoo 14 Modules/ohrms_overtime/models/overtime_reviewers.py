# -*- coding: utf-8 -*-

from dateutil import relativedelta
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from datetime import datetime, date, timedelta, time



class OvertimeReviewers(models.Model):
    _name = "hr.overtime.reviewers"
    _description = "Overtime Reviewers"

    name = fields.Char("Stage Name", required=True, translate=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('m_approved', 'Manager Approved'),
                              ('hr_approved', 'HR Approved'),
                              ('f_approved', 'Final Approved'),
                              ('refused', 'Refused')], string="state",
                             default="draft")
    reviewer_ids = fields.Many2many('res.users',string='Reviewers')