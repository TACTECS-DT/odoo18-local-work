# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tools.safe_eval import safe_eval
from .selection import State, ExpiringState, KanbanState, ContractType, Visibility


class PartnerContract(models.Model):
    _name = 'xf.partner.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Partner Contract'
    _order = 'date_start, type, name'

    _min_user_group = 'xf_partner_contract.group_xf_partner_contract_user'

    # Fields
    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        tracking=1,
    )
    ref = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        tracking=1,
    )
    active = fields.Boolean(
        default=True,
    )
    kanban_state = fields.Selection(
        string='Kanban State',
        selection=KanbanState.list,
        default=KanbanState.default,
        tracking=10,
        copy=False,
    )
    state = fields.Selection(
        string='State',
        selection=State.list,
        default=State.default,
        required=True,
        readonly=True,
        copy=False,
        tracking=10,
    )
    expiring_state = fields.Selection(
        string='Expiring State',
        selection=ExpiringState.list,
        default=ExpiringState.default,
        required=True,
        copy=False,
        help='The stage to which the contract will be moved after expiring',
    )
    type = fields.Selection(
        string='Type',
        selection=ContractType.list,
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        required=True,
        readonly=True,
        tracking=1,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
        tracking=1,
    )
    payment_term_id = fields.Many2one(
        string='Payment Terms',
        comodel_name='account.payment.term',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True,
    )
    user_id = fields.Many2one(
        string='Responsible User',
        comodel_name='res.users',
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
        tracking=5,
    )
    privacy_visibility = fields.Selection(
        string='Visibility',
        selection=Visibility.list,
        default=Visibility.default,
        required=True,
        index=True,
        help="Defines the visibility of the contract:\n"
             "- All Internal Users: employees may see all contracts.\n"
             "- Invited Internal Users: employees may only see the followed contracts.\n"
    )
    amount = fields.Monetary(
        string='Cost',
        readonly=True,
        tracking=1,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True,
        tracking=1,
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today,
        help='Start date of the contract.',
        readonly=True,
        tracking=5,
    )
    date_end = fields.Date(
        string='End Date',
        help='End date of the contract (if it is a fixed-term contract).',
        readonly=True,
        tracking=5,
    )
    date_last_payment = fields.Date(
        string='Last Payment Date',
        help='The date after which the system will not allow payments to be made',
        readonly=True,
        tracking=5,
    )
    days_left = fields.Integer(
        compute='_compute_days_left',
        string='Days Left',
    )
    notes = fields.Text(
        string='Terms and Conditions',
        help='Write here all supplementary information relative to this contract',
        copy=False,
        readonly=True,
    )
    contract_approval = fields.Selection(
        string='Use Approval Route',
        related='company_id.contract_approval',
        readonly=True,
    )
    approval_team_id = fields.Many2one(
        string='Approval Team',
        comodel_name='xf.partner.contract.team',
        ondelete='restrict',
        domain="[('company_id', '=', company_id)]",
        readonly=True,
        tracking=10,
        groups=_min_user_group,
    )
    has_access = fields.Boolean(
        compute='_compute_access',
    )
    can_edit = fields.Boolean(
        compute='_compute_access',
    )
    approver_ids = fields.One2many(
        string='Approvers',
        comodel_name='xf.partner.contract.approver',
        inverse_name='contract_id',
        readonly=True,
        groups=_min_user_group,
    )
    current_approver = fields.Many2one(
        string='Current Approver',
        comodel_name='xf.partner.contract.approver',
        compute='_compute_approver',
    )
    next_approver = fields.Many2one(
        string='Next Approver',
        comodel_name='xf.partner.contract.approver',
        compute='_compute_approver',
    )
    is_current_approver = fields.Boolean(
        string='Is Current Approver',
        compute='_compute_approver'
    )
    is_fully_approved = fields.Boolean(
        string='Is Fully Approved',
        compute='_compute_approver'
    )
    comments = fields.Text(
        string='Comments',
        readonly=True,
    )
    use_lines = fields.Boolean(
        string='Use Lines',
        default=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        string='Lines',
        comodel_name='xf.partner.contract.line',
        inverse_name='contract_id',
        readonly=True,
    )
    invoice_ids = fields.One2many(
        string='Invoices',
        comodel_name='account.move',
        inverse_name='contract_id',
        readonly=True,
    )
    
    invoice_ids_count = fields.Integer(
        compute='_compute_invoice_ids_count'
    )
    sale_id = fields.One2many(
        string='Sale Order',
        comodel_name='sale.order',
        inverse_name='contract_id',
        readonly=True,
    )
    sale_ids_count = fields.Integer(
        compute='_sale_ids_count'
    )
    @api.depends('sale_id')
    def _sale_ids_count(self):
        for record in self:
            record.sale_ids_count = len(record.sale_id)
    # Compute and search fields, in the same order of fields declaration

    @api.depends('date_end', 'state')
    def _compute_days_left(self):
        """return a dict with as value for each contract an integer
        if contract is running or expired, return 0
        if contract is in a closed state, return -1
        otherwise return the number of days before the contract expires
        """
        for record in self:
            if record.date_end and record.state in ('running', 'expired'):
                today = fields.Date.from_string(fields.Date.today())
                expiration_date = fields.Date.from_string(record.date_end)
                diff_time = (expiration_date - today).days
                record.days_left = diff_time > 0 and diff_time or 0
            else:
                record.days_left = -1

    @api.depends('approver_ids.state')
    def _compute_approver(self):
        for contract in self:
            if not self.user_has_groups(self._min_user_group) or not contract.approval_team_id:
                contract.next_approver = False
                contract.current_approver = False
                contract.is_current_approver = False
                contract.is_fully_approved = False
                continue
            next_approvers = contract.approver_ids.filtered(lambda a: a.state == 'to approve')
            contract.next_approver = next_approvers[0] if next_approvers else False

            current_approvers = contract.approver_ids.filtered(lambda a: a.state == 'pending')
            contract.current_approver = current_approvers[0] if current_approvers else False

            contract.is_current_approver = ((contract.current_approver and contract.current_approver.user_id == self.env.user)
                                            or self.env.is_superuser())

            approved_lines = contract.approver_ids.filtered(lambda a: a.state == 'approved')
            contract.is_fully_approved = len(approved_lines) == len(contract.approver_ids)

    @api.depends('state', 'user_id', 'approval_team_id')
    def _compute_access(self):
        """
        Compute if the current user has access to edit contract
        :return:
        """
        for contract in self:
            if not self.user_has_groups(self._min_user_group):
                contract.has_access = False
                contract.can_edit = False
                continue

            # Responsible person and superuser has initial access to edit/manage contract
            contract.has_access = self.env.user == contract.user_id or self.env.is_superuser()
            if not contract.has_access and contract.approval_team_id:
                team_users = contract.approval_team_id.approver_ids.mapped('user_id')
                # Also approval team leader and members have access to edit/manage contract
                contract.has_access = (self.env.user == contract.approval_team_id.user_id or self.env.user in team_users)

            # Whoever has access can edit it in the draft stage or before own approval according team settings
            contract.can_edit = ((contract.state == 'draft' and contract.has_access)
                                 or (contract.is_current_approver and contract.current_approver.can_edit))

    @api.depends('invoice_ids')
    def _compute_invoice_ids_count(self):
        for record in self:
            record.invoice_ids_count = len(record.invoice_ids)

    # Constraints and onchanges

    @api.constrains('active', 'state')
    def _check_active_state(self):
        for record in self:
            if record.active:
                continue
            if record.state == 'running':
                raise UserError(_('You cannot archive current contracts! Please close them first!'))
            if record.state == 'approval':
                raise UserError(_('You cannot archive contracts when they are in the approval stage! Please cancel them first!'))

    @api.constrains('date_start', 'date_end')
    def _check_date_end(self):
        for record in self:
            if record.date_start and record.date_end and record.date_end < record.date_start:
                raise ValidationError(_('End Date must be greater than Start Date!'))

    @api.onchange('use_lines')
    def _onchange_use_lines(self):
        if not self.use_lines and self.line_ids:
            self.use_lines = True
            raise ValidationError(_('To disable using lines please remove all lines first!'))

    @api.constrains('date_start', 'date_last_payment')
    def _check_date_last_payment(self):
        for record in self:
            if record.date_start and record.date_last_payment and record.date_last_payment < record.date_start:
                raise ValidationError(_('Last Payment Date must be greater than Start Date!'))

    # Built-in methods overrides

    def write(self, vals):
        if 'state' in vals and 'kanban_state' not in vals:
            # Reset kanban state when regular state is changed
            vals['kanban_state'] = KanbanState.default
        return super(PartnerContract, self).write(vals)

    def _track_subtype(self, init_values):
        self.ensure_one()
        init_state = init_values.get('state')
        State.check_state_flow_rule(init_state, self.state)

        if init_state and self.state == 'running':
            if init_state == 'approval':
                return self.env.ref('xf_partner_contract.mt_contract_approved')
            return self.env.ref('xf_partner_contract.mt_contract_confirmed')
        elif init_state and self.state == 'approval':
            return self.env.ref('xf_partner_contract.mt_contract_confirmed_and_sent')
        elif init_state and self.state == 'cancelled':
            return self.env.ref('xf_partner_contract.mt_contract_cancelled')

        return super(PartnerContract, self)._track_subtype(init_values)

    # Action methods

    def action_confirm(self):
        for contract in self:
            if not contract.approval_team_id:
                contract.set_state('draft', 'running')
            else:
                # Generate approval route and send PO to approve
                contract.generate_approval_route()
                if contract.next_approver:
                    # If approval route is generated and there is next approver
                    contract.set_state('draft', 'approval')
                    # And send request to approve
                    contract.send_to_approve()
                else:
                    # If there are not approvers, do default behaviour and move contract to the "Running" state
                    contract.set_state('draft', 'running')
        return True

    def action_approve(self):
        for contract in self:
            if not contract.approval_team_id:
                # Run contract if approval team is not set
                contract.set_state(None, 'running')
            elif contract.current_approver:
                if contract.is_current_approver:
                    # If current user is current approver (or superuser) update state as "approved"
                    contract.current_approver.state = 'approved'
                    contract.message_post(body=_('Contract approved by %s') % self.env.user.name)
                    # Check is there is another approver
                    if contract.next_approver:
                        # Send request to approve is there is next approver
                        contract.send_to_approve()
                    elif contract.is_fully_approved:
                        # If approval is finished, send notification
                        contract.send_contract_approved()
                        # Run contract
                        contract.set_state(None, 'running')
                else:
                    raise AccessError(_('The contract is waiting for the approval from {}') % contract.current_approver.display_name)

    def action_return_for_correction_wizard(self):
        self.ensure_one()
        view = self.env.ref('xf_partner_contract.return_for_correction_wizard')
        return {
            'name': _('Return for Correction'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self._name,
            'res_id': self.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'type': 'ir.actions.act_window',
            'domain': [],
            'context': {},
            'target': 'new',
        }

    def action_return_for_correction(self):
        for contract in self:
            prev_state = State.get_prev_value(contract.state)
            if not prev_state:
                raise UserError(_('Incorrect Action!'))
            comments = contract.comments
            contract.set_state(None, 'draft')
            # Ask responsible person for correction
            contract.message_post_with_view(
                'xf_partner_contract.return_for_correction',
                subject=_('Contract Returned for Correction: %s') % (contract.name,),
                values={'comments': comments},
                composition_mode='mass_mail',
                partner_ids=[(4, contract.user_id.partner_id.id)],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False,
                subtype_id=self.env.ref('mail.mt_note').id)

    def action_draft(self):
        self._check_access_before_update()
        self.set_state(None, 'draft')

    def action_renew(self):
        self._check_access_before_update()
        self.set_state(None, 'to_renew')

    def action_close(self):
        self._check_access_before_update()
        self.set_state(None, 'closed')

    def action_cancel(self):
        self._check_access_before_update()
        self.set_state(None, 'cancelled')

    def create_sale_order(self):
       
        for rec in self:
            values = {
                'name': rec.name,
                
                'partner_id': rec.partner_id.id,
                'contract_id':rec.id,
                'user_id': rec.user_id.id,
           

            }
            order_lines = []
            for quant in rec.line_ids:
                
                if quant.quantity > 0:
                    line = [0, False, {
                        'qty_delivered':0,
                        'product_id': quant.product_id.id,
                        # 'product_uom': quant.product_id.uom_id.id,
                        'sequence': quant.product_id.sequence,
                        'price_unit': quant.price_unit,
                        'product_uom_qty': quant.quantity,
                        'state': 'draft',
                        # 'qty_delivered_updateable': True,
                        'invoice_status': 'no',
                        'name': quant.product_id.name, }]
                    order_lines.append(line)

            values['order_line'] = order_lines
            sale_order = self.env['sale.order'].create(values)
            #sale_order.action_confirm()
            
            
        return self.action_view_saleorder(sale_order)
        pass
    def action_view_saleorder(self, invoices=False):
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the contract, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['sale_id'])
            invoices = self.sale_id
        act_window_close = {'type': 'ir.actions.act_window_close'}
        #move_type = self._get_move_type()
        action = self.env['ir.actions.actions']._for_xml_id("sale.action_orders")
        # choose the view_mode accordingly
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
            form_view = [(self.env.ref('sale.view_order_tree').id, 'list')]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = act_window_close

        context={}
        # context = {
        #     'default_move_type': move_type,
        # }
        if len(self) == 1:
            context.update({
                'default_contract_id': self.id,
                'default_partner_id': self.partner_id.id,
                # 'default_invoice_payment_term_id': (self.payment_term_id.id
                #                                     or self.partner_id.property_payment_term_id.id
                #                                     or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id')),
                'default_user_id': self.user_id.id,
            })
        # action['context'] = context
        return action
    def action_create_customer_sale_order(self):
        return self.create_sale_order()
        pass
    def action_create_customer_invoice(self):
        return self.action_create_invoice()

    def action_create_vendor_bill(self):
        return self.action_create_invoice()

    def action_create_invoice(self):
        moves = self.env['account.move']
        for contract in self:
            invoice_vals = contract._prepare_invoice()
            move = self.env['account.move'].create(invoice_vals)
            move.apply_contract_lines()
            moves |= move
        return self.action_view_invoice(moves)

    def action_view_invoice(self, invoices=False):
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the contract, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids
        act_window_close = {'type': 'ir.actions.act_window_close'}
        move_type = self._get_move_type()
        if move_type == 'in_invoice':
            action = self.env['ir.actions.actions']._for_xml_id('account.action_move_in_invoice_type')
        elif move_type == 'out_invoice':
            action = self.env['ir.actions.actions']._for_xml_id("account.action_move_out_invoice_type")
        else:
            action = act_window_close
        # choose the view_mode accordingly
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = act_window_close

        context = {
            'default_move_type': move_type,
        }
        if len(self) == 1:
            context.update({
                'default_contract_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_invoice_payment_term_id': (self.payment_term_id.id
                                                    or self.partner_id.property_payment_term_id.id
                                                    or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id')),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    # Business methods

    def _check_access_before_update(self):
        for contract in self:
            if not contract.has_access:
                raise AccessError(_('Sorry, you are not allowed to edit this contract!'))

    def set_state(self, from_state, to_state, comments=None):
        for record in self:
            if from_state and from_state != record.state:
                raise UserError(_('Incorrect Action!'))
            record.write({'state': to_state, 'comments': comments})

    def send_contract_approved(self):
        for contract in self:
            if not contract.is_fully_approved:
                continue
            partner = contract.user_id.partner_id if contract.user_id else contract.create_uid.partner_id
            contract.message_post_with_view(
                'xf_partner_contract.contract_approved',
                subject=_('Contract Approved: %s') % (contract.name,),
                composition_mode='mass_mail',
                partner_ids=[(4, partner.id)],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False,
                subtype_id=self.env.ref('mail.mt_note').id)

    def send_to_approve(self):
        for contract in self:
            if contract.state != 'approval' and not contract.approval_team_id:
                continue

            main_error_msg = _('Unable to send approval request to next approver.')
            if contract.current_approver:
                reason_msg = _('The contract must be approved by %s') % contract.current_approver.display_name
                raise UserError("%s %s" % (main_error_msg, reason_msg))

            if not contract.next_approver:
                reason_msg = _("There are no approvers in the selected approval team.")
                raise UserError("%s %s" % (main_error_msg, reason_msg))
            # use sudo as regular user cannot update xf.partner.contract.approver
            contract.sudo().next_approver.state = 'pending'
            # Now next approver became as current
            current_approver_partner = contract.current_approver.user_id.partner_id
            if current_approver_partner not in contract.message_partner_ids:
                contract.message_subscribe([current_approver_partner.id])
            contract.with_user(contract.user_id).message_post_with_view(
                'xf_partner_contract.request_to_approve',
                subject=_('Contract Approval: %s') % (contract.name,),
                composition_mode='mass_mail',
                partner_ids=[(4, current_approver_partner.id)],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False,
                subtype_id=self.env.ref('mail.mt_note').id)

    def compute_custom_condition(self, team_approver):
        self.ensure_one()
        localdict = {'CONTRACT': self, 'USER': self.env.user}
        if not team_approver.custom_condition_code:
            return True
        try:
            safe_eval(team_approver.custom_condition_code, localdict, mode='exec', nocopy=True)
            return bool(localdict['result'])
        except Exception as e:
            raise UserError(_('Wrong condition code defined for %s. Error: %s') % (team_approver.display_name, e))

    def generate_approval_route(self):
        """
        Generate approval route for contract
        :return:
        """
        for contract in self:
            if not contract.approval_team_id:
                continue
            if contract.approver_ids:
                # reset approval route
                contract.approver_ids.unlink()
            for team_approver in contract.approval_team_id.approver_ids:

                custom_condition = contract.compute_custom_condition(team_approver)
                if not custom_condition:
                    # Skip approver, if custom condition for the approver is set and the condition result is not True
                    continue

                min_amount = team_approver.company_currency_id._convert(
                    team_approver.min_amount,
                    contract.currency_id,
                    contract.company_id,
                    contract.date_start or fields.Date.today())
                if min_amount > contract.amount:
                    # Skip approver if Minimum Amount is greater than Amount
                    continue
                max_amount = team_approver.company_currency_id._convert(
                    team_approver.max_amount,
                    contract.currency_id,
                    contract.company_id,
                    contract.date_start or fields.Date.today())
                if max_amount and max_amount < contract.amount:
                    # Skip approver if Maximum Amount is set and less than Amount
                    continue

                # Add approver to the contract
                self.env['xf.partner.contract.approver'].create({
                    'sequence': team_approver.sequence,
                    'team_id': team_approver.team_id.id,
                    'user_id': team_approver.user_id.id,
                    'role': team_approver.role,
                    'can_edit': team_approver.can_edit,
                    'min_amount': team_approver.min_amount,
                    'max_amount': team_approver.max_amount,
                    'contract_id': contract.id,
                    'team_approver_id': team_approver.id,
                })

    @api.model
    def update_state(self):
        plus_7d = fields.Date.to_string(date.today() + relativedelta(days=7))
        plus_1d = fields.Date.to_string(date.today() + relativedelta(days=1))
        contracts_to_block = self.search([
            ('state', '=', 'running'), ('kanban_state', '!=', 'blocked'),
            '|',
            '&',
            ('date_end', '<=', plus_7d),
            ('date_end', '>=', plus_1d),
            '&',
            ('date_last_payment', '<=', plus_7d),
            ('date_last_payment', '>=', plus_1d),
        ])

        for contract in contracts_to_block:
            contract.activity_schedule(
                'mail.mail_activity_data_todo', contract.date_end,
                _('The contract "%s" is about to expire.', contract.name),
                user_id=contract.user_id.id or self.env.uid)

        contracts_to_block.write({'kanban_state': 'blocked'})

        expired_contracts = self.search([
            ('state', '=', 'running'),
            '|',
            ('date_end', '<=', plus_1d),
            ('date_last_payment', '<=', plus_1d),
        ])

        for expired_contract in expired_contracts:
            expired_contract.write({'state': expired_contract.expiring_state})
        return True

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to always display all states. """
        if groupby and groupby[0] == "state":
            return [self._state_group(state, domain, groupby) for state in State.list]
        else:
            return super(PartnerContract, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)

    def _state_group(self, state, domain, groupby):
        state_domain = [('state', '=', state[0])] + domain
        return {
            'state': state[0],
            'state_count': self.search_count(state_domain),
            '__context': {'group_by': groupby[1:]},
            '__domain': state_domain,
            '__fold': state[0] in State.folded
        }

    def _get_move_type(self):
        if self.type == 'sale':
            return 'out_invoice'
        if self.type == 'purchase':
            return 'in_invoice'

        raise UserError(_('Unsupported type of contract'))

    def _prepare_invoice(self, move_type=False):
        self.ensure_one()
        return {
            'move_type': move_type or self._get_move_type(),
            'contract_id': self.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'invoice_origin': self.ref,
            'narration': self.notes,
            'invoice_payment_term_id': self.payment_term_id.id,
        }


class PartnerContractLine(models.Model):
    _name = 'xf.partner.contract.line'
    _description = 'Partner Contract Line'
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='xf.partner.contract',
        required=True,
        ondelete='cascade',
    )
    contract_type = fields.Selection(
        related='contract_id.type',
        readonly=True,
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )
    product_uom_category_id = fields.Many2one(
        comodel_name='uom.category',
        related='product_id.uom_id.category_id',
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        string='Unit of Measure',
        comodel_name='uom.uom',
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    name = fields.Char(
        string='Label',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        digits='Product Unit of Measure',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        related='contract_id.partner_id',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        related='contract_id.company_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='contract_id.currency_id',
        readonly=True,
    )
    price_unit = fields.Monetary(
        string='Unit Price',
        digits='Product Price',
    )
    discount = fields.Float(
        string='Discount (%)',
        digits='Discount',
        default=0.0,
    )
    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        comodel_name='account.analytic.account',
        check_company=True,
    )
    analytic_tag_ids = fields.Many2many(
        string='Analytic Tags',
        comodel_name='account.analytic.tag',
        check_company=True,
    )

    def _prepare_invoice_line(self, move_id):
        self.ensure_one()
        vals = {
            'display_type': False,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'sequence': self.sequence,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'name': self.name,
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        if move_id:
            vals['move_id'] = move_id
        return vals
