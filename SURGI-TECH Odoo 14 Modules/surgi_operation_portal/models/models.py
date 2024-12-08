# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100,):
        args = args or []
        domain = args + ['|', '|','|',
                         ('name', operator, name),
                         ('ref', operator, name),
                         ('phone', operator, name),
                         ('mobile', operator, name)]
        partners = self.search(domain, limit=limit)
        return partners.name_get()
class CrmTeam(models.Model):
    _inherit = 'crm.team'
    member_ids = fields.One2many(
        'res.users', 'sale_team_id', string='Channel Members',
        check_company=True,
        help="Add members to automatically assign their documents to this sales team. You can only be member of one team.")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user,
        domain=[('active','=',True)]
        )
        # domain=lambda self: "[('groups_id', '=', {}), ('company_ids', '=', company_id)]".format(
        #     self.env.ref("sales_team.group_sale_salesman").id
        # ),
class Account(models.Model):
    _inherit = 'account.move'

    invoice_user_id = fields.Many2one('res.users', copy=False, tracking=True,
                                      string='Salesperson',
                                      default=lambda self: self.env.user)

class operation_type(models.Model):
    _inherit = 'product.operation.type'
    is_molnlycke = fields.Boolean()

class operations(models.Model):
    _inherit = 'operation.operation'
    patient_national_id_image = fields.Binary('Patient National ID image', store=True)
    patient_national_id_image_file_name = fields.Char('File Name')
    is_molnlycke = fields.Boolean(related='operation_type.is_molnlycke')
    def createOP(self, vals):
        # self.ensure_one()
        self.env['operation.operation'].create(vals)
        op = self.env['operation.operation'].search([], order="create_date desc", limit=1)
        # raise Warning(string(op.id))
        return op;

    def getOpComponent(self, operation_type):
        components = self.env['operation.operation'].search(
            [('operation_component', '=', True), ('operation_type', '=', operation_type)])
        return components
        pass
    def _compute_access_url(self):
        super(operations, self)._compute_access_url()
        for request in self:
            request.access_url = '/my/operation/%s' % (request.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (_('Operation'), self.name)
    def _notify_get_groups(self, msg_vals=None):
        """ Give access button to users and portal customer as portal is integrated
        in sale. Customer and portal group have probably no right to see
        the document so they don't have the access button. """
        groups = super(operations, self)._notify_get_groups(msg_vals=msg_vals)
        self.ensure_one()
        if self.state not in ('draft', 'cancel'):
            for group_name, group_method, group_data in groups:
                if group_name not in ('customer', 'portal'):
                    group_data['has_button_access'] = True

        return groups
    def preview_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }


class ResUser(models.Model):
    _inherit = 'res.users'

    operation_portal_access = fields.Boolean('Operation portal access')
