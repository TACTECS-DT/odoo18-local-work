from odoo import fields, models, api
import json
import hashlib


class POSDeviceConfig(models.Model):
    _name = 'pos.device.config'
    _description = 'POS Device Config'
    _rec_name = 'name'

    _sql_constraints = [
        ('pos_company_uniq', 'unique (pos_id,company_id)', 'The pos must be unique per company !')
    ]

    name = fields.Char('Name', required=True, copy=False, index=True)
    pos_id = fields.Many2one('pos.config', 'POS', required=True, domain="[('company_id', '=', company_id)]", copy=False,
                             inverse='_set_pos_with_config')
    partner_id = fields.Many2one('res.partner', 'Branch', required=True)
    branch_code = fields.Char('Branch Code', copy=False, required=True)
    serial_number = fields.Char('Serial Number', copy=False, required=True)
    syndicate_license_number = fields.Char('Syndicate License Number', copy=False)
    pos_os_version = fields.Char('POS OS Version', required=True)
    activity_code = fields.Char('Activity Code', required=True)
    pre_shared_key = fields.Char('Preshared Key')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    grant_type = fields.Char('Grant Type', required=True, copy=False)
    client_id = fields.Char('Client ID', required=True, copy=False)
    client_secret = fields.Char('Client Secret', required=True, copy=False)
    access_token = fields.Text('Access Token')
    token_expiration_date = fields.Datetime('Token Expiration Date')
    production_env = fields.Boolean('Production Env')

    def _set_pos_with_config(self):
        if self.pos_id:
            self.pos_id.device_config_id = self.id

    @api.model
    def _serialize_receipt(self, receipt_dict):
        if not isinstance(receipt_dict, dict):
            return json.dumps(str(receipt_dict), ensure_ascii=False)

        canonical_str = []
        for key, value in receipt_dict.items():
            if not isinstance(value, list):
                canonical_str.append(json.dumps(key, ensure_ascii=False).upper())
                canonical_str.append(self._serialize_receipt(value))
            else:
                canonical_str.append(json.dumps(key, ensure_ascii=False).upper())
                for elem in value:
                    canonical_str.append(json.dumps(key, ensure_ascii=False).upper())
                    canonical_str.append(self._serialize_receipt(elem))
        return ''.join(canonical_str)

    @api.model
    def _hash_serialized_receipt(self, serialized):
        hashed_data = hashlib.sha256(serialized.encode()).digest().hex()
        return hashed_data
