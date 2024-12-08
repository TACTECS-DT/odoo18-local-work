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


class ReferralRequest(models.Model):
    _name = 'referral.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Referral Request'

    name = fields.Char(default='New')
    date = fields.Date('Date',default=date.today(),tracking=True)
    person_name = fields.Char(tracking=True)
    current_company = fields.Char(tracking=True)
    current_position = fields.Char(tracking=True)
    person_mobile = fields.Char(tracking=True)
    person_email = fields.Char(tracking=True)
    relation = fields.Char(tracking=True)
    partner_national_id = fields.Char('National ID')
    active = fields.Boolean(string="Active", default=True)
    job_id = fields.Many2one('hr.job',string='Suggested job',tracking=True,domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('job_state','=','gm')]")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='draft')
    applicant_id = fields.Many2one('hr.applicant')




    def action_approve(self):
        self.ensure_one()
        job_applicant = self.env['hr.applicant'].sudo().create({
            'name': str(self.person_name+' Application'),
            'partner_name':self.person_name,
            'email_from':self.person_email,
            'partner_phone':self.person_mobile,
            'partner_national_id':self.partner_national_id,
            'job_id': self.job_id.id,
            'ref_user_id': self.user_id.id,
            'company_id': self.company_id.id
        })
        return self.write({
            'state': 'approved','applicant_id':job_applicant.id,
        })


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('referral.request') or '/'
        return super().create(values)