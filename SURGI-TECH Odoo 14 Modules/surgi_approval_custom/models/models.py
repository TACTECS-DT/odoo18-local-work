# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Approvals(models.Model):
    _inherit = 'approval.request'



    partner_invoices_ids = fields.Many2many('account.move',domain="[('partner_id','=',partner_id),('payment_state','in',['not_paid','partial'])]",store=True)
    submitted_by = fields.Many2one('res.users',string="Submitted By",readonly=True)
    submitted_on = fields.Char(string="Submitted On",readonly=True)
    approval_history_ids = fields.One2many('approval.approval.history','approval_id')
    total_lines = fields.Float(compute='compute_total_invoice_lines')
    discount_percentage = fields.Float('Discount percentage',store=True,compute='compute_discount_percentage')
    @api.depends('partner_invoices_ids','total_lines')
    def compute_discount_percentage(self):
        for rec in self:
            percentage = 0
            if rec.amount and rec.partner_invoices_ids:
                percentage = (rec.amount / rec.total_lines) * 100
            rec.discount_percentage = percentage
    def compute_total_invoice_lines(self):
        for rec in self:
            amount = sum(rec.partner_invoices_ids.mapped('amount_total_signed'))
            rec.total_lines = amount
    def action_confirm(self):
        for rec in self:
            rec.submitted_by = self.env.user.id
            rec.submitted_on = fields.Datetime.now()
        super(Approvals, self).action_confirm()
    def action_approve(self, approver=None):
        self.env['approval.approval.history'].create({'approval_id':self.id,'approved_by': self.env.user.id,'approved_on':fields.Datetime.now()})

        super(Approvals, self).action_approve()

class aprovalaprovalhistory(models.Model):
    _name = 'approval.approval.history'
    approval_id = fields.Many2one('approval.request',string='approval')
    approved_by = fields.Many2one('res.users',string="Approved By",readonly=True)
    approved_on = fields.Char(string="Approved On",readonly=True)
    # @api.depends('partner_id')
    # def get_partner_invoices_ids(self):
    #     for rec in self:
    #         if rec.partner_id:
    #             invoices = self.env['account.move'].search([('partner_id','=',rec.partner_id.id),('payment_state','in',['not_paid','partial'])])
    #             print('invoices',invoices)
    #             rec.write({'partner_invoices_ids': [(6, 0, invoices.ids)]})


