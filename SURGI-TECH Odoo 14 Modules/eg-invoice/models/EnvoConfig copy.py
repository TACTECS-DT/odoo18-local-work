from audioop import reverse
import time

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError, Warning
from odoo.modules.module import get_module_resource
import requests
import json
import urllib
from datetime import datetime, timedelta, timezone
import pytz

#import odoo.exceptions.UserError
from pathlib import Path

from odoo.http import request
from dateutil import parser
import base64
import pytz


class EnvoConfig:
    # def __init__(self):
    #     print("VVVVVVVVV")
    #     pass

    def getissuerdata(self, company_id):
        if not (company_id.country_code and company_id.state_id.display_name and company_id.city and company_id.name and company_id.registration_id):
            raise Warning(
                "Please Check your company name , country ,city and registration id")
        var = """{
                "address": {
                    "branchID": "0",
                    "country": \""""+str(company_id.country_code)+"""\",
                    "governate": \""""+str(company_id.state_id.display_name)+"""\",
                    "regionCity": \""""+str(company_id.city)+"""\",
                    "street": \""""+str(company_id.street)+"""\",
                    "buildingNumber":\""""+str(company_id.building_no)+"""\",
                    "postalCode": \""""+str(company_id.zip)+"""\",
                    "floor": "",
                    "room": "",
                    "landmark": "",
                    "additionalInformation": ""
                },
                "type": "B",
                "id": \""""+str(company_id.registration_id)+"""\",
                "name": \""""+str(company_id.name)+"""\"
            }"""
        return var
        # return {
        #         "address": {
        #             "branchID": "0",
        #             "country": company_id.country_code,
        #             "governate": company_id.state_id.display_name,
        #             "regionCity": company_id.city,
        #             "street": company_id.street,
        #             "buildingNumber": "",
        #             "postalCode": company_id.zip,
        #             "floor": "",
        #             "room": "",
        #             "landmark": "",
        #             "additionalInformation": ""
        #         },
        #         "type": "B",#*
        #         "id": "674859545",#*
        #         "name": company_id.name
        #     }
        pass

    def getRecieverdata(self, partner_id):
        if partner_id.company_type == 'person':
            type = "p"
        else:
            type = "B"
        if not (partner_id.country_id.code and partner_id.state_id.display_name and partner_id.city and partner_id.name and partner_id.tax_reg_no):
            raise Warning(
                "Please Check Reciver  name , country ,city and registration id")

        val = """
        {
                "address": {
                    "country": \""""+str(partner_id.country_id.code)+"""\",
                    "governate": \""""+str(partner_id.state_id.display_name)+"""\",
                    "regionCity": \""""+str(partner_id.city)+"""\",
                    "street": \""""+str(partner_id.street)+"""\",
                    "buildingNumber": \""""+str(partner_id.building_no)+"""\",
                    "postalCode": \""""+str(partner_id.company_id.zip)+"""\",
                    "floor": "",
                    "room": "",
                    "landmark": "",
                    "additionalInformation": ""
                },
                "type": \""""+str(type)+"""\",
                "id": \""""+str(partner_id.tax_reg_no)+"""\",
                "name": \""""+str(partner_id.name)+"""\"
            }
        """
        return val
        # return {
        #     "address": {
        #         "country": partner_id.country_id.code,
        #         "governate": partner_id.state_id.display_name,
        #         "regionCity": partner_id.city,
        #         "street": partner_id.street,
        #         "buildingNumber": "",
        #         "postalCode": partner_id.company_id.zip,
        #         "floor": "",
        #         "room": "",
        #         "landmark": "",
        #         "additionalInformation": ""
        #     },
        #     "type": "B",
        #     "id": "313717919",
        #     "name": partner_id.name
        # }
        pass

    def getLineTaxes(self, line):
        taxes = line.tax_ids
        vals = ""
        for tax in taxes:
            if not (tax.eg_tax_type.code and tax.eg_tax_subtype.code and tax.amount):
                raise Warning(
                    "Please Check Tax types and Sub Types of "+str(tax.name))
            vals = """
                    {
                                        "taxType": \""""+str(tax.eg_tax_type.code)+"""\",
                                        "amount": """+str(line.totaltaxperline)+""",
                                        "subType":\""""+str(tax.eg_tax_subtype.code)+"""\",
                                        "rate": """+str(tax.amount)+"""
                                    }
                    """
            if tax.id != taxes[-1].id:
                vals += ""","""

        return vals

    def getInvoiceLinesold(self, lines):
        invoicelines = "["
        # for line in lines:
        # sales total = Total amount for the invoice line considering quantity and unit price in EGP (with excluded factory amounts if they are present for specific types in documents).
        # total => Total amount for the invoice line after adding all pricing items, taxes, removing discounts.
        # valueDifference=>Value difference when selling goods already taxed (accepts +/- numbers), e.g., factory value based
        # totalTaxableFees => Total amount of additional taxable fees to be used in final tax calculation.
        # netTotal => Total amount for the invoice line after applying discount.
# line.itemsDiscount
        err = ""
        for line in lines:

            if not (line.itemType and line.itemCode and line.unitamountEGP):
                err = "Please check Einvoice Data for item " + \
                    str(line.description)+" \n"

            invoicelines += """
            {
                    "description": \""""+str(line.eg_tax_desc)+"""\",
                    "itemType": \""""+str(line.itemType)+"""\",
                    "itemCode": \""""+str(line.itemCode)+"""\",
                    "unitType": "EA",
                    "quantity":"""+str(line.quantitiy)+""",
                    "internalCode": "",
                    "salesTotal":"""+str(line.salestotal)+""",
                    "total": """+str(line.total)+""",
                    "valueDifference": 0.00,
                    "totalTaxableFees":"""+str(line.totaltaxablefees)+""",
                    "netTotal": """+str(line.nettotal)+""",
                    "itemsDiscount":0.0,
                    "unitValue": {
                        "currencySold": \"EGP\",
                        "amountEGP": """+str(line.unitamountEGP)+"""
                    },
                    "discount": {
                        "rate": """+str(line.discount_rate)+""",
                        "amount": """+str(line.itemsDiscount)+"""
                    },
                    "taxableItems": [
                        """+self.getLineTaxes(line)+"""
                        ]
                   
                }
            """
            if not line.id == lines[-1].id:
                invoicelines += ","
            # ,
            # "discount": {
            #     "rate": 0,
            #     "amount": 0
            # },
            # "taxableItems": [
            #     {
            #         "taxType": "T1",
            #         "amount": 0,
            #         "subType": "V001",
            #         "rate": 0
            #     }
            # ]
        invoicelines += "]"
        if err != "":
            raise Warning(err)
        return invoicelines
        pass

    def getInvoiceLines(self, lines):
        invoicelines = "["
        # for line in lines:
        # sales total = Total amount for the invoice line considering quantity and unit price in EGP (with excluded factory amounts if they are present for specific types in documents).
        # total => Total amount for the invoice line after adding all pricing items, taxes, removing discounts.
        # valueDifference=>Value difference when selling goods already taxed (accepts +/- numbers), e.g., factory value based
        # totalTaxableFees => Total amount of additional taxable fees to be used in final tax calculation.
        # netTotal => Total amount for the invoice line after applying discount.
# line.itemsDiscount
        err = ""
        for line in lines:

            if not (line.itemType and line.itemCode and line.unitamountEGP):
                err = "Please check Einvoice Data for item " + \
                    str(line.description)+" \n"

            invoicelines += """
            {
                    "description": \""""+str(line.eg_tax_desc)+"""\",
                    "itemType": \""""+str(line.itemType)+"""\",
                    "itemCode": \""""+str(line.itemCode)+"""\",
                    "unitType": "EA",
                    "quantity":"""+str(line.quantitiy)+""",
                    "internalCode": "",
                    "salesTotal":"""+str(line.salestotal)+""",
                    "total": """+str(line.total)+""",
                    "valueDifference": 0.00,
                    "totalTaxableFees":"""+str(line.totaltaxablefees)+""",
                    "netTotal": """+str(line.nettotal)+""",
                    "itemsDiscount":0.0,
                    "unitValue": {
                        "currencySold": \"EGP\",
                        "amountEGP": """+str(line.unitamountEGP)+"""
                    },
                    "discount": {
                        "rate": """+str(line.discount_rate)+""",
                        "amount": """+str(line.itemsDiscount)+"""
                    },
                    "taxableItems": [
                        """+self.getLineTaxes(line)+"""
                        ]
                   
                }
            """
            if not line.id == lines[-1].id:
                invoicelines += ","
            # ,
            # "discount": {
            #     "rate": 0,
            #     "amount": 0
            # },
            # "taxableItems": [
            #     {
            #         "taxType": "T1",
            #         "amount": 0,
            #         "subType": "V001",
            #         "rate": 0
            #     }
            # ]
        invoicelines += "]"
        if err != "":
            raise Warning(err)
        return invoicelines
        pass

    def getPrintInvoiceLine(self, lines):
        invoicelines = "["
        err = ""
        lastline = ""
        for x in reversed(lines):
            if x.product_id:
                lastline = x.id
                break

        for line in lines:
            if line.product_id:
                if not (line.product_id.eg_tax_barcode_type and line.product_id.eg_tax_barcode and line.product_id.eg_tax_unittype):
                    err = "Please check Einvoice Data for item " + \
                        str(line.description)+" \n"

                invoicelines += """
                {
                        "description": \""""+str(line.description)+"""\",
                        "itemType": \""""+str(line.product_id.eg_tax_barcode_type)+"""\",
                        "itemCode": \""""+str(line.product_id.eg_tax_barcode)+"""\",
                        "unitType": "EA",
                        "quantity":"""+str(line.uquantity)+""",
                        "internalCode": "",
                        "salesTotal":"""+str(line.total)+""",
                        "total": """+str(line.total)+""",
                        "valueDifference": 0.00,
                        "totalTaxableFees":"""+str(0)+""",
                        "netTotal": """+str(line.total)+""",
                        "itemsDiscount":0.0,
                        "unitValue": {
                            "currencySold": \"EGP\",
                            "amountEGP": """+str(line.uprice)+"""
                        },
                        "discount": {
                            "rate": """+str(0)+""",
                            "amount": """+str(0)+"""
                        },
                        "taxableItems": [
                             """+self.getLineTaxes(line)+"""
                            ]
                    
                    }
                """
                # """+self.getLineTaxes(line)+"""
                if line.id != lastline:
                    invoicelines += ","

        invoicelines += "]"
        if err != "":
            raise Warning(err)
        return invoicelines

    def CreateInvoice(self, move):
        issuer = self.getissuerdata(move.company_id)
        reciever = self.getRecieverdata(move.partner_id)
        token = Connection._access_token
        # "documentTypeVersion": \""""+str(move.documentversion)+"""\",
        dt1 = datetime.now(tz=pytz.UTC)
        dt = dt1.strftime("%Y-%m-%dT%H:%M:%SZ")

        if move.einvoice_itemstype == "items":

            val = """
                    
                {
                "issuer":""" + str(issuer) + """,
                "receiver":""" + str(reciever) + """,
                "documentType": \"""" + str(move.documenttype) + """\",
                "documentTypeVersion": \"""" + str(Connection.tax_v) + """\",
                    "dateTimeIssued": \"""" + str(dt) + """\",
                    "taxpayerActivityCode": "4620",
                "internalID": \"""" + str(move.name) + """\",
                "invoiceLines": """ + self.getInvoiceLines(move.eg_tax_lines) + """,
                "totalDiscountAmount": """ + str(move.eg_tax_totalDiscountAmount) + """ ,
                    "totalSalesAmount": """ + str(move.eg_tax_totalSalesAmount) + """,
                    "netAmount": """ + str(move.eg_tax_netamount) + """,
                    "taxTotals": [
                        {
                            "taxType": "T1",
                            "amount":  """ + str(move.eg_tax_taxtotal) + """
                        }
                    ],
                    "totalAmount": """ + str(move.eg_tax_totalAmount) + """,
                    "extraDiscountAmount": 0,
                    "totalItemsDiscountAmount": 0.0,
                    "signatures": [
                        {
                            "signatureType": "I",
                            "value": \"""" + str(token) + """\"
                        }
                    ]




                }
                    
                """
        else:

            val = """
                    
                    {
                    "issuer":""" + str(issuer) + """,
                    "receiver":""" + str(reciever) + """,
                    "documentType": \"""" + str(move.documenttype) + """\",
                    "documentTypeVersion": \"""" + str(Connection.tax_v) + """\",
                    "dateTimeIssued": \"""" + str(dt) + """\",
                    "taxpayerActivityCode": "4620",
                    "internalID": \"""" + str(move.name) + """\",
                    "invoiceLines": """ + self.getPrintInvoiceLine(move.printinvoicetoline) + """,
                    "totalDiscountAmount": """ + str(0) + """ ,
                        "totalSalesAmount": """ + str(sum(line.total for line in move.printinvoicetoline)) + """,
                        "netAmount": """ + str(sum(line.total for line in move.printinvoicetoline)) + """,
                        "taxTotals": [
                            
                        ],
                        "totalAmount": """ + str(str(sum(line.total for line in move.printinvoicetoline))) + """,
                        "extraDiscountAmount": 0,
                        "totalItemsDiscountAmount": 0.0,
                        "signatures": [
                            {
                                "signatureType": "I",
                                "value": \"""" + str(token) + """\"
                            }
                        ]




                    }
                    
                    """

        return val

    def CreateDocument(self, moves):
        val = """
                   {
                            "documents": [
                      """
        for move in moves:
            val += self.CreateInvoice(move)
            if move.id != moves[-1].id:
                val += ""","""
        val += """
                ]
                }

                """
        return val
        pass

    def getdocuments(self):
        moves = self.env['account.move'].search(
            [("eg_tax_status", "=", "Sent")])
        docs = {
            "no": len(moves)
        }

        for move in moves:
            documents = {"documents": [self.CreateDocument(move)]}

        docs["documents":documents]
        return docs

    def DocumentSubmissions(self, move):
        con = Connection(move.company_id)
        # Connection.getToken()
        x = Connection
        token = Connection._access_token
        documents = {"documents": [self.CreateDocument(move)]}
        #con =Connection(Connection._access_token,Connection._expire_in,Connection._token_type,Connection._scope)
        # con=Connection()

        #vals = json.dumps(documents)
        vals = self.CreateDocument(move)
        # vals=vals.replace("\n","")
        headers = {"Authorization": Connection._token_type+" "+con.getToken(),
                   "Content-Type": "application/json"}

        response = requests.post(
            con.apiBaseUrl + "/api/v1/documentsubmissions", data=vals.encode('utf-8'), headers=headers)
        res = json.loads(response.text)
        #raise UserError(str(response))
        if res['acceptedDocuments']:
            print("f")
            move.submissionId = res['submissionId']
            move.egtax_uuid = res['acceptedDocuments'][0]['uuid']
            move.egtax_longid = res['acceptedDocuments'][0]['longId']
            time.sleep(2)
            documentdata = self.getDocumentStatus(
                res['acceptedDocuments'][0]['uuid'], move.company_id)
            move.egtax_status = documentdata['status']
            move.egtax_link = documentdata['url']
            move.hashkey = res['acceptedDocuments'][0]['hashKey']

        err = ""
        if res['rejectedDocuments']:
            for i in res['rejectedDocuments']:
                err += str(i['internalId']) + " Have Errors : \n "
                for x in i['error']['details']:
                    err += str(x['message']) + " " + \
                        str(x['propertyPath']) + "\n"
            err += "*******************************"
            raise Warning(err)
            print("response 202")
        if response.status_code == 400:
            raise UserError(response.text)
        elif response.status_code == 202:
            # v=json.loads(response.text)
            error202 = json.loads(response.text)

        elif response.status_code == 200:
            res = response.json()
            print(response)
        pass

    def CancelDocument(self, document, reason, company_id):
        con = Connection(company_id)
        token = Connection._access_token
        url = "https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/state/"+document+"/state"

        payload = json.dumps({
            "status": "cancelled",
            "reason": str(reason)
        })
        headers = {"Authorization": Connection._token_type + " " + con.getToken(),
                   "Content-Type": "application/json"}
        res = con.SendPutRequest(url=url, headers=headers, data=payload)
        if res.status_code == 200:
            return True
        elif res.status_code == 400:
            response = json.loads(res.text)
            err = ""
            for i in response['error']['details']:
                err += str(i['message'])+"\n"
            raise UserError(err)
            return False

    def getDocumentDetail(self, company_id, uuid):
        url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/"+uuid+"/details"
        payload = {}
        con = Connection(company_id)
        res = con.sendGetRequest(url=url, data=payload)
        response = json.loads(res.text)
        if res.status_code == 404:

            raise UserError("this invoice not registered")
        if res.status_code == 200 and response['status'] in ('invalid', 'rejected', 'cancelled'):
            raise UserError("this Document Status already "+str(res.status))

    def getPrintedVersion(self, uuid, company_id):
        con = Connection(company_id)

        url = con.apiBaseUrl+"/api/v1/documents/"+str(uuid)+"/pdf"

        payload = {}

        #url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/:documentUUID/details"

        response = requests.get(url, headers=Connection._header, data=payload)
        return response.text
        pdf = base64.b64decode(response.text or '')
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename="Invoice.pdf"'),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
        # return response.txt

    def getDocumentStatus(self, uuid, company_id):
        con = Connection(company_id)

        url = con.apiBaseUrl+"/api/v1/documents/"+str(uuid)+"/details"

        payload = {}

        #url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/:documentUUID/details"

        response = requests.get(url, headers=Connection._header, data=payload)
        if response.status_code == 200:
            res = json.loads(response.text)
            x = {"status": res['status'], "url": res['publicUrl'], 'res': res}
            return x

        else:
            x = {"status": '', "url": ''}
            return x
            #raise UserError("We Cant get this Document Status")
            print("x")

    def getlivedocuments(self, company_id, page=1):
        con = Connection(company_id)
        user_tz = (self.env.user.tz or pytz.utc)
        local = pytz.timezone(user_tz)
        payload = {}
        url = con.apiBaseUrl + "/api/v1.0/documents/recent"
        head = Connection._header
        response = requests.get(url, headers=head, data=payload)
        if response.status_code == 200:
            res = json.loads(response.text)
            data = res['result']
            return data  # json.dumps(data)

    def getRecentDocuments(self, company_id):
        con = Connection(company_id)
        user_tz = (self.env.user.tz or pytz.utc)
        local = pytz.timezone(user_tz)

        url = con.apiBaseUrl + "/api/v1.0/documents/recent"

        payload = {}
        lastinserted = self.env['egytax.getdocuments'].search(
            [], order='create_date desc', limit=1)
        # url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/:documentUUID/details"
        lastuuid = lastinserted.uuid
        if lastuuid:
            lastuuid = lastuuid
        else:
            lastuuid = "z"
        head = Connection._header
        head['PageSize'] = '10'
        head['PageNo'] = '1'
        documents = []
        pages = 1
        response = requests.get(url, headers=head, data=payload)
        if response.status_code == 200:
            res = json.loads(response.text)
            pages = res['metadata']['totalPages']
            abort = -1
            for i in range(0, pages):
                if abort == 1:
                    return documents
                head = Connection._header
                head['PageSize'] = "10"
                head['PageNo'] = "'"+str(i)+"'"
                responsepages = requests.get(url, headers=head, data=payload)
                res = json.loads(responsepages.text)
                data = res['result']
                for x in data:

                    if x['uuid'] == lastuuid:
                        abort = 1
                        break
                    else:
                        a = parser.parse(x['dateTimeIssued']
                                         ).replace(tzinfo=None)
                        if x['dateTimeIssued']:
                            # .astimezone(local)#datetime.strptime(x['dateTimeIssued'],'%Y-%m-%dT%H:%M:%SZ' )#pytz.UTC.localize(datetime.strptime(x['dateTimeIssued'],'%Y-%m-%dT%H:%M:%S%z' )).astimezone(local)
                            x['dateTimeIssued'] = parser.parse(
                                x['dateTimeIssued']).replace(tzinfo=None)
                        if x['dateTimeReceived']:
                            # .astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)
                            x['dateTimeReceived'] = parser.parse(
                                x['dateTimeReceived']).replace(tzinfo=None)
                        if x['cancelRequestDate']:
                            x['cancelRequestDate'] = parser.parse(x['cancelRequestDate']).replace(
                                tzinfo=None)  # .astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)x['dateTimeReceived'] =parser.parse(x['dateTimeReceived']).replace(tzinfo=None)#.astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)
                        if x['rejectRequestDate']:
                            x['rejectRequestDate'] = parser.parse(x['rejectRequestDate']).replace(
                                tzinfo=None)  # .astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)
                        if x['cancelRequestDelayedDate']:
                            x['cancelRequestDelayedDate'] = parser.parse(x['cancelRequestDelayedDate']).replace(
                                tzinfo=None)  # .astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)
                        if x['rejectRequestDelayedDate']:
                            x['rejectRequestDelayedDate'] = parser.parse(x['rejectRequestDelayedDate']).replace(
                                tzinfo=None)  # .astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)
                        if x['declineCancelRequestDate']:
                            x['declineCancelRequestDate'] = parser.parse(x['declineCancelRequestDate']).replace(
                                tzinfo=None)  # .astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)
                        if x['declineRejectRequestDate']:
                            x['declineRejectRequestDate'] = parser.parse(x['declineRejectRequestDate']).replace(
                                tzinfo=None)  # .astimezone(local)#datetime.strptime(x['dateTimeReceived'], '%Y-%m-%dT%H:%M:%S.%fZ')#pytz.UTC.localize(x['dateTimeReceived']).astimezone(local)

                        documents.append(x)

           # x= {"status":res['status'],"url":res['publicUrl'],'res':res}
        return documents

    pass


class Connection:
    def __init__(self, company):
        if company.pre_egtax_default:  # production
            Connection.clientId = company.pro_egtax_clientid
            Connection.tax_v = company.pro_egtax_v
            Connection.clientSecret = company.pro_egtax_clientsecret1
            self.getToken()
        else:
            Connection.clientId = company.pre_egtax_clientid
            Connection.tax_v = company.pre_egtax_v
            Connection.clientSecret = company.pre_egtax_clientsecret1
            self.apiBaseUrl = "https://api.preprod.invoicing.eta.gov.eg"
            self.idSrvBaseUrl = "https://id.preprod.eta.gov.eg"
            self.apiBaseUrl = "https://api.preprod.invoicing.eta.gov.eg"
            self.getToken()
            Connection._header = {"Authorization": Connection._token_type + " " + Connection._access_token,
                                  "Content-Type": "application/json"}

    # clientId = "8078ab5f-a208-41c3-b8a2-b6620b4adbad"
    # clientSecret = "45b2804f-220b-4594-b3b8-26fde38bd215"
    #
    tax_v = ""
    _access_token = None
    _expire_in = None
    _expire_date = datetime(year=1990, month=2, day=1, minute=00, second=00)
    _token_type = None
    _scope = None
    _header = ""

    # def __init__(self,access_token,expire_in,token_type,scope):
    #     self.scope=scope
    #     self.access_token=access_token
    #     self.expire_in=expire_in
    #     self.token_type=token_type

    @staticmethod
    def _check_token_state():

        if Connection._expire_in and Connection._expire_date > datetime.now():
            return True
        else:
            return False
    # @staticmethod

    def getToken(self):

        if Connection._check_token_state():
            return Connection._access_token
        else:
            vals = {
                'grant_type': "client_credentials",
                'client_id': self.clientId,
                'client_secret': self.clientSecret,
                'scope': 'InvoicingAPI'

            }
            response = requests.post(
                self.idSrvBaseUrl + "/connect/token", data=vals)
            if response.status_code == 200:
                res = response.json()
                Connection._access_token = res['access_token']
                Connection._expire_in = res['expires_in']
                Connection._scope = res['scope']
                Connection._expire_date = datetime.now()+timedelta(seconds=Connection._expire_in)
                Connection._token_type = res['token_type']
                # return Connection._access_token
            else:
                raise UserError("Connection Error => " +
                                str(response.status_code))

    #headers = {"Authorization": _token_type +" " +getToken(), "Content-Type": "application/json"}
    def sendRequest(self, urlParams, vals):
        response = requests.post(self.idSrvBaseUrl + ""+urlParams, data=vals)
        if response.status_code == 200:
            res = response.json()
            return res
        elif response.status_code == 202:
            print("res=response.json()")
        elif response.error:
            raise UserError(response.error)
        else:
            raise UserError("Connection Error => " + str(response.status_code))

    def sendGetRequest(self, url, data):
        response = requests.request(
            "GET", url, headers=self._header, data=data)
        return response

    def SendPutRequest(self, url, headers, data):
        response = requests.request(
            "PUT", url, headers=self._header, data=data)
        return response

    pass


class Segnelton:
    @staticmethod
    def getActivities():
        #text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'ActivityCodes.json')
        text_file_path = "https://sdk.preprod.invoicing.eta.gov.eg/files/ActivityCodes.json"
        codes = []
        # , encoding="utf8"
        with urllib.request.urlopen(text_file_path) as json_file:
            data = json.load(json_file)
            for i in data:
                codes.append((i['code'], i['Desc_ar']))
            return codes

    @staticmethod
    def getMeasureUnit():
        #text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'UnitTypes.json')
        text_file_path = "https://sdk.preprod.invoicing.eta.gov.eg/files/UnitTypes.json"
        codes = []
        # , encoding="utf8"
        with urllib.request.urlopen(text_file_path) as json_file:
            data = json.load(json_file)
            for i in data:
                codes.append((i['code'], i['desc_en']))

        return codes
    # @staticmethod
    # def get_currency():
    #     text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'UnitTypes.json')
    #     text_file_path=""
    #     codes = []
    #     with open(text_file_path, encoding="utf8") as json_file:
    #         data = json.load(json_file)
    #         for i in data:
    #             codes.append((i['code'], i['desc_en']))
    #
    #     return codes
    # @staticmethod
    # def get_tax_type():
    #     text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'UnitTypes.json')
    #     codes = []
    #     with open(text_file_path, encoding="utf8") as json_file:
    #         data = json.load(json_file)
    #         for i in data:
    #             codes.append((i['code'], i['desc_en']))
    #     return codes
    # @staticmethod
    # def get_tax_subtype():
    #     text_file_path = get_module_resource('eg-invoice', 'static\\src\\', 'UnitTypes.json')
    #     codes = []
    #     with open(text_file_path, encoding="utf8") as json_file:
    #         data = json.load(json_file)
    #         for i in data:
    #             codes.append((i['code'], i['desc_en']))
    #     return codes
    #
