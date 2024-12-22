from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

from odoo.fields import Date


class StockInvCount(models.Model):
    _name = 'setu.stock.inventory.count'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Stock Inventory Count'

    name = fields.Char(string="Name")
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
    line_ids = fields.One2many('setu.stock.inventory.count.line', 'inventory_count_id',
                               string="Inventory Count Lines"
                               )
    inventory_count_date = fields.Date(
        default=fields.Datetime.now,
        string="Inventory Count Date"
    )
    state = fields.Selection(selection=[
        ('Rejected', 'Rejected'),
        ('Draft', 'Draft'),
        ('In Progress', 'In Progress'),
        ('To Be Approved', 'To Be Approved'),
        ('Approved', 'Approved'),
        # ('Validated', 'Validated'),
        # ('Adjustment Requested', 'Adjustment Requested'),
        ('Inventory Adjusted', 'Inventory Adjusted'),
        ('Cancel', 'Cancel')
    ], default="Draft", string="State")
    approver_id = fields.Many2one(
        comodel_name="res.users",
        string="Approver"
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        default=lambda self: self.env.user.id,
        string="User"
    )
    session_ids = fields.One2many('setu.inventory.count.session', 'inventory_count_id', string="Sessions Details")
    count_session_ids = fields.Integer(
        compute="_compute_count_session_ids",
        string="Session Count"
    )
    re_count_ids = fields.Integer(
        compute="_compute_count_ids",
        string="Re-Count"
    )
    start_inventory_bool = fields.Boolean(
        compute="_compute_start_inventory_bool",
        string="Is Start Inventory"
    )
    create_count_bool = fields.Boolean(
        compute="_compute_create_count_bool",
        string="Create Count"
    )
    create_session_bool = fields.Boolean(
        compute="_compute_create_session_bool",
        string="Is Create Session"
    )
    discrepancy_ratio = fields.Float(
        compute="_compute_discrepancy_ratio",
        string="Discrepancy Ratio"
    )
    user_mistake_ratio = fields.Float(
        compute="_compute_user_mistake_ratio",
        string="User Mistake Ration"
    )
    inventory_adj_ids = fields.One2many('setu.stock.inventory', 'inventory_count_id', string="Inventory Adjustment Details")
    use_barcode_scanner = fields.Boolean(
        default=False,
        string="Use barcode scanner"
    )
    non_cancelled_session = fields.Boolean(
        compute="_compute_non_cancelled_session",
        string="Non cancelled session"
    )
    type = fields.Selection([
        ('Single Session', 'Single Session'),
        ('Multi Session', 'Multi Session')],
        default='Single Session',
        required=True,
        string="Type"
    )
    # is_single_session = fields.Boolean(string='Single Session?', compute='_compute_is_single_session')
    planner_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count.planner",
        string='Planner',
        readonly=True
    )
    count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        readonly=True,
        copy=False,
        string="Count"
    )
    count_ids = fields.One2many('setu.stock.inventory.count', 'count_id', copy=False, string='Counts')
    stock_move_line_ids = fields.One2many('stock.move.line', 'count_id', string="Move Line")
    rejected_lines_count = fields.Integer(
        compute="_compute_rejected_lines_count",
        string="Rejected lines count"
    )

    @api.constrains('inventory_count_date')
    def _check_inventory_count_date(self):
        if self.inventory_count_date < Date.today():
            raise ValidationError(_('You cannot select date from past.'))

    # def _compute_is_single_session(self):
    #
    #     if self.type == 'Single Session':
    #         running_session = self.session_ids.filtered(lambda l: l.state not in ('Cancel','Done'))
    #
    #         if not running_session:
    #             self.is_single_session = True
    #         else:
    #             self.is_single_session = False
    #     else:
    #         self.is_single_session = False

    def _compute_non_cancelled_session(self):
        for rec in self:
            if rec.session_ids and rec.session_ids.filtered(lambda s: s.state != 'Cancel'):
                rec.non_cancelled_session = True
            else:
                rec.non_cancelled_session = False

    def complete_counting(self):
        if self.session_ids.filtered(lambda s: s.state not in ('Cancel', 'Done')):
            raise ValidationError(
                "Please submit and validate all the incomplete sessions before completing the counting.")
        self.state = 'To Be Approved'

    def _compute_discrepancy_ratio(self):
        for rec in self:
            if rec.line_ids:
                product_discrepancy_dict = dict()
                for line in rec.line_ids:
                    product_id = line.product_id.id
                    if product_id in product_discrepancy_dict:
                        if line.is_discrepancy_found:
                            product_discrepancy_dict.update({
                                product_id: True
                            })
                    else:
                        product_discrepancy_dict.update({
                            product_id: line.is_discrepancy_found
                        })
                number_of_products = len(product_discrepancy_dict.keys())
                discrepancy_products = 0
                for product, discrepancy_bool in product_discrepancy_dict.items():
                    if discrepancy_bool:
                        discrepancy_products += 1
                ratio = discrepancy_products * 100 / number_of_products
                rec.discrepancy_ratio = ratio
            rec.discrepancy_ratio = 0

    def action_open_discrepancy_lines(self):
        discrepancy_lines = self.line_ids.filtered(lambda l: l.is_discrepancy_found)
        ids = discrepancy_lines.ids if discrepancy_lines else []
        return {
            'name': 'Discrepancy Lines',
            'view_mode': 'tree',
            'view_id': self.sudo().env.ref(
                'setu_inventory_count_management_18.setu_stock_inventory_count_line_tree_view').id,
            'res_model': 'setu.stock.inventory.count.line',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ids)]
        }

    def _compute_user_mistake_ratio(self):
        for rec in self:
            if rec.line_ids:
                product_user_mistake_dict = dict()
                for line in rec.line_ids:
                    product_id = line.product_id.id
                    if product_id in product_user_mistake_dict:
                        if line.user_calculation_mistake:
                            product_user_mistake_dict.update({
                                product_id: True
                            })
                    else:
                        product_user_mistake_dict.update({
                            product_id: line.user_calculation_mistake
                        })
                number_of_products = len(product_user_mistake_dict.keys())
                user_mistake_products = 0
                for product, user_mistake_bool in product_user_mistake_dict.items():
                    if user_mistake_bool:
                        user_mistake_products += 1
                ratio = user_mistake_products * 100 / number_of_products
                rec.user_mistake_ratio = ratio
            rec.user_mistake_ratio = 0

    def approve_all_lines(self):
        wiz = self.env['inventory.warning.message.wizard'].create({
            'message': "Are you sure that you want to Approve all session lines? (Even rejected lines will also be approved)"
        })
        return {
            'name': 'Warning!!!',
            'view_mode': 'form',
            'view_id': self.sudo().env.ref(
                'setu_inventory_count_management_18.inventory_count_warning_message_approve_wizard_form_view').id,
            'res_model': 'inventory.warning.message.wizard',
            'type': 'ir.actions.act_window',
            'res_id': wiz.id,
            'target': 'new'
        }

    def reject_all_lines(self):
        wiz = self.env['inventory.warning.message.wizard'].create({
            'message': "Are you sure that you want to Reject all session lines? (Even approved lines will also be rejected)"
        })
        return {
            'name': 'Warning!!!',
            'view_mode': 'form',
            'view_id': self.sudo().env.ref(
                'setu_inventory_count_management_18.inventory_count_warning_message_reject_wizard_form_view').id,
            'res_model': 'inventory.warning.message.wizard',
            'type': 'ir.actions.act_window',
            'res_id': wiz.id,
            'target': 'new'
        }

    def open_new_count(self, users, theoritical=None):
        rejected_lines = self.line_ids.filtered(lambda s: s.state == 'Reject')
        new_count = self.env['setu.stock.inventory.count'].create({
            'approver_id': self.approver_id.id,
            'count_id': self.id,
            'location_id': self.location_id.id,
            'warehouse_id': self.warehouse_id.id,
            'use_barcode_scanner': self.use_barcode_scanner,
            'type': 'Multi Session'
        })
        # products = new_count.product_ids = rejected_lines.mapped('product_id')
        # new_count.product_ids = products
        new_session = self.env['setu.inventory.count.session'].create({
            'is_multi_session': True,
            'user_ids': [(6, 0, users.ids)],
            'inventory_count_id': new_count.id,
            'location_id': new_count.location_id.id,
            'warehouse_id': new_count.warehouse_id.id,
            'use_barcode_scanner': new_count.use_barcode_scanner,
            'type': 'Multi Session',
        })
        for line in rejected_lines:
            # new_count_line = self.env['setu.stock.inventory.count.line'].create({
            #     'product_id': line.product_id.id,
            #     'location_id': line.location_id.id,
            #     'inventory_count_id': new_count.id
            # })
            tracking = line.product_id.tracking
            vals = {
                'product_id': line.product_id.id,
                'location_id': line.location_id.id,
                'date_of_scanning': datetime.now(),
                'session_id': new_session.id,
                'inventory_count_id': new_count.id,
                'is_multi_session': new_session.is_multi_session,
            }
            domain = [('location_id', '=', line.location_id.id),
                     ('product_id', '=', line.product_id.id)]
            if tracking == 'none':
                quants = self.env['stock.quant'].sudo().search(domain)
                qty_available = sum([x.quantity for x in quants])
                vals.update({'theoretical_qty': qty_available})
            elif tracking == 'lot':
                domain.append(('lot_id', '=', line.lot_id.id))
                quants = self.env['stock.quant'].sudo().search(domain)
                qty_available = sum([x.quantity for x in quants])
                vals.update({'theoretical_qty': qty_available, 'lot_id': line.lot_id.id})

            self.env['setu.inventory.count.session.line'].create(vals)
        self.state = 'Approved'
        self.create_inventory_adj()

    def action_open_user_mistake_lines(self):
        user_mistake_lines = self.line_ids.filtered(lambda l: l.user_calculation_mistake)
        ids = user_mistake_lines.ids if user_mistake_lines else []
        return {
            'name': 'User Calculation Mistake Lines',
            'view_mode': 'tree',
            'view_id': self.sudo().env.ref(
                'setu_inventory_count_management_18.setu_stock_inventory_count_line_tree_view').id,
            'res_model': 'setu.stock.inventory.count.line',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ids)]
        }

    def reset_to_draft(self):
        self.state = 'Draft'
        # self.is_single_session = False
        if not self.count_id:
            self.line_ids.unlink()
        else:
            self.line_ids.state = 'Pending Review'
            self.line_ids.counted_qty = 0

    def cancel(self):
        sessions = self.session_ids.filtered(lambda s: s.state != 'Cancel')
        if sessions:
            sessions_str = "\n".join(set(sessions.mapped('name')))
            raise ValidationError(
                _("This Inventory Count cannot be cancelled because few of the sessions are already running, "
                  "\n%s" % sessions_str))
        if self.state == 'Draft':
            self.state = 'Cancel'
            for session in self.session_ids:
                session.state = 'Cancel'
            for line in self.line_ids:
                line.qty_in_stock = line.theoretical_qty

    def _compute_rejected_lines_count(self):
        for rec in self:
            rejected_lines = rec.line_ids.filtered(lambda l: l.state == 'Reject')
            rec.rejected_lines_count = len(rejected_lines) if rejected_lines else 0

    def _compute_create_count_bool(self):
        for rec in self:
            if self.state in ('To Be Approved', 'Done') and self.rejected_lines_count > 0:
                # if rec.session_ids and rec.session_ids.filtered(lambda s: s.state != 'Cancel'):
                rec.create_count_bool = True
            else:
                rec.create_count_bool = False
            # else:
            #     rec.create_count_bool = False

    def _compute_create_session_bool(self):
        for rec in self:
            if rec.state in ('Draft', 'In Progress'):
                if self.type == 'Single Session':
                    session = self.session_ids.filtered(lambda l: l.state not in ('Cancel'))

                    if not session:
                        self.create_session_bool = True
                    else:
                        self.create_session_bool = False
                else:
                    self.create_session_bool = True
            else:
                rec.create_session_bool = False

    def _compute_start_inventory_bool(self):
        for rec in self:
            rec.start_inventory_bool = True
            if rec.inventory_adj_ids and rec.inventory_adj_ids.filtered(lambda a: a.state not in ('cancel')):
                rec.start_inventory_bool = False
                continue
            adj_lines = rec.line_ids.filtered(lambda l: l.is_discrepancy_found and l.state == 'Approve')
            if not adj_lines:
            	rec.start_inventory_bool = False

    def _compute_count_session_ids(self):
        for rec in self:
            session = rec.session_ids.filtered(lambda l: l.state not in ('Cancel'))
            rec.count_session_ids = len(session)

    def _compute_count_ids(self):
        for rec in self:
            rec.re_count_ids = len(rec.count_ids)

    def get_products_from_setu_reports(self):
        action = \
            self.sudo().env.ref('setu_inventory_count_management_18.get_products_from_setu_reports_act_window').read()[0]
        wizard = self.env['get.products.from.adv.inv.rep.wizard'].create({})
        wizard.warehouse_ids = self.warehouse_id
        action.update({
            'res_id': wizard.id
        })
        return action

    def action_open_sessions(self):
        sessions_to_open = self.session_ids
        action = self.sudo().env.ref('setu_inventory_count_management_18.inventory_count_session_act_window').read()[0]
        if len(sessions_to_open) > 1:
            action['domain'] = [('id', 'in', sessions_to_open.ids)]
        elif len(sessions_to_open) == 1:
            action['views'] = [
                (self.sudo().env.ref('setu_inventory_count_management_18.inventory_count_session_form_view').id, 'form')]
            action['res_id'] = sessions_to_open.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_open_counts(self):
        count_to_open = self.count_ids
        action = self.sudo().env.ref('setu_inventory_count_management_18.new_inventory_count_act_window').read()[0]
        if len(count_to_open) > 1:
            action['domain'] = [('id', 'in', count_to_open.ids)]
        elif len(count_to_open) == 1:
            action['views'] = [(self.sudo().env.ref(
                'setu_inventory_count_management_18.setu_stock_inventory_count_form_view').id, 'form')]
            action['res_id'] = count_to_open.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def create(self, vals_list):
        seq = self.env['ir.sequence'].next_by_code('setu.inventory.count.seq')
        vals_list.update({
            'name': seq
        })
        return super(StockInvCount, self).create(vals_list)

    def create_session(self):
        if self.type == 'Multi Session':
            is_multi_session = True
        else:
            is_multi_session = False
        session_creator_wiz = self.env['inventory.session.creator'].create({'inventory_count_id': self.id,
                                                                            'is_multi_session': is_multi_session})
        products = self.product_ids.ids
        session_creator_wiz.write({'product_ids': [(6, 0, products)]})

        return {
            'name': 'Create Session',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'products': products},
            'res_model': 'inventory.session.creator',
            'type': 'ir.actions.act_window',
            'view_id': self.sudo().env.ref('setu_inventory_count_management_18.inventory_session_creator_form_view').id,
            'res_id': session_creator_wiz.id,
            'target': 'new'
        }

    def create_re_count(self):
        # is_multi_session = True
        session_creator_wiz = self.env['setu.inventory.session.validate.wizard'].create({})
        # products = self.product_ids.ids
        # session_creator_wiz.write({'product_ids': [(6, 0, products)]})
        return {
            'name': 'Create Inventory Count',
            'view_type': 'form',
            'view_mode': 'form',
            # 'context': {'products': products},
            'res_model': 'setu.inventory.session.validate.wizard',
            'type': 'ir.actions.act_window',
            'view_id': self.sudo().env.ref('setu_inventory_count_management_18.inventory_count_validate_form_view').id,
            'res_id': session_creator_wiz.id,
            'target': 'new'
        }

    def reject_inventory_count(self):
        self.state = 'Rejected'
        for session in self.session_ids:
            session.state = 'Cancel'

    def action_open_inventory_adj(self):
        inventory_adjs = self.inventory_adj_ids
        action = self.sudo().env.ref('setu_inventory_count_management_18.setu_stock_inventory_act_window').read()[0]
        if len(inventory_adjs) > 1:
            action['domain'] = [('id', 'in', inventory_adjs.ids)]
        elif len(inventory_adjs) == 1:
            action['views'] = [
                (self.sudo().env.ref('setu_inventory_count_management_18.setu_stock_inventory_form_view').id, 'form')]
            action['res_id'] = inventory_adjs.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def approve_inventory_count(self):
        session_ids = self.session_ids.filtered(lambda s: s.state != 'Cancel')
        session_states = session_ids.mapped('state')
        if 'Draft' in session_states or 'In Progress' in session_states:
            raise ValidationError(_("Please validate all sessions before approving the Inventory Count."))
        if self.type == "Multi Session":
            rejected_lines = self.line_ids.filtered(lambda p: p.state == 'Reject')
            pending_lines = self.line_ids.filtered(lambda p: p.state == 'Pending Review')
            if pending_lines:
                raise ValidationError(
                    _('Please check and set the state in all count lines of this count to open this count again.'))
            if rejected_lines:
                return {
                    'name': 'Rejected Lines Found!!!',
                    'view_mode': 'form',
                    'view_id': self.sudo().env.ref(
                        'setu_inventory_count_management_18.inventory_count_validate_form_view').id,
                    'res_model': 'setu.inventory.session.validate.wizard',
                    'type': 'ir.actions.act_window',
                    'target': 'new'
                }
        self.state = 'Approved'
        self.create_inventory_adj()

    def unlink(self):
        for count in self:
            if count.state != 'Draft':
                raise ValidationError(_(f'You cannot delete the Inventory Count once it is in {count.state} state.'))
        # return super(StockInvCount, self).unlink()
        if self.session_ids:
            self.session_ids.with_context(from_count=True).unlink()
        return super(StockInvCount, self).unlink()

    def create_inventory_adj(self):
        if self.type == 'Single Session':
            lines_to_adjust = self.line_ids.filtered(lambda l: l.is_discrepancy_found)
        else:
            lines_to_adjust = self.line_ids.filtered(lambda l: l.is_discrepancy_found and l.state == 'Approve')
        if lines_to_adjust:
            self._create_inventory_adj(lines_to_adjust)
            try:
                self.message_post(
                    body="<div style='color:red; margin:10px 30px;;'>&bull; Discrepancy found. <strong>Inventory Adjustment</strong> is created.</div>")
            except Exception as e:
                pass
        else:
            #if self.type != 'Single Session':
            #    raise ValidationError(_("No Approved lines found to adjust the inventory."))
            try:
                self.message_post(
                    body="<div style='color:green; margin:10px 30px;;'>&bull; No discrepancy found. <strong>Inventory Adjustment</strong> is not created.</div>")
            except Exception as e:
                pass

    def get_all_counts(self):
        list = [self.id]
        while True:
            if self.count_id:
                list.append(self.count_id.id)
                list_2 = self.count_id.get_all_counts()
                if list_2:
                    list.extend(list_2)
            break
        return set(list)

    def _create_inventory_adj(self, count_lines):
        if count_lines:
            lines = []
            for l in count_lines:
                if l.product_id.tracking != 'serial':
                    lines.append((
                    0, 0, {'product_id': l.product_id.id, 'product_uom_id': l.product_id.uom_id.id,
                           'location_id': l.location_id.id, 'product_qty': l.counted_qty,
                           'prod_lot_id': l.lot_id.id if l.lot_id else False,
                           'theoretical_qty': l.qty_in_stock}))
                else:
                    if l.serial_number_ids:
                        existing_serial_numbers = self.env['stock.quant'].sudo().search(
                                [('location_id', '=', l.location_id.id),
                                 ('lot_id', 'in', l.serial_number_ids.ids),
                                 ('product_id', '=', l.product_id.id)])
                        settlement_serial_ids = l.serial_number_ids - existing_serial_numbers.lot_id
                        for s in settlement_serial_ids:
                            lot_exists = self.env['stock.quant'].sudo().search(
                                [('location_id', '=', l.location_id.id),
                                 ('lot_id', '=', s.id),
                                 ('product_id', '=', l.product_id.id)]).mapped('lot_id')
                            lines.append((
                                0, 0, {'product_id': l.product_id.id, 'product_uom_id': l.product_id.uom_id.id,
                                       'location_id': l.location_id.id, 'product_qty': 1,
                                       'prod_lot_id': l.lot_id.id if l.lot_id else False,
                                       'serial_number_ids': [(6, 0, s.ids)],
                                       'theoretical_qty': s.product_qty if lot_exists else 0}))
                    if l.not_found_serial_number_ids:
                        for m in l.not_found_serial_number_ids:
                            lot_exists = self.env['stock.quant'].sudo().search(
                                [('location_id', '=', l.location_id.id),
                                 ('lot_id', '=', m.id),
                                 ('quantity', '>', 0),
                                 ('product_id', '=', l.product_id.id)]).mapped('lot_id')
                            lines.append((
                                0, 0, {'product_id': l.product_id.id, 'product_uom_id': l.product_id.uom_id.id,
                                       'location_id': l.location_id.id, 'product_qty': 0,
                                       'prod_lot_id': l.lot_id.id if l.lot_id else False,
                                       'serial_number_ids': [(6, 0, m.ids)],
                                       'theoretical_qty': m.product_qty if lot_exists else 0}))



            adj = self.env['setu.stock.inventory'].create({
                'location_id': self.location_id.id,
                'name': 'ADJ - ' + self.name,
                'inventory_count_id': self.id,
                'partner_id': self.approver_id.id,
                'date': self.inventory_count_date,
                'line_ids': lines
            })
            adj.inventory_count_id = self
            adj.action_start()
            adj.product_ids = count_lines.mapped('product_id')

    def _create_inventory_adj_old(self, count_lines):
        if count_lines:
            # serial_lines = count_lines.filtered(lambda x:x.product_id.tracking=='serial')
            # count_lines -= serial_lines
            lines = []
            # if count_lines:
            for l in count_lines:
                # new_serial_count = 0
                if l.product_id.tracking == 'serial':
                    lot_ids = self.env['stock.quant'].sudo().search(
                                    [('location_id', '=', l.location_id.id),
                                     ('quantity', '=', 1),
                                     ('product_id', '=', l.product_id.id)]).mapped('lot_id')
                    new_serial = (l.serial_number_ids) - (lot_ids - l.not_found_serial_number_ids)
                    # new_serial_count = len(new_serial)
                lines.append((
                0, 0, {'product_id': l.product_id.id, 'product_uom_id': l.product_id.uom_id.id,
                       'location_id': l.location_id.id, 'product_qty': l.counted_qty,
                       'prod_lot_id': l.lot_id.id if l.lot_id else False,
                       'not_found_serial_number_ids': [(6, 0, l.not_found_serial_number_ids.ids)],
                       'new_serial_number_ids': [(6, 0, new_serial.ids)],
                       # 'new_serial_count': new_serial_count,
                       'serial_number_ids': [(6, 0, l.serial_number_ids.ids)],
                       'theoretical_qty': l.qty_in_stock}))
            # lines = list(map(lambda l: ,
            #                  count_lines))
            # if serial_lines:
            #     for sl in serial_lines:
            #         lot_ids = self.env['stock.quant'].sudo().search(
            #             [('location_id', '=', sl.location_id.id),
            #              ('quantity', '=', 1),
            #              ('product_id', '=', sl.product_id.id)]).mapped('lot_id')
            #         if sl.serial_number_ids:
            #
            #             new_serial = (sl.serial_number_ids) - (lot_ids - sl.not_found_serial_number_ids)
            #             theoretical_qty = len(sl.serial_number_ids)-len(new_serial)
            #             lines.append(
            #                 (0, 0, {'product_id': sl.product_id.id, 'product_uom_id': sl.product_id.uom_id.id,
            #                         'location_id': sl.location_id.id, 'product_qty': sl.counted_qty,
            #                         'serial_number_ids': [(6, 0, sl.serial_number_ids.ids)],
            #                         'theoretical_qty': theoretical_qty}))
            #         if sl.not_found_serial_number_ids:
            #             lines.append(
            #                 (0, 0, {'product_id': sl.product_id.id, 'product_uom_id': sl.product_id.uom_id.id,
            #                        'location_id': sl.location_id.id, 'product_qty': 0,
            #                        'serial_number_ids': [(6, 0, sl.not_found_serial_number_ids.ids)],
            #                        'theoretical_qty': len(sl.not_found_serial_number_ids)}))



            adj = self.env['setu.stock.inventory'].create({
                'location_id': self.location_id.id,
                'name': 'ADJ - ' + self.name,
                'inventory_count_id': self.id,
                'partner_id': self.approver_id.id,
                'date': self.inventory_count_date,
                'line_ids': lines
            })
            adj.inventory_count_id = self
            adj.action_start()
            adj.product_ids = count_lines.mapped('product_id')

    # @api.onchange('location_id')
    # def onchange_location_id(self):
    #     if self.location_id:
    #         self.warehouse_id = self.location_id.get_warehouse()

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
