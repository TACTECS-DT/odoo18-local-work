# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class JobAnalysisBatch(models.Model):
    _name = 'job.analysis.batch'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Job Analysis Batch'

    name = fields.Char(tracking=True)
    from_date = fields.Date('Start', tracking=True)
    to_date = fields.Date('End', tracking=True)
    active = fields.Boolean(string="Active", default=True)
    type = fields.Selection([
        ('employee', 'Employee'),
        ('company', 'Company'), ('tag', 'Employee Tag'), ('department', 'Department')
    ], string='Batch Type', required=1)
    employee_ids = fields.Many2many(
        'hr.employee', string='Employees')
    company_ids = fields.Many2many('res.company', string='Companies')
    category_ids = fields.Many2many('hr.employee.category', string='Employee Tags')
    department_ids = fields.Many2many('hr.department', string='Departments')
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')
    ], string='Status', copy=False, index=True, readonly=True, default='draft', tracking=True)
    questionnaire_ids = fields.Many2many('job.analysis.questionnaire')
    answer_count = fields.Integer("Registered", compute="_compute_answer_statistic")
    answer_done_count = fields.Integer("Attempts", compute="_compute_answer_statistic")

    def _compute_answer_statistic(self):
        for rec in self:
            rec.answer_count = self.env['questionnaires.answer'].sudo().search_count([('batch_id', '=', self.id)])
            rec.answer_done_count = self.env['collection.job.analysis'].sudo().search_count(
                [('batch_id', '=', self.id)])

    def create_answer(self, employee_id):
        qust = []
        try:
            # self.env['questionnaires.answer'].create(
            #     {'batch_id': self.id,
            #      'employee_id': employee_id.id,
            #      'answer_line_ids': qust})
            self.env.cr.execute(
                "INSERT INTO questionnaires_answer (active,batch_id, employee_id,state) VALUES (%s,%s, %s,%s) RETURNING id",
                (True,self.id, employee_id.id,'draft'))
            last_id = self.env['questionnaires.answer'].search([])[-1].id
            for q in self.questionnaire_ids:
                self.env['answer.line'].create({'answer_id':last_id,'question_id': q.id})
        except Exception as e:
            pass

    def create_collection(self, position, company):
        try:
            if position:
                self.env.cr.execute(
                    """INSERT INTO collection_job_analysis (active,batch_id, position_id,company_id,state) VALUES (%s,%s,%s,%s,%s) """,
                    (True,self.id,position.id,company.id,'draft'))
        except Exception as e:
            pass


    def confirm(self):
        self.ensure_one()
        self.write({'state': 'confirm'})
        if self.type == 'employee':
            positions = []
            for emp in self.employee_ids:
                if emp.user_id:
                    self.create_answer(emp)
                    if emp.job_id:
                        positions.append(emp.job_id)
            if positions:
                for po in set(positions):
                    self.create_collection(po, self.company_id)
        elif self.type == 'company':
            for com in self.company_ids:
                positions = []
                employees = self.env['hr.employee'].sudo().search([('company_id', '=', com.id)])
                for emp in employees:
                    if emp.user_id:
                        self.create_answer(emp)
                        if emp.job_id:
                            positions.append(emp.job_id)
                if positions:
                    for po in set(positions):
                        self.create_collection(po, com)
        elif self.type == 'tag':
            positions = []
            for tag in self.category_ids:
                employees = self.env['hr.employee'].sudo().search(
                    [('company_id', '=', self.company_id.id), ('category_ids', 'in', tag.id)])
                for emp in employees:
                    if emp.user_id:
                        self.create_answer(emp)
                        if emp.job_id:
                            positions.append(emp.job_id)
                if positions:
                    for po in set(positions):
                        self.create_collection(po, self.company_id)
        elif self.type == 'department':
            positions = []
            for deb in self.department_ids:
                employees = self.env['hr.employee'].sudo().search(
                    [('company_id', '=', self.company_id.id), ('department_id', '=', deb.id)])
                for emp in employees:
                    if emp.user_id:
                        self.create_answer(emp)
                        if emp.job_id:
                            positions.append(emp.job_id)
                if positions:
                    for po in set(positions):
                        self.create_collection(po, self.company_id)
        return True

    def show_questionnaires(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registered',
            'view_mode': 'tree,form',
            'res_model': 'questionnaires.answer',
            'domain': [('batch_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def show_collections(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Answer Collections',
            'view_mode': 'tree,form',
            'res_model': 'collection.job.analysis',
            'domain': [('batch_id', '=', self.id)],
            'context': "{'search_default_position': 1,'create': False}"
        }

    def show_answer_row(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Answer Report',
            'view_mode': 'tree,form',
            'res_model': 'answer.row',
            'domain': [('batch_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def reset(self):
        self.ensure_one()
        self.write({'state': 'draft'})
