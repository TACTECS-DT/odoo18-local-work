from email.policy import default

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class stockType(models.Model):
    _inherit = 'stock.picking.type'
    is_admin_operation_type = fields.Boolean(string="Is Admin Operation Type")

class AdminWharehouse(models.Model):
    _name = "admin.warehouse"
    _inherit = ['mail.thread', 'mail.activity.mixin','portal.mixin']

    def _compute_access_url(self):
        super(AdminWharehouse, self)._compute_access_url()
        for request in self:
            request.access_url = '/admin/warehouse/%s' % (request.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (_('Warehouse-Request'), self.name)
    def find_to_approve(self):
        domain = []

        if self.env.user.has_group('surgi_admin_wharehouse.Warehouse_admin_team_approver'):
            obj = self.env['admin.warehouse'].search([('user_id', '=', self.env.user.id), ('state', '=', ['draft','submit'])])
            for rec in obj:
                domain.append(rec.id)
        else:
            domain=[]
            print(domain)
        return domain

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def buttonToApproveAction(self):
        value = {
            'name': 'To Approve',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'res_model': 'admin.warehouse',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.find_to_approve())],
            'context': {'edit': 1, 'create': 1,},
        }
        return value

    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('hr_expense.group_hr_expense_user') or self.user_has_groups('account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('hr_expense.group_hr_expense_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]
        return res
    @api.model
    def _default_employee_id(self):
        employee = self.env.user.employee_id
        if not employee and not self.env.user.has_group('hr_expense.group_hr_expense_team_approver'):
            raise ValidationError(_('The current user has no related employee. Please, create one.'))
        return employee
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True, tracking=True, states={'draft': [('readonly', False)]}, default=_default_employee_id, check_company=True, domain= lambda self: self.env['admin.warehouse']._get_employee_id_domain())
    department_id = fields.Many2one(related="employee_id.department_id")
    work_location = fields.Char(related="employee_id.work_location",store=True)
    name = fields.Char(string="Code", copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    date = fields.Date(readonly=True, states={'draft': [('readonly', False)], 'reported': [('readonly', False)], 'refused': [('readonly', False)]}, default=fields.Date.context_today, string="Request Date")
    Description = fields.Text("Description")
    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=False, copy=False, tracking=True,)
    state = fields.Selection([
        ('draft', 'To Submit'),('submit','Submited'),
        ('approved', 'Approved'),
        ('InProgress', 'In Progress'),
        ('received', 'Received'),
        ('refused', 'Refused')
    ],  string='Status', copy=False, index=True, readonly=True, store=True, default='draft', help="Status")
    delivered_user = fields.Char(string="Delivered User")
    employeeDeliverd = fields.Boolean()
    lines_ids = fields.One2many('admin.warehouse.line','admin_warehouse',copy=True)
    createPO = fields.Boolean('Create PO')
    vender_id = fields.Many2one('res.partner',string="Vendor",domain="[('vendor','=',True)]",)
    po_id = fields.Many2one('purchase.order',string="Order")
    def EMpDeliverd(self):
        user = self.env.user.name

        self.write({'delivered_user': user})

        self.write({'employeeDeliverd': True})
    def action_submit(self):

        self.write({'state': 'submit'})
        sumarry = str(self.name) +' Admin Request Waiting Approval'
        for usr in self.user_id:
            activity = self.env['mail.activity'].create({
                'activity_type_id': self.env.ref("mail.mail_activity_data_todo").id,
                'user_id': usr.id,
                'res_id': self.id,
                'summary': sumarry,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'admin.warehouse')], limit=1).id,
            })
            print(usr)
            print(activity)
            print(usr.name)
    def action_create_po(self):
        if not self.vender_id:
            raise ValidationError('Please provide a Vendor')
        line_vals =[]
        vals = {}
        b2b_lines = self.lines_ids
        for line in b2b_lines:
            line_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'name': line.product_id.name,
                'product_qty': line.quantity,

            }))
        vals = {
            'partner_id': self.vender_id.id,
            'po_type': 'Administrative',
            'order_line': line_vals,
            }
        po = self.env['purchase.order'].sudo().create(vals)
        print(po)
        print(b2b_lines)
        print('--------------------------------',line_vals)
        self.po_id = po.id
        self.write({'state': 'InProgress'})
    def action_view_po(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        requests = self.env['purchase.order'].search([('id','=',self.po_id.id)])
        tools = [r.id for r in requests]
        action['domain'] = [('id', 'in', tools)]
        return action
    def name_get(self):
        res = []
        for rec in self:
            name = u"{}/ {}/ {}".format(rec.name, rec.employee_id.name,rec.department_id.name,)
            res.append((rec.id, name))
        return res

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for sheet in self:

            sheet.user_id = sheet.employee_id.expense_manager_id or sheet.employee_id.parent_id.user_id

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('admin.warehouse.seq') or _('New')
        res = super(AdminWharehouse, self).create(vals)
        return res

    def approve_expense_sheets(self):
        if not self.user_has_groups('surgi_admin_wharehouse.Warehouse_admin_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve Request"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager') and not  self.user_has_groups('surgi_admin_wharehouse.Warehouse_admin_team_approver'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own Request"))

            if not self.env.user in current_managers and not self.user_has_groups(
                    'hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only approve your department Request"))

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no reports to approve.'),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        filtered_sheet = self.filtered(lambda s: s.state in ['draft','submit'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'approved', 'user_id': sheet.user_id.id or self.env.user.id})
        notification['params'].update({
            'title': _('The reports were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
        activity = self.env['mail.activity'].search([('res_id','=',self.id)])
        print('activity',activity)
        activity.sudo().unlink()
        print('activity',activity)

        return notification


    def create_transfer(self):
        operation_type = self.env['stock.picking.type'].search([('is_admin_operation_type','=',True)])
        if len(operation_type) == 0:
            raise ValidationError('Please Set Operation Type For Admin Operation Type')
        operation_type = operation_type[0]
        vals = {
            'partner_id': self.employee_id.user_id.partner_id.id,
            'picking_type_id' : operation_type.id,
            'location_id': operation_type.default_location_src_id.id,
            'location_dest_id': self.employee_id.user_id.partner_id.property_stock_customer.id,
            'origin':self.name,
        }
        print('val',vals)
        lines = []
        for line in self.lines_ids:
            lines.append((0, 0, line.get_line_vals()))
        print("lines:", lines)
        vals['move_ids_without_package'] = lines
        d = self.env['stock.picking'].create(vals)
        print('trnasfer creted',d)
        print('valsssssssssssssssssss',vals)

    def action_received(self):
        self.create_transfer()
        self.write({'state': 'received'})
    def action_inprogress(self):
        self.write({'state': 'InProgress'})
    def action_refused(self):
        self.write({'state': 'refused'})
    def action_view_tool(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        requests = self.env['stock.picking'].search([('origin','=',self.name)])
        tools = [r.id for r in requests]
        action['domain'] = [('id', 'in', tools)]
        return action


    product_names = fields.Char(
        string="Products",
        compute='_compute_product_names',
        search='_search_product_names'
    )
    product_internal_reference = fields.Char(
        string="Internal Reference",
        compute='_compute_internal_reference',
        search='_search_internal_reference'
    )

    def _compute_product_names(self):
        for record in self:
            record.product_names = ', '.join(
                line.product_id.name for line in record.lines_ids
            )
    def _compute_internal_reference(self):
        for record in self:
            record.product_names = ', '.join(
                line.product_id.default_code for line in record.lines_ids
            )

    def _search_product_names(self, operator, value):
        return [('lines_ids.product_id.name', operator, value)]

    def _search_internal_reference(self, operator, value):
        return [('lines_ids.product_id.default_code', operator, value)]



class AdminWharehouseLine(models.Model):
    _name = "admin.warehouse.line"
    def find_to_category(self):
        obj = self.env['product.product'].search([('product_group','ilike','Admin')])
        res = []
        for rec in obj:
            res.append(rec.categ_id.id)
        domain = [('id','in',res)]
        print(domain)
        return domain
    ProductCategory = fields.Many2one('product.category',string="Product Category",domain=find_to_category)
    product_id = fields.Many2one('product.product', string='Product', tracking=True,domain="[('product_group','ilike','Admin'),('categ_id','=',ProductCategory)]")
    quantity = fields.Float(required=True, string="Quantity", default=1,digits = (12,0))
    reason = fields.Char(string="Reason")
    admin_warehouse = fields.Many2one('admin.warehouse',string="Request Code")
    employee_id = fields.Many2one('hr.employee',related="admin_warehouse.employee_id",string="Employee",store=True)
    user_id = fields.Many2one('res.users',related="admin_warehouse.user_id",string="Request Manager",store=True)
    Request_date = fields.Date(related="admin_warehouse.date",string="Request Date")
    department_id = fields.Many2one('hr.department',related="admin_warehouse.department_id",string="Department",store=True)
    work_location = fields.Char(related="admin_warehouse.work_location",string="Work Location",store=True)
    state = fields.Selection(related="admin_warehouse.state",string="State",store=True)
    def get_line_vals(self):
        return {
                'product_id' : self.product_id.id,
                'product_uom_qty' : self.quantity,
                'product_uom' : self.product_id.uom_id.id,
                'name' : self.product_id.name
            }