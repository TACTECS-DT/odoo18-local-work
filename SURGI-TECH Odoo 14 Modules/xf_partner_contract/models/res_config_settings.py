# -*- coding: utf-8 -*-

from odoo import fields, models
from .selection import UseContract


class Company(models.Model):
    _inherit = 'res.company'

    contract_approval = fields.Selection(
        string='Use Contract Approval Workflow',
        selection=UseContract.list,
        default=UseContract.default,
    )
    use_contract = fields.Selection(
        string='Use Contract for Invoices',
        selection=UseContract.list,
        default=UseContract.default,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    contract_approval = fields.Selection(
        string='Use Contract Approval Workflow',
        related='company_id.contract_approval',
        readonly=False,
    )
    use_contract = fields.Selection(
        string='Use Contract for Invoices',
        related='company_id.use_contract',
        readonly=False,
    )
