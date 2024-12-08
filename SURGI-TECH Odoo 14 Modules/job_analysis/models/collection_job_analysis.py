# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class CollectionJobAnalysis(models.Model):
    _name = 'collection.job.analysis'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Collection Job Analysis'
    _rec_name = 'position_id'

    batch_id = fields.Many2one('job.analysis.batch')
    active = fields.Boolean(string="Active", default=True, tracking=True)
    position_id = fields.Many2one(comodel_name="hr.job", string="Job Position")
    # child_ids = fields.One2many('hr.employee', 'parent_id', string='Direct subordinates')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    answer_line_ids = fields.One2many('answer.line', 'collection_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('manager', 'Manager Approved'), ('parent', 'Parent Manager Approved'), ('hr', 'HR Manager Approved')
    ], string='Status', copy=False, index=True, readonly=True, default='draft', tracking=True)
    is_manager = fields.Boolean(compute='_compute_groups')
    is_parent = fields.Boolean(compute='_compute_groups')
    parent_manager_ids = fields.Many2many('res.users', string='Parent Managers')


    def _compute_parent_manager(self):
        for rec in self:
            record = rec.position_id.position_manager_id
            parents = []
            while record.parent_id.user_id:
                parents.append(record.parent_id.user_id.id)
                record = record.parent_id
            rec.write({'parent_manager_ids': parents})

    def _compute_groups(self):
        for rec in self:
            if rec.position_id.position_manager_id.user_id and self.env.user == rec.position_id.position_manager_id.user_id:
                rec.is_manager = True
            else:
                rec.is_manager = False
            if rec.parent_manager_ids and self.env.user in rec.parent_manager_ids:
                rec.is_parent = True
            else:
                rec.is_parent = False

    def manager_approve(self):
        self.ensure_one()
        partners = []

        if self.position_id.department_id.manager_id.user_id:
            partners.append(self.position_id.department_id.manager_id.user_id.partner_id.id)
            self._send_notification('Manager Approved', partners)
        self._compute_parent_manager()
        self.write({'state': 'manager'})

    def parent_approve(self):
        self.ensure_one()
        group = self.env.ref('job_analysis.group_job_analysis_manager').sudo().users
        partners = []
        if group:
            for usr in group:
                partners.append(usr.partner_id.id)
            self._send_notification('Parent Manager Approved', partners)
        self.write({'state': 'parent'})

    def hr_approve(self):
        self.ensure_one()
        self.write({'state': 'hr'})

    def reset(self):
        self.ensure_one()
        if self.state == 'manager':
            partners = []
            if self.position_id.position_manager_id.user_id:
                partners.append(self.position_id.position_manager_id.user_id.partner_id.id)
                self._send_notification('Draft', partners)
            self.write({'state': 'draft'})
        elif self.state == 'parent':
            partners = []
            if self.position_id.department_id.manager_id.user_id:
                partners.append(self.position_id.department_id.manager_id.user_id.partner_id.id)
                self._send_notification('Manager Approved', partners)

            self.write({'state': 'manager'})
        elif self.state == 'hr':
            group = self.env.ref('job_analysis.group_job_analysis_manager').sudo().users
            partners = []
            if group:
                for usr in group:
                    partners.append(usr.partner_id.id)
                self._send_notification('Parent Manager Approved', partners)
            self.write({'state': 'parent'})

    def _send_notification(self, state, partners):
        message = _('Collection of Job Analysis: %s is convert to %s') % (
            str(self.batch_id.name + "/" + self.position_id.name), state)
        return self.message_post(body=message, partner_ids=partners)


class AnswerLine(models.Model):
    _inherit = 'answer.line'

    collection_id = fields.Many2one('collection.job.analysis')
