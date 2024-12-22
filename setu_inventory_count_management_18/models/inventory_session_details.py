from odoo import fields, models, api
import datetime
from datetime import datetime


class InvSessionDetails(models.Model):
    _name = 'inventory.session.details'
    _description = 'Inventory Session Details'

    session_id = fields.Many2one(
        comodel_name="setu.inventory.count.session",
        string="Session"
    )
    start_date = fields.Datetime(
        string="Start Date"
    )
    end_date = fields.Datetime(
        string="End Date"
    )
    duration = fields.Char(
        compute="_compute_duration",
        string="Duration"
    )
    duration_seconds = fields.Integer(
        compute="_compute_duration",
        string="Duration seconds"
    )

    def _compute_duration(self):
        for history in self:
            start_date = history.start_date
            # start_date = datetime.strptime(str(start_date)[0:19], '%Y-%m-%d %H:%M:%S')
            end_date = history.end_date
            if not history.end_date:
                end_date = datetime.now()
                # end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            difference = end_date - start_date
            history.duration = difference
            history.duration_seconds = int(difference.seconds)
