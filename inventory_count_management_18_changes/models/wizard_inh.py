from odoo import models , fields , api ,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.exceptions import UserError as Warning
from odoo.tools.float_utils import float_compare, float_is_zero
import json
import logging
from odoo.exceptions import UserError, ValidationError



class WarningMSGWizard(models.TransientModel):
    _inherit = 'inventory.warning.message.wizard'

    def reject_count_lines(self):
        count_id = self.env['setu.stock.inventory.count'].browse(self.env.context.get('active_id', False))
        for line in count_id.line_ids:
            line.state = 'Reject'
        count_id.is_all_line_refused = True
        count_id.is_all_line_approved = False


        
    def approve_count_lines(self):
        count_id = self.env['setu.stock.inventory.count'].browse(self.env.context.get('active_id', False))
        for line in count_id.line_ids:
            line.state = 'Approve'
        count_id.is_all_line_approved = True
        count_id.is_all_line_refused = False

