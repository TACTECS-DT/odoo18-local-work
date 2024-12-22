from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class GetProducts(models.TransientModel):
    _name = 'get.products.from.adv.inv.rep.wizard'

    report_type = fields.Selection(
        [('ABC', 'ABC'),
         ('FSN', 'FSN')],
        default='ABC',
        string="Report Type"
    )

    def set_products_in_inventory_count(self, product_ids):
        count = self.env['setu.stock.inventory.count'].browse(self.env.context.get('active_id', False))
        product_ids = self.env['product.product'].browse(product_ids)
        count.product_ids |= product_ids

    def get_products_from_setu_reports(self):
        product_ids = False
        if self.report_type == 'XYZ':
            product_ids = [val['product_id'] for val in self.get_inventory_xyz_analysis_report_data()]
        elif self.report_type == 'FSN':
            product_ids = [val['product_id'] for val in self.get_inventory_fsn_analysis_report_data()]
        elif self.report_type == 'ABC':
            product_ids = [val['product_id'] for val in self.get_abc_sales_analysis_report_data()]
        if product_ids:
            self.set_products_in_inventory_count(product_ids)
        else:
            raise ValidationError(_('No products found.'))
