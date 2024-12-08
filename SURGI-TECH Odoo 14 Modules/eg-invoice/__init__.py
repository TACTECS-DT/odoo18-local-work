# -*- coding: utf-8 -*-

from . import controllers
from . import models
from .import wizard
from odoo import api, SUPERUSER_ID
from odoo.modules.module import get_module_resource
import requests,json,urllib

def _update_taxes(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    #text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'TaxTypes.json')
    text_file_path="https://sdk.preprod.invoicing.eta.gov.eg/files/TaxTypes.json"
    with urllib.request.urlopen(text_file_path) as json_file:#, encoding="utf8"
     data = json.load(json_file)
     for i in data:
        env['eg.tax'].create({'code':i['Code'],'desc_en':i['Desc_en'],'name':i['Desc_ar'],"nontaxble":0})
     #text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'NonTaxableTaxTypes.json')
     text_file_path="https://sdk.preprod.invoicing.eta.gov.eg/files/NonTaxableTaxTypes.json"
     with urllib.request.urlopen(text_file_path) as json_file:#, encoding="utf8"
         data = json.load(json_file)
         for i in data:
             env['eg.tax'].create({'code': i['Code'], 'desc_en': i['Desc_en'], 'name': i['Desc_ar'], "nontaxble": 1})
     #text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'TaxSubtypes.json')
     text_file_path="https://sdk.preprod.invoicing.eta.gov.eg/files/TaxSubtypes.json"
     with urllib.request.urlopen(text_file_path) as json_file:#, encoding="utf8"
         data = json.load(json_file)
         for i in data:
             tax=env['eg.tax'].search([("code","=",i['TaxtypeReference'])])
             for x in tax:
                env['eg.subtax'].create({'code': i['Code'], 'desc_en': i['Desc_en'], 'name': i['Desc_ar'], "taxrefrecnce":i["TaxtypeReference"],"tax":x.id})