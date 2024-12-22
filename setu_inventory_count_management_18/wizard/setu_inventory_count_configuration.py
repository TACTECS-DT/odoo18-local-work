from odoo import fields, models, api, tools
import os
from odoo.modules.module import get_module_resource
import base64
import logging
_logger = logging.getLogger(__name__)


class SetuInventoryCountConfiguration(models.TransientModel):
    _name = 'setu.inventory.count.configuration'
    _description = 'Setu Inventory Count Configuration'

    install_setu_inventory_count_extended = fields.Boolean(string="Enable ABC/FSN Classification")

    @api.model
    def default_get(self, fields):
        res = super(SetuInventoryCountConfiguration, self).default_get(fields)
        install_setu_inventory_count_extended = self.env['ir.config_parameter'].sudo().get_param(
            'setu_inventory_count_management_18.extended_ic_module_in_registry')
        if install_setu_inventory_count_extended:
            res['install_setu_inventory_count_extended'] = True if install_setu_inventory_count_extended == 'installed' else False
        return res

    def execute(self):
        install_setu_inventory_count = self.env['ir.config_parameter'].sudo().get_param('setu_inventory_count_management_18.extended_ic_module_in_registry')
        self.unzip_and_install_extended_module(True, install_setu_inventory_count)
        self.env['ir.config_parameter'].set_param('setu_inventory_count_management_18.extended_ic_module_in_registry', True)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def unzip_and_install_extended_module(self, state, install_setu_inventory_count):
        try:
            extended_inventory_count = self.env['ir.module.module'].sudo().search(
                [('name', '=', 'setu_inventory_count_extended')],
                limit=1)
            status = ''
            source_dir = __file__.replace('/wizard/setu_inventory_count_configuration.py',
                                          '/module/setu_inventory_count_extended.zip')
            target_dir = __file__.split('/setu_inventory_count_management_18/wizard/setu_inventory_count_configuration.py')[0]
            if not state and extended_inventory_count and extended_inventory_count.state == 'installed':
                status = 'uninstall'
            if state:
                if extended_inventory_count and extended_inventory_count.state != 'installed':
                    status = 'install'
                elif not extended_inventory_count:
                    import zipfile
                    with zipfile.ZipFile(source_dir, 'r') as zip_ref:
                        zip_ref.extractall(target_dir)
                    self.env['ir.module.module'].sudo().update_list_setu_inventory_count_management_18()
            return True
        except Exception as e:
            _logger.info("====================%s==================" % e)
            return False
