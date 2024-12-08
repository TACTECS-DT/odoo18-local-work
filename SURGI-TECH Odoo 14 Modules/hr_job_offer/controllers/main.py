# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug

import odoo.http as http

from odoo.http import request
from odoo.tools.misc import get_lang


class OfferController(http.Controller):

    # YTI Note: Keep id and kwargs only for retrocompatibility purpose
    @http.route('/offer/accept',type='http', auth='public', website=True, sitemap=False)
    def accept_offer(self, id, **kwargs):
        offer = request.env['hr.job.offer'].sudo().search([
            ('id', '=', id),
            ('state', '!=', 'accepted')])
        offer.do_accept()
        return request.redirect('/my/home')

    @http.route('/offer/refuse', type='http', auth='public', website=True, sitemap=False)
    def refuse_offer(self, id, **kwargs):
        offer = request.env['hr.job.offer'].sudo().search([
            ('id', '=', id),
            ('state', '!=', 'refused')])
        offer.do_refuse()
        return request.redirect('/my/home')
