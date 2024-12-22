# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # module_setu_inventory_count_extended = fields.Boolean(
    #     string="Install ABC/FSN Classification"
    # )
    # extended_ic_module_in_registry = fields.Boolean(
    #     string="Extended Module in Registry",
    #     default=False,
    #     config_parameter="setu_inventory_count_management_18.extended_ic_module_in_registry"
    # )
    auto_inventory_adjustment = fields.Boolean(string="Auto Inventory Adjustment?",
                                               config_parameter="setu_inventory_count_management_18.auto_inventory_adjustment")

    # def open_actions_setu_inventory_count_configuration(self):
    #     action_values = self.sudo().sudo().env.ref('setu_inventory_count_management_18.actions_setu_inventory_count_configuration').sudo().read()[0]
    #     return action_values
    #
    # def execute(self):
    #     res = super(ResConfigSettings, self).execute()
    #     return res
