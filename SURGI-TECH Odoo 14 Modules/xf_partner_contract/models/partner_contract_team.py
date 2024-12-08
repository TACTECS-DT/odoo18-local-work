# -*- coding: utf-8 -*-
from odoo import api, fields, models
from .selection import ApproverState


class ContractApprovalTeam(models.Model):
    _name = 'xf.partner.contract.team'
    _inherit = ['mail.thread']
    _description = 'Contract Approval Team'

    active = fields.Boolean(
        string='Active',
        default=True,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    user_id = fields.Many2one(
        string='Team Leader',
        comodel_name='res.users',
        default=lambda self: self.env.user,
        required=True,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    approver_ids = fields.One2many(
        string='Approvers',
        comodel_name='xf.partner.contract.team.approver',
        inverse_name='team_id',
    )


class ContractApprovalTeamApprover(models.Model):
    _name = 'xf.partner.contract.team.approver'
    _description = 'Contract Approval Team Approver'
    _order = 'sequence'
    _rec_name = 'user_id'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    team_id = fields.Many2one(
        string='Team',
        comodel_name='xf.partner.contract.team',
        required=True,
        ondelete='cascade',
    )
    user_id = fields.Many2one(
        string='Approver',
        comodel_name='res.users',
        required=True,
    )
    role = fields.Char(
        string='Role/Position',
        required=True,
        default='Approver',
    )
    can_edit = fields.Boolean(
        string='Can Edit',
        default=False,
        help='Can edit contract details before own approval',
    )
    min_amount = fields.Monetary(
        string='Minimum Amount',
        currency_field='company_currency_id', readonly=False,
        help="""Minimum Amount (included) for which a validation by approver is required.
        If a contract cost is less than Minimum Amount then the approver will be skipped.""",
    )
    max_amount = fields.Monetary(
        string='Maximum Amount',
        currency_field='company_currency_id', readonly=False,
        help="""Maximum Amount (included) for which a validation by approver is required. 
        If a contract cost is greater than Maximum Amount then the approver will be skipped.""",
    )
    company_currency_id = fields.Many2one(
        string='Company Currency',
        comodel_name='res.currency',
        related='team_id.company_id.currency_id',
        readonly=True,
        help='Utility field to express threshold currency',
    )
    custom_condition_code = fields.Text(
        string='Custom Condition Code',
        help='You can enter python expression to define custom condition'
    )

    @api.onchange('user_id')
    def _detect_user_role(self):
        for approver in self:
            # if user related to employee, try to get job title for hr.employee
            employee = hasattr(approver.user_id, 'employee_ids') and getattr(approver.user_id, 'employee_ids')
            employee_job_id = hasattr(employee, 'job_id') and getattr(employee, 'job_id')
            employee_job_title = employee_job_id.name if employee_job_id else False
            if employee_job_title:
                approver.role = employee_job_title
                continue
            # if user related partner, try to get job title for res.partner
            partner = approver.user_id.partner_id
            partner_job_title = hasattr(partner, 'function') and getattr(partner, 'function')
            if partner_job_title:
                approver.role = partner_job_title


class ContractApprover(models.Model):
    _name = 'xf.partner.contract.approver'
    _inherit = 'xf.partner.contract.team.approver'
    _description = 'Contact Approver'

    team_approver_id = fields.Many2one(
        string='Team Approver',
        comodel_name='xf.partner.contract.team.approver',
        ondelete='set null',
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='xf.partner.contract',
        required=True,
        ondelete='cascade',
    )
    state = fields.Selection(
        string='Status',
        selection=ApproverState.list,
        default=ApproverState.default,
        readonly=True,
        required=True,
    )
