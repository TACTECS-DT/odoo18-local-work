from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from datetime import datetime


class StockInvCountPlanner(models.Model):
    _name = 'setu.stock.inventory.count.planner'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Stock Inventory Count Planner'

    name = fields.Char(
        string="Name"
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location"
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products"
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse"
    )
    inventory_count_date = fields.Date(
        default=fields.Datetime.now,
        string="Date"
    )
    planing_frequency = fields.Integer(
        string="Planing Frequency Day"
    )
    next_execution_date = fields.Date(
        string="Next Execution Date",
        default=fields.Date.today
    )
    previous_execution_date = fields.Date(
        string="Previous Execution Date",
        default=fields.Date.today
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified')],
        default="draft",
        string="Status",
        help="To identify process status")
    approver_id = fields.Many2one(
        comodel_name="res.users",
        string="Approver"
    )
    use_barcode_scanner = fields.Boolean(
        default=False,
        string="Use barcode scanner"
    )
    active = fields.Boolean(
        default=True,
        string="Active"
    )
    past_history_days = fields.Integer(
        string="Past History Days",
        default="365"
    )
    type = fields.Selection([
        ('Single Session', 'Single Session'),
        ('Multi Session', 'Multi Session')],
        default='Single Session',
        required=True,
        string="Type"
    )

    def reset_to_draft(self):
        self.state = 'draft'

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            return {'domain': {
                'location_id': [('usage', '=', 'internal'), ('id', 'child_of', self.warehouse_id.view_location_id.id)]}}
        else:
            return {'domain': {'location_id': [('usage', '=', 'internal')]}}

    @api.onchange('location_id')
    def onchange_location_id(self):
        if self.location_id:
            domain = [('view_location_id', 'parent_of', self.location_id.id)]
            wh = self.env['stock.warehouse'].search(domain)
            return {'value': {
                'warehouse_id': wh.id}}

    @api.onchange('approver_id')
    def onchange_approver_id(self):
        users = self.sudo().env.ref('setu_inventory_count_management_18.group_setu_inventory_count_manager').users
        ids = users.ids if users else []
        return {'domain': {'approver_id': [('id', 'in', ids)]}}

    def auto_create_inventory_count_record(self):
        records = self.search([('next_execution_date', '<=', datetime.today().date()), ('state', '=', 'verified')])
        for record in records:
            record.create_inventory_count_record()
        return True

    def verify_inventory_count_planing(self):
        if self.planing_frequency <= 0:
            raise ValidationError('Please Enter Proper Frequency Days.')
        # if not self.product_ids:
        #     raise ValidationError('Please select Product.')
        self.write({'state': 'verified'})
        return True

    def set_products_in_inventory_count(self, product_ids):
        count = self.env['setu.stock.inventory.count'].browse(self.env.context.get('active_id', False))
        product_ids = self.env['product.product'].browse(product_ids)
        count.product_ids |= product_ids

    def create_inventory_count(self):
        self.create_inventory_count_record()
        return True

    def create_inventory_count_record(self):
        inventory_count_obj = self.env['setu.stock.inventory.count']
        vendor_product_dict = self.get_approver_product_mapping_dict()
        for approver_id, product_ids in vendor_product_dict.items():
            vals = self.prepare_vales_for_inventory_count(approver_id, product_ids)
            rec = inventory_count_obj.search([('planner_id', '=', self.id), ('state', '=', 'draft')])
            if rec:
                rec.product_ids and rec.product_ids.unlink()
                rec.write(vals)
            else:
                mail_obj = self.env['mail.mail']
                data = {'planner_id': self.id}
                rec = inventory_count_obj.create(vals)
                if rec.approver_id.partner_id not in rec.message_follower_ids.mapped('partner_id'):
                    data.update({'message_follower_ids': [(4, rec.approver_id.partner_id.id)]})
                rec.write(data)
                email_template = self.sudo().sudo().env.ref(
                    'setu_inventory_count_management_18.mail_template_request_for_inventory_count', False)
                partners = rec.message_follower_ids.mapped('partner_id')
                # mail_body = email_template._render({}, engine='ir.qweb', minimal_qcontext=True)
                mail_mail = email_template and email_template.send_mail(rec.id) or False
                mail_mail = mail_mail and mail_obj.sudo().browse(mail_mail)
                if mail_mail:
                    mail_mail.recipient_ids = [(6, 0, [rec.approver_id.partner_id.id])]
                    mail_mail.send()
            self.write({'previous_execution_date': datetime.today().date(),
                        'next_execution_date': datetime.today().date() + timedelta(days=self.planing_frequency)
                        })
            if product_ids:
                self.set_products_in_inventory_count(product_ids)

    def get_approver_product_mapping_dict(self):
        approver_product_dict = {}
        if self.approver_id:
            approver_product_dict.update({self.approver_id.id: self.product_ids.ids})
        return approver_product_dict

    def prepare_vales_for_inventory_count(self, approver, product_list):
        approver_id = self.env['res.users'].browse(approver)
        vals = {'planner_id': self.id,
                'approver_id': approver_id.id,
                'warehouse_id': self.warehouse_id.id,
                'type': self.type,
                'location_id': self.location_id.id,
                'product_ids': [(6, 0, product_list)],
                'use_barcode_scanner': self.use_barcode_scanner
                }
        return vals
