# -*- coding: utf-8 -*-


import base64
import datetime
import io
import re
import requests
import PyPDF2

from PIL import Image
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import Warning, UserError, AccessError
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for


class SlidePartner(models.Model):
    _inherit = 'slide.slide.partner'
    completed = fields.Boolean('Is Completed', defaul=False)
    slide_type = fields.Selection([
        ('infographic', 'Infographic'),
        ('webpage', 'Web Page'),
        ('presentation', 'Presentation'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('quiz', "Quiz")],
        string='Type',  default='document',
        related='slide_id.slide_type',
        )


class ResPartner(models.Model):
    _inherit = 'res.partner'

    slide_slide_partner_ids = fields.One2many(
        comodel_name='slide.slide.partner',
        inverse_name='partner_id',
        string='Student Data',
        required=False)

    slide_channel = fields.Many2many(
        comodel_name='slide.channel',
        string='Channel', compute='_compute_slide_channel')

    def _compute_slide_channel(self):
        self.slide_channel = self.env['slide.slide.partner'].search([('partner_id', '=', self.id)]).channel_id.ids


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    slide_partner_ids_stadistic = fields.Many2many('slide.slide.partner', string='Student Data',compute='_compute_slide_partner_ids')
    completed_partner = fields.Boolean('Completed', compute='_compute_partner_statistics', compute_sudo=False)
    completion_partner = fields.Integer('Progress (%)', compute='_compute_partner_statistics', compute_sudo=False)

    def _compute_slide_partner_ids(self):
        active_ids = self.env.context.get('default_slide_partner_ids', [])
        ids=[]
        for id in active_ids:
            ids.append(id[1])
        if active_ids:
            self.slide_partner_ids_stadistic=self.env['slide.slide.partner'].sudo().search([('id', 'in',ids),('channel_id','=',self.id)])
        else:
            self.slide_partner_ids_stadistic=False


    @api.depends('slide_partner_ids', 'total_slides')
    def _compute_partner_statistics(self):
        active_ids = self.env.context.get('default_partner_id', [])

        if active_ids:
            current_user_info = self.env['slide.channel.partner'].sudo().search(
                [('channel_id', 'in', self.ids), ('partner_id', 'in', active_ids)]
            )
            mapped_data = dict((info.channel_id.id, (info.completed, info.completion)) for info in current_user_info)
            for record in self:
                completed, completion = mapped_data.get(record.id, (False, 0))
                record.completed_partner = completed
                record.completion_partner = round(100.0 * completion / (record.total_slides or 1))


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'
    completion_partner = fields.Integer('Progress (%)', compute='_compute_partner_statistics', compute_sudo=False)

    @api.depends('channel_id', 'partner_id')
    def _compute_partner_statistics(self):
        for record in self:
            record.completion_partner = round(100.0 * record.completion / (record.channel_id.total_slides or 1))