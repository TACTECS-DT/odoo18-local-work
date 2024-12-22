from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SessionCreator(models.TransientModel):
    _name = 'inventory.session.creator'
    _description = 'Inventory Session Creator'

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users"
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products"
    )
    inventory_count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Inventory Count"
    )
    is_multi_session = fields.Boolean(
        default=False,
        string="Is multi sesstion"
    )
    parent_count_id = fields.Many2one(
        related='inventory_count_id.count_id',
        string="Parent Count"
    )

    def confirm(self, users=False):
        if not self.user_ids:
            raise ValidationError(_("Please add User(s)."))
        else:
            count_id = self.env['setu.stock.inventory.count'].sudo().browse(self.inventory_count_id.id) or self.env['setu.stock.inventory.count'].sudo().browse(self.env.context.get('active_id', False))
            if count_id.type == 'Multi Session':
                is_multi_session = True
            else:
                is_multi_session = False
            session = self.env['setu.inventory.count.session'].create({
                'is_multi_session': is_multi_session,
                'inventory_count_id': self.inventory_count_id.id,
                'location_id': self.inventory_count_id.location_id.id,
                'warehouse_id': self.inventory_count_id.warehouse_id.id,
                'use_barcode_scanner': self.inventory_count_id.use_barcode_scanner
            })
            session.user_ids = self.user_ids or users
            session_line_vals = []
            domain = [('location_id', '=', self.inventory_count_id.location_id.id)]
            locations = self.env['stock.location'].sudo().search(domain)
            if not count_id.count_id:
                for product in self.product_ids:
                    for loc in locations:
                        inv_count_line = self.inventory_count_id.line_ids.filtered(
                            lambda l: l.product_id == product and l.location_id == loc)
                        if not inv_count_line:
                            inv_count_line = self.env['setu.stock.inventory.count.line'].create({
                                    'product_id': product.id,
                                    'inventory_count_id': self.inventory_count_id.id,
                                    'location_id': loc.id
                            })
                            # self.inventory_count_id.write({
                            #     'line_ids': [(0, 0, {'product_id': product.id, 'location_id': loc.id})]
                            # })
                        session_line_vals.append((0, 0, {
                            'product_id': product.id,
                            'inventory_count_id': self.inventory_count_id.id,
                            'inventory_count_line_id': inv_count_line.id,
                            'location_id': loc.id,
                            'is_multi_session': session.is_multi_session,
                        }))
            else:
                for line in count_id.line_ids.filtered(lambda p: p.product_id in self.product_ids):
                    session_line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'location_id': line.location_id.id,
                        'inventory_count_id': count_id.id,
                        'inventory_count_line_id': line.id,
                        'is_multi_session': session.is_multi_session,
                    }))
            session.write({
                'session_line_ids': session_line_vals
            })


class WarningMSGWizard(models.TransientModel):
    _name = 'inventory.warning.message.wizard'
    _description = 'Inventory Warning Message Wizard'

    message = fields.Char(
        string="Message"
    )

    def approve(self):
        session_id = self.env['setu.inventory.count.session'].browse(self.env.context.get('active_id', False))
        for line in session_id.session_line_ids:
            line.state = 'Approve'
        session_id.is_session_approved = True
        
    def approve_count_lines(self):
        count_id = self.env['setu.stock.inventory.count'].browse(self.env.context.get('active_id', False))
        for line in count_id.line_ids:
            line.state = 'Approve'

    def reject(self):
        session_id = self.env['setu.inventory.count.session'].browse(self.env.context.get('active_id', False))
        for line in session_id.session_line_ids:
            line.state = 'Reject'
        session_id.is_session_approved = False
        
    def reject_count_lines(self):
        count_id = self.env['setu.stock.inventory.count'].browse(self.env.context.get('active_id', False))
        for line in count_id.line_ids:
            line.state = 'Reject'


class InventoryValidateWiz(models.TransientModel):
    _name = 'setu.inventory.session.validate.wizard'
    _description = 'Setu Inventory  Session Validate Wizard'

    session_id = fields.Many2one(
        comodel_name="setu.inventory.count.session",
        string="Session"
    )
    session_state = fields.Selection(
        related="session_id.state",
        string="Session State"
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users"
    )

    def create_re_count(self):
        count = self.env['setu.stock.inventory.count'].sudo().browse(self.env.context.get('active_id', False))
        count.open_new_count(self.user_ids)

    def create_re_session(self):
        session = self.env['setu.inventory.count.session'].browse(self.env.context.get('active_id', False))
        session.open_new_session()
        session._validate_session()

    def no_re_session(self):
        session = self.env['setu.inventory.count.session'].browse(self.env.context.get('active_id', False))
        session._validate_session()

    def continue_re_session(self):
        self.create_re_session()
