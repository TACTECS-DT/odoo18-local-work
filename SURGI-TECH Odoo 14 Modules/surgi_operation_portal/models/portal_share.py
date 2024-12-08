from odoo import models ,fields,_,api
class CrmTeam(models.Model):
    _inherit = 'crm.team'
    member_ids = fields.One2many(
        'res.users', 'sale_team_id', string='Channel Members',
        check_company=True,domain=[],
        help="Add members to automatically assign their documents to this sales team. You can only be member of one team.")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user,domain=[])
    @api.depends('partner_id', 'date_order')
    def _compute_analytic_account_id(self):
        for order in self:
            if not order.analytic_account_id:
                default_analytic_account = order.env['account.analytic.default'].sudo().account_get(
                    partner_id=order.partner_id.id,
                    date=order.date_order,
                    company_id=order.company_id.id,
                )
                order.analytic_account_id = default_analytic_account.analytic_id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.user_id or False
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        user_id = partner_user.id
        values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)

