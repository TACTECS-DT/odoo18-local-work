from datetime import datetime, timedelta
import requests
import json
import pprint
import logging
import psycopg2
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

ETA_URLS = {
    'access_token_pre': 'https://id.preprod.eta.gov.eg/connect/token',
    'access_token_pro': 'https://id.eta.gov.eg/connect/token',
    'submit_receipt_pre': 'https://api.preprod.invoicing.eta.gov.eg/api/v1/receiptsubmissions',
    'submit_receipt_pro': 'https://api.invoicing.eta.gov.eg/api/v1/receiptsubmissions'
}

class ModelName(models.Model):
    _inherit = 'pos.order.line'
    
    is_total_cost_computed = fields.Boolean('TCC')
    total_cost = fields.Monetary('')
    margin = fields.Monetary('')
    margin_percent = fields.Monetary('')
    refunded_qty = fields.Monetary('')
    refund_orderline_ids = fields.One2many('pos.order.line', 'refunded_orderline_id', 'Refund Order Lines', help='Orderlines in this field are the lines that refunded this orderline.')
    refunded_orderline_id = fields.Many2one('pos.order.line', 'Refunded Order Line', help='If this orderline is a refund, then the refunded orderline is specified in this field.')
    
    @api.depends('refund_orderline_ids')
    def _compute_refund_qty(self):
        for orderline in self:
            orderline.refunded_qty = -sum(orderline.mapped('refund_orderline_ids.qty'))


class ModelName(models.Model):
    _inherit = 'pos.order'

    eta_uuid = fields.Char('ETA UUID', copy=False, index=True)
    eta_submit_state = fields.Selection([('unsent', _('Unsent')),
                                         ('sent', _('Sent'))], default='unsent', copy=False)
    eta_status = fields.Selection([('invalid', 'Invalid'),
                                   ('valid', 'Valid')], copy=False)
    invalid_reason = fields.Text('Validation Error')
    margin = fields.Monetary('')
    margin_percent = fields.Monetary('')
    is_total_cost_computed = fields.Boolean('TCC')
    is_refunded = fields.Boolean(compute='_compute_refund_related_fields')
    refund_orders_count = fields.Integer('Number of Refund Orders', compute='_compute_refund_related_fields')
    refunded_order_ids = fields.Many2many('pos.order', compute='_compute_refund_related_fields')
    refunded_order_ids = fields.Many2many('pos.order', compute='_compute_refund_related_fields') 
    refunded_orders_count = fields.Integer(compute='_compute_refund_related_fields')
   
    
    @api.depends('lines.refund_orderline_ids', 'lines.refunded_orderline_id')
    def _compute_refund_related_fields(self):
        for order in self:
            order.refund_orders_count = len(order.mapped('lines.refund_orderline_ids.order_id'))
            order.is_refunded = order.refund_orders_count > 0
            order.refunded_order_ids = order.mapped('lines.refunded_orderline_id.order_id')
            order.refunded_orders_count = len(order.refunded_order_ids)

    def _prepare_header_info(self):
        date_string = self.date_order.strftime('%Y-%m-%dT%H:%M:%SZ')
        company_currency_id = self.company_id.currency_id
        currency_id = self.currency_id
        header = {
            "dateTimeIssued": date_string,
            "receiptNumber": self.pos_reference,
            "uuid": "",
            "previousUUID": self._get_previous_order(),
        }

        if self.amount_total < 0.0:
            referenceUUID = False
            if self.refunded_order_ids:
                referenceUUID = self.refunded_order_ids.filtered(lambda r: r.eta_uuid)
                if not referenceUUID:
                    raise ValidationError(_('It must to send the origin receipt to ETA before the refund.'))
                else:
                    referenceUUID = referenceUUID[-1].eta_uuid

            header.update({
                'referenceUUID': referenceUUID or self.eta_uuid
            })

        header.update({
            "referenceOldUUID": "",
            "currency": currency_id.name,
            "exchangeRate": self.currency_rate if currency_id.id != company_currency_id.id else 0,
            "sOrderNameCode": self.name,
            "orderdeliveryMode": "FC",
            "grossWeight": 0.0,
            "netWeight": 0.0
        })

        return header

    def _get_previous_order(self):
        order_ids = self.search(
            [('config_id', '=', self.config_id.id), ('eta_submit_state', '=', 'sent'), ('eta_status', '=', 'valid'),
             ('id', '!=', self.id)], order='date_order desc')
        if not order_ids:
            return ""
        return order_ids[0].eta_uuid or ""

    def _prepare_seller_info(self):
        device_config_id = self.config_id.device_config_id
        return {
            "rin": device_config_id.partner_id.vat,
            "companyTradeName": device_config_id.partner_id.name,
            "branchCode": device_config_id.branch_code,
            "branchAddress": {
                "country": device_config_id.partner_id.country_id.code,
                "governate": device_config_id.partner_id.state_id.name,
                "regionCity": device_config_id.partner_id.city,
                "street": device_config_id.partner_id.street,
                "buildingNumber": device_config_id.partner_id.building_no,
                "postalCode": device_config_id.partner_id.zip or "",
                "floor": device_config_id.partner_id.floor or "",
                "room": device_config_id.partner_id.room or "",
                "landmark": device_config_id.partner_id.landmark or "",
                "additionalInformation": device_config_id.partner_id.additional_information or ""
            },
            "deviceSerialNumber": device_config_id.serial_number,
            "syndicateLicenseNumber": device_config_id.syndicate_license_number or "",
            "activityCode": device_config_id.activity_code
        }

    def _prepare_buyer_info(self):
        partner = self.partner_id
        if abs(self.amount_total) > 150000:
            if not partner:
                raise ValidationError(_('If receipt is more than 50,000 buyer details are required.'))
            return {
                "type": "B" if partner.company_type == 'company' and partner.country_id.code == 'EG' else "P" if partner.company_type == 'person' and partner.country_id.code == 'EG' else "F",
                "id": partner.vat,
                "name": partner.name,
                "mobileNumber": partner.mobile or "",
                "paymentNumber": ""
            }
        else:
            return {
                "type": "P",
                "id": partner.vat or "",
                "name": partner.name or "",
                "mobileNumber": partner.mobile or "",
                "paymentNumber": ""
            }

    def _prepare_item_lines(self):
        item_data = []
        for line in self.lines:
            if line.price_unit > 0:
                receipt_data = {
                    "internalCode": line.product_id.default_code or "",
                    "description": line.full_product_name,
                    "itemType": line.product_id.item_type,
                    "itemCode": line.product_id.item_code,
                    "unitType": line.product_uom_id.unit_type,
                    "quantity": abs(line.qty),
                    "unitPrice": self._get_amount(line.price_subtotal / line.qty),
                    "netSale": self._get_amount(line.price_subtotal),
                    "totalSale": self._get_amount(line.qty * line.price_unit),
                    "total": self._get_amount(line.price_subtotal_incl)
                }
                discount = abs((line.discount / 100.0) * self._get_amount(line.qty * line.price_unit))

                receipt_data.update({
                    "valueDifference": 0.0,
                    "taxableItems": [
                        {
                            "taxType": str(tax.eg_eta_code).split('_')[0].upper(),
                            "amount": self._get_amount(abs((tax.amount / 100.0) * line.price_subtotal)) or 0,
                            "subType": str(tax.eg_eta_code).split('_')[1].upper(),
                            "rate": abs(tax.amount) or 0,
                        } for tax in line.tax_ids_after_fiscal_position if tax.eg_eta_code
                    ]
                })
                if discount:
                    if line.tax_ids:
                        receipt_data.update({
                            "commercialDiscountData": [{
                                'amount': self._get_amount(discount),
                                'description': str(self._get_amount(discount)),
                            }
                            ],
                        })
                    else:
                        receipt_data.update({
                            "itemDiscountData": [
                                 self._get_amount(discount),
                            ],
                        })
                item_data.append(receipt_data)
        _logger.info('Item Data: %s.' % item_data)
        return item_data

    def _amount_grouped_tax(self, lines=None):
        tax_lines = []
        if not lines:
            lines = self.lines
        for line in lines:
            taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
            taxes = self.fiscal_position_id.map_tax(taxes)
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = taxes.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id,
                                      partner=line.order_id.partner_id or False)['taxes']
            for tax in taxes:
                new_tax = True
                taxType = self.env['account.tax'].sudo().browse(tax['id']).eg_eta_code.split('_')[0].upper()
                for line in tax_lines:
                    if taxType and line['taxType'] == taxType:
                        line['amount'] += self._get_amount(tax['amount'])
                        new_tax = False

                if new_tax:
                    tax_lines.append({
                        'amount': self._get_amount(tax['amount']),
                        'taxType': taxType or ""
                    })

        return tax_lines

    def _prepare_receipt_data(self):
        return {
            "header": self._prepare_header_info(),
            "documentType": {
                "receiptType": "S" if self.amount_total > 0.0 else "r",
                "typeVersion": "1.2"
            },
            "seller": self._prepare_seller_info(),
            "buyer": self._prepare_buyer_info(),
            "itemData": self._prepare_item_lines(),
            "totalSales": self._get_amount(sum([line.qty * line.price_unit for line in self.lines])),
            "totalCommercialDiscount": self._get_amount(
                sum([(line.discount / 100.0) * line.qty * line.price_unit for line in self.lines if line.tax_ids])),
            "totalItemsDiscount": self._get_amount(
                sum([(line.discount / 100.0) * line.qty * line.price_unit for line in self.lines if not line.tax_ids])),
            "extraReceiptDiscountData": [{
                'amount': self._get_amount(self._prepare_global_discount()),
                'description': 'Global Discount',
            }],
            "netAmount": self._get_amount(sum([line.price_subtotal for line in self.lines])),
            # "feesAmount": 0.0,
            "totalAmount": self._get_amount(self.amount_total),
            "taxTotals": self._amount_grouped_tax(),
            "paymentMethod": self.payment_ids[0].payment_method_id.eg_eta_code if self.payment_ids and self.payment_ids[
                0].payment_method_id.eg_eta_code else "C",
        }

    def _action_gen_uuid(self, receipt_data):
        DEVICE_CONFIG = self.env['pos.device.config']
        SERIALIZED_DATA = DEVICE_CONFIG._serialize_receipt(receipt_data)
        UUID = DEVICE_CONFIG._hash_serialized_receipt(SERIALIZED_DATA)
        self.eta_uuid = UUID
        return UUID

    def _prepare_receipt_for_eta(self):
        receipt_data = self._prepare_receipt_data()
        uuid = self._action_gen_uuid(receipt_data)
        receipt_data['header']['uuid'] = uuid
        return receipt_data

    def _get_access_token(self):
        token = self._get_exist_access_token()
        if token:
            return token

        if self.config_id.device_config_id.production_env:
            url = ETA_URLS['access_token_pro']
        else:
            url = ETA_URLS['access_token_pre']
        credentials = self._get_pos_credentials()
        payload = 'grant_type={}&client_id={}&client_secret={}'.format(credentials['grant_type'],
                                                                       credentials['client_id'],
                                                                       credentials['client_secret'])
        headers = {
            'posserial': credentials['posserial'],
            'pososversion': credentials['pososversion'],
            'posmodelframework': '',
            'presharedkey': '',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            _logger.info('Token Request: %s.' % response.text)
            response_data = response.json()
            if 'error' in response_data:
                raise ValidationError(_(response_data['error']))

            token = response_data.get('access_token')
            if token:
                DEVICE_CONFIG = self.config_id.device_config_id
                DEVICE_CONFIG.access_token = token
                DEVICE_CONFIG.token_expiration_date = datetime.now() + timedelta(
                    seconds=response_data.get('expires_in'))
                return token
        except Exception as ex:
            raise ValidationError(_('%s' % ex))

    def _get_pos_credentials(self):
        DEVICE_CONFIG = self.config_id.device_config_id
        return {
            'grant_type': DEVICE_CONFIG.grant_type,
            'client_id': DEVICE_CONFIG.client_id,
            'client_secret': DEVICE_CONFIG.client_secret,
            'posserial': DEVICE_CONFIG.serial_number,
            'pososversion': DEVICE_CONFIG.pos_os_version
        }

    def _get_exist_access_token(self):
        DEVICE_CONFIG = self.config_id.device_config_id
        if DEVICE_CONFIG.access_token and DEVICE_CONFIG.token_expiration_date and datetime.now() <= DEVICE_CONFIG.token_expiration_date:
            return DEVICE_CONFIG.access_token
        return False

    def _get_amount(self, amount):
        from_currency = self.currency_id
        to_currency = self.company_id.currency_id
        new_amount = amount
        if from_currency != to_currency:
            new_amount = amount * self._exchange_currency_rate()
        _logger.info('Calculate Amount: %s.' % new_amount)
        return abs(round(new_amount, 5))

    def _exchange_currency_rate(self):
        from_currency = self.currency_id
        to_currency = self.company_id.currency_id
        company = self.company_id
        rate = 1.0
        if from_currency != to_currency:
            rate = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company,
                                                                 self.date_order)
        _logger.info('Exchange Rate: %s.' % rate)
        return round(rate, 5)

    def action_send_eta_receipt(self):
        payload = {"receipts": []}
        main_order = False
        for order in self:
            if main_order and main_order.config_id != order.config_id:
                raise ValidationError(_('All orders must be from one pos while send patch.'))

            main_order = order
            print(order.config_id.dont_send_e_receipt)
            if not order.config_id.device_config_id:
                raise ValidationError(_('Create ETA configuration for this POS.'))

            if order.eta_submit_state == 'sent' and order.eta_status == 'valid':
                raise ValidationError(_('This receipt was already sent.'))

            receipt_data = order._prepare_receipt_for_eta()
            pprint.pprint(receipt_data)
            # self.test_receipt_calculatoins(receipt_data)
            payload['receipts'].append(receipt_data)

        access_token = main_order._get_access_token()
        _logger.info('Access Token: %s.' % access_token)

        if main_order.config_id.device_config_id.production_env:
            url = ETA_URLS['submit_receipt_pro']
        else:
            url = ETA_URLS['submit_receipt_pre']
        headers = {
            'Authorization': 'Bearer %s' % access_token,
            'Content-Type': 'application/json'
        }

        data = json.dumps(payload, ensure_ascii=False, indent=4).encode('utf-8')
        try:
            response = requests.request("POST", url, headers=headers, data=data)
            _logger.info('Submit URL: %s.' % url)
            _logger.info('Returned Response: %s.' % response.text)

            response_data = response.json()
            print(response_data)
            if 'acceptedDocuments' in response_data:
                for acc_receipt in response_data['acceptedDocuments']:
                    rec = self.search([('eta_uuid', '=', acc_receipt['uuid'])])
                    if rec:
                        rec.eta_submit_state = 'sent'
                        rec.eta_status = 'valid'

            if 'rejectedDocuments' in response_data:
                for rej_receipt in response_data['rejectedDocuments']:
                    rec = self.search([('eta_uuid', '=', rej_receipt['uuid'])])
                    if rec:
                        rec.eta_submit_state = 'sent'
                        rec.eta_status = 'invalid'
                        if 'error' in rej_receipt and 'details' in rej_receipt['error']:
                            errors = []
                            for error in rej_receipt['error']['details']:
                                errors.append('Message: %s, Target: %s,  Property Path: %s' % (
                                    error['message'], error['target'], error['propertyPath']))

                            text_error = '\n'.join(errors)
                            rec.invalid_reason = text_error



        except Exception as ex:
            _logger.error('Error When Send: %s.' % ex)
            raise ValidationError(_('%s' % ex))

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param dict order: dictionary representing the order.
        :param bool draft: Indicate that the pos_order is not validated yet.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns: id of created/updated pos.order
        :rtype: int
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
            pos_order._create_order_picking()
            # pos_order._compute_total_cost_in_real_time()

        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order._generate_pos_order_invoice()
        if not pos_order.config_id.dont_send_e_receipt:
            pos_order.action_send_eta_receipt()

        return pos_order.id

    # def test_receipt_calculatoins(self,data):
    #     for item in data['itemData']:
    #         if not (item['totalSale'] == item['quantity'] * item['unitPrice']):
    #             print('nooooooo',item['totalSale'],(item['quantity'] * item['unitPrice']))
    #         # if not (item['netSale'] == (item['totalSale'] - sum(item['commercialDiscountData']['amount']))):
    #         print('nooooooo',item['netSale'],item['totalSale'], item['commercialDiscountData'][0]['amount'])

    def _prepare_global_discount(self):
        total = 0
        for line in self.lines:
            if line.price_unit < 0:
                total += line.price_subtotal_incl
        return total
