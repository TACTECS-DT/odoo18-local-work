from odoo import models, fields, api, _


class ChatChannel(models.Model):
    _inherit = 'discuss.channel'

    ks_dashboard_board_id = fields.Many2one('ks_dashboard_ninja.board')
    ks_dashboard_item_id = fields.Many2one('ks_dashboard_ninja.item')

    def ks_chat_wizard_channel_id(self, **kwargs):
        item_id = kwargs.get('item_id')
        dashboard_id = kwargs.get('dashboard_id')
        item_name = kwargs.get('item_name')
        dashboard_name = kwargs.get('dashboard_name')

        channel = self.search([('ks_dashboard_item_id', '=', item_id)], limit=1)

        if not channel:
            users = self.env['res.users'].search([
                ('active', '=', True), ('groups_id', 'in', self.env.ref('base.group_user').id)]).mapped('partner_id.id')

            channel = self.sudo().create({
                'name': f"{dashboard_name} - {item_name}",
                'ks_dashboard_board_id': dashboard_id,
                'ks_dashboard_item_id': item_id,
                'channel_member_ids': [(0, 0, {'partner_id': partner_id}) for partner_id in users]
            })

        return channel.id if channel else None
