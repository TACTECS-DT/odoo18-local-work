from odoo import fields, models, api


class POSConfig(models.Model):
    _inherit = 'pos.config'

    device_config_id = fields.Many2one('pos.device.config', 'POS Device Configuration')
    dont_send_e_receipt = fields.Boolean('Dont Send E-Receipt Auto')

