from odoo import fields, models, api, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    barcode = fields.Char(
        string="Barcode",
        copy=False
    )
    check_stock_barcode_installed = fields.Boolean(
        string="Module is Installed",
        compute="_check_stock_barcode_installed"
    )

    def _check_stock_barcode_installed(self):
        for rec in self:
            installed = self.env['ir.module.module'].sudo().search([('name', '=', 'stock_barcode'),
                                                                    ('state', '=', 'installed')], limit=1)
            if installed:
                rec.check_stock_barcode_installed = True
            else:
                rec.check_stock_barcode_installed = False
