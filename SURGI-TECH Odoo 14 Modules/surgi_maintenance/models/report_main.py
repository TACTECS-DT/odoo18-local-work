from odoo import models, fields, api, exceptions, _

from datetime import datetime, timedelta

class maintenance_inform_form(models.Model):
    _name = 'maintenance.inform'

    client_res = fields.Many2one('res.partner', related="order_id.partner_id", string='العميل', store=True, )
    employee_id = fields.Many2one(related="order_id.user_id", string='موظف الشركة')
    contact_representative = fields.Many2one('contact.representative', string='المندوب', store=True,
                                             domain="[('contact_id', '=', client_res)]", )
    representative_mobile = fields.Char(string="التلفون", related='contact_representative.client_representative_mobile',
                                        store=True)
    pickup_date = fields.Date(string='تاريخ البلاغٍ')
    comments = fields.Text(string='ملاحظات')

    #################### location
    street1 = fields.Char(related='client_res.street', string='الشارع')
    street2 = fields.Char(related='client_res.street2', string='الشارع')
    city = fields.Char(related='client_res.city', string='المدينة')
    country_id = fields.Char(related='client_res.country_id.name', string='البلد')

    order_id = fields.Many2one('sale.order', store=True, string='رقم امر التوريد')
    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')
    picking_id = fields.Many2one('stock.picking', store=True, domain="[('sale_id', '=', order_id)]")
    product_forms = fields.One2many('stock.move.line', 'pickup_delivery_inform',
                                    related="picking_id.move_line_ids_without_package", domain=[()], string='المنتج',
                                    readonly=False)

    inform = fields.Boolean('إبلاغ')
    pickup_dvice = fields.Boolean('سحب جهاز')
    traine = fields.Boolean('تدريب')
    insure = fields.Boolean('دورية')
    installed = fields.Boolean('تسليم الجهاز')


    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("maintenance.inform.code")

    name = fields.Char(
        "الرقم المرجعي", readonly=True, index=True, store=True, default=_get_default_code
    )

    @api.onchange('client_res')
    def compute_display_name(self):
        self.contact_representative = ""

    def print_installation_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date
        }
        # docids = self.env['sale.order'].search([]).ids
        return self.env.ref('surgi_maintenance.report_maintenance_inform_card').report_action(None, data=data)


class maint_installation(models.AbstractModel):
    _name = 'report.maintenance.report_maintenance_inform_card'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['maintenance.inform'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'maintenance.inform',
            'docs': docs,
            'data': data,
            'get_something': self.get_something,
        }

    def get_something(self):
        return 5

