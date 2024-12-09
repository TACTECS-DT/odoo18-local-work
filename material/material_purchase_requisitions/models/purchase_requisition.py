# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError  # تم حذف Warning

class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']  # odoo11
    _order = 'id desc'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise UserError(
                    _('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
        return super(MaterialPurchaseRequisition, self).unlink()

    name = fields.Char(
        string='Number',
        index=True,
        readonly=1,
    )
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approval'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Order Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        tracking=True
    )
    request_date = fields.Date(
        string='Requisition Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        copy=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True,
        copy=True,
    )
    approve_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        readonly=True,
        copy=False,
    )
    reject_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager Reject',
        readonly=True,
    )
    approve_employee_id = fields.Many2one(
        'hr.employee',
        string='Approved by',
        readonly=True,
        copy=False,
    )
    reject_employee_id = fields.Many2one(
        'hr.employee',
        string='Rejected by',
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True,
        copy=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,
    )
    requisition_line_ids = fields.One2many(
        'material.purchase.requisition.line',
        'requisition_id',
        string='Purchase Requisitions Line',
        copy=True,
    )
    date_end = fields.Date(
        string='Requisition Deadline',
        readonly=True,
        help='Last date for the product to be needed',
        copy=True,
    )
    date_done = fields.Date(
        string='Date Done',
        readonly=True,
        help='Date of Completion of Purchase Requisition',
    )
    managerapp_date = fields.Date(
        string='Department Approval Date',
        readonly=True,
        copy=False,
    )
    manareject_date = fields.Date(
        string='Department Manager Reject Date',
        readonly=True,
    )
    userreject_date = fields.Date(
        string='Rejected Date',
        readonly=True,
        copy=False,
    )
    userrapp_date = fields.Date(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    receive_date = fields.Date(
        string='Received Date',
        readonly=True,
        copy=False,
    )
    reason = fields.Text(
        string='Reason for Requisitions',
        required=False,
        copy=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True,
    )
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Internal Picking',
        readonly=True,
        copy=False,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Requisition Responsible',
        copy=True,
    )
    employee_confirm_id = fields.Many2one(
        'hr.employee',
        string='Confirmed by',
        readonly=True,
        copy=False,
    )
    confirm_date = fields.Date(
        string='Confirmed Date',
        readonly=True,
        copy=False,
    )

    purchase_order_ids = fields.One2many(
        'purchase.order',
        'custom_requisition_id',
        string='Purchase Orders',
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,
    )

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        vals.update({
            'name': name
        })
        res = super(MaterialPurchaseRequisition, self).create(vals)
        return res

    def requisition_confirm(self):
        for rec in self:
            manager_mail_template = self.env.ref(
                'material_purchase_requisitions.email_confirm_material_purchase_requistion')
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'dept_confirm'
            if manager_mail_template:
                manager_mail_template.send_mail(self.id)

    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.userreject_date = fields.Date.today()

    def manager_approve(self):
        for rec in self:
            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            employee_mail_template = self.env.ref(
                'material_purchase_requisitions.email_purchase_requisition_iruser_custom')
            email_iruser_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition')
            employee_mail_template.send_mail(self.id)
            email_iruser_template.send_mail(self.id)
            rec.state = 'ir_approve'

    def user_approve(self):
        for rec in self:
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        pick_vals = {
            'product_id': line.product_id.id,
            'product_uom_qty': line.qty,
            'product_uom': line.uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.dest_location_id.id,
            'name': line.product_id.name,
            'picking_type_id': self.custom_picking_type_id.id,
            'picking_id': stock_id.id,
            'custom_requisition_line_id': line.id,
            'company_id': line.requisition_id.company_id.id,
        }
        return pick_vals

    @api.model
    def _prepare_po_line(self, line=False, purchase_order=False):
        seller = line.product_id._select_seller(
            partner_id=self._context.get('partner_id'),
            quantity=line.qty,
            date=purchase_order.date_order and purchase_order.date_order.date(),
            uom_id=line.uom
        )
        po_line_vals = {
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_qty': line.qty,
            'product_uom': line.uom.id,
            'date_planned': fields.Date.today(),
            'price_unit': seller.price or line.product_id.standard_price or 0.0,
            'order_id': purchase_order.id,
            'analytic_distribution': {self.sudo().analytic_account_id.id: 100} if self.analytic_account_id else False,
            'custom_requisition_line_id': line.id
        }
        return po_line_vals

    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        for rec in self:
            if not rec.requisition_line_ids:
                raise UserError(_('Please create some requisition lines.'))
            if any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
                if not rec.location_id.id:
                    raise UserError(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id.id:
                    raise UserError(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise UserError(_('Select Destination location under the picking details.'))
                picking_vals = {
                    'partner_id': rec.employee_id.sudo().address_home_id.id,
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                    'picking_type_id': rec.custom_picking_type_id.id,
                    'origin': rec.name,
                    'move_type': 'direct',
                    'company_id': rec.company_id.id,
                    'requisition_id': rec.id,
                }
                picking_id = stock_obj.create(picking_vals)
                stock_move_vals = []
                for line in rec.requisition_line_ids:
                    stock_move_vals.append(self._prepare_pick_vals(line=line, stock_id=picking_id))
                if stock_move_vals:
                    move_obj.create(stock_move_vals)
                rec.delivery_picking_id = picking_id.id
            po_vals = {
                'origin': rec.name,
                'partner_id': rec.employee_id.sudo().address_home_id.id,
                'company_id': rec.company_id.id,
                'date_order': fields.Date.today(),
                'custom_requisition_id': rec.id,
                'order_line': [],
                'picking_type_id': rec.custom_picking_type_id.id,
            }
            po_id = purchase_obj.create(po_vals)
            po_line_vals = []
            for line in rec.requisition_line_ids:
                po_line_vals.append(self._prepare_po_line(line=line, purchase_order=po_id))
            if po_line_vals:
                purchase_line_obj.create(po_line_vals)
            rec.purchase_order_ids = [(4, po_id.id)]
            rec.state = 'stock'
