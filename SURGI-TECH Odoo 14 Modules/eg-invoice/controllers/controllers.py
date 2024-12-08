# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from .. import models as mod
import requests,json

class Eg_invoice(http.Controller):
    @http.route('/ping', auth='public',csrf=False)
    def index(self, **kw):
        return kw['rin']
    @http.route('/eg-invoice/ping/', auth='public',csrf=False)
    def index(self, **kw):
        return kw['rin']

    @http.route('/eg-invoice/getunsignedinvoice/', auth='public')
    def list(self, **kw):
        invo=mod.EnvoConfig
        docs=invo.getdocuments

        return (docs)
        # return http.request.render('eg-invoice.listing', {
        #     'root': '/eg-invoice/eg-invoice',
        #     'objects': http.request.env['eg-invoice.eg-invoice'].search([]),
        # })

    @http.route('/eg-invoice/eg-invoice/get_printout', type='http', auth='public')
    def object(self, companyid,uuid, **kw):
        comp=companyid
        #Model = request.registry["res.company"]
        Model = request.registry["res.company"].search([('id','=',companyid)])

        con = mod.EnvoConfig.Connection(companyid)

        url = con.apiBaseUrl + "/api/v1/documents/" + str(uuid) + "/pdf"

        payload = {}

        # url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/:documentUUID/details"

        response = requests.get(url, headers=Connection._header, data=payload)
        return http.request.render('eg-invoice.object', {
            'object': obj
        })
