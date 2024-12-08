# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import base64
import io

from PIL import Image

from odoo import api, fields, models
from odoo.tools.mimetypes import guess_mimetype


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _pwa_icon_url_base = "/portal_attendance_knk/icon"

    pwa_name = fields.Char("Progressive Web App Name")
    pwa_short_name = fields.Char("Progressive Web App Short Name")
    pwa_icon = fields.Binary("Icon", readonly=False)
    pwa_background_color = fields.Char("Background Color")
    pwa_theme_color = fields.Char("Theme Color")

    @api.model
    def get_values(self):
        config_parameter_obj_sudo = self.env["ir.config_parameter"].sudo()
        res = super(ResConfigSettings, self).get_values()
        res["pwa_name"] = (
            config_parameter_obj_sudo.get_param(
                "pwa.manifest.name", default="Odoo Attendance")
        )
        res["pwa_short_name"] = (
            config_parameter_obj_sudo.get_param(
                "pwa.manifest.short_name", default="Odoo Attendance")
        )
        pwa_icon_ir_attachment = (
            self.env["ir.attachment"]
            .sudo()
            .search([("url", "like", self._pwa_icon_url_base + ".")])
        )
        res["pwa_icon"] = (
            pwa_icon_ir_attachment.datas if pwa_icon_ir_attachment else False
        )
        res["pwa_background_color"] = (
            config_parameter_obj_sudo.get_param(
                "pwa.manifest.background_color", default="#2E69B5")
        )
        res["pwa_theme_color"] = (
            config_parameter_obj_sudo.get_param(
                "pwa.manifest.theme_color", default="#2E69B5")
        )
        return res

    def _unpack_icon(self, icon):
        # Wrap decoded_icon in BytesIO object
        decoded_icon = base64.b64decode(icon)
        icon_bytes = io.BytesIO(decoded_icon)
        return Image.open(icon_bytes)

    def _write_icon_to_attachment(self, extension, mimetype, size=None):
        url = self._pwa_icon_url_base + extension
        icon = self.pwa_icon
        # Resize image
        if size:
            image = self._unpack_icon(icon)
            resized_image = image.resize(size)
            icon_bytes_output = io.BytesIO()
            resized_image.save(icon_bytes_output, format=extension.lstrip(".").upper())
            icon = base64.b64encode(icon_bytes_output.getvalue())
            url = "%s%sx%s%s" % (
                self._pwa_icon_url_base,
                str(size[0]),
                str(size[1]),
                extension,
            )
        # Retreive existing attachment
        existing_attachment = (
            self.env["ir.attachment"].sudo().search([("url", "like", url)])
        )
        # Write values to ir_attachment
        values = {
            "datas": icon,
            "db_datas": icon,
            "url": url,
            "name": url,
            "type": "binary",
            "mimetype": mimetype,
        }
        # Rewrite if exists, else create
        if existing_attachment:
            existing_attachment.sudo().write(values)
        else:
            self.env["ir.attachment"].sudo().create(values)

    @api.model
    def set_values(self):
        config_parameter_obj_sudo = self.env["ir.config_parameter"].sudo()
        res = super(ResConfigSettings, self).set_values()
        config_parameter_obj_sudo.set_param(
            "pwa.manifest.name", self.pwa_name
        )
        config_parameter_obj_sudo.set_param(
            "pwa.manifest.short_name", self.pwa_short_name
        )
        config_parameter_obj_sudo.set_param(
            "pwa.manifest.background_color", self.pwa_background_color
        )
        config_parameter_obj_sudo.set_param(
            "pwa.manifest.theme_color", self.pwa_theme_color
        )
        # Retrieve previous value for pwa_icon from ir_attachment
        pwa_icon_ir_attachments = (
            self.env["ir.attachment"]
            .sudo()
            .search([("url", "like", self._pwa_icon_url_base)])
        )
        # Delete or ignore if no icon provided
        if not self.pwa_icon:
            if pwa_icon_ir_attachments:
                pwa_icon_ir_attachments.unlink()
            return res
        decoded_pwa_icon = base64.b64decode(self.pwa_icon)
        # Full mimetype detection
        pwa_icon_mimetype = guess_mimetype(decoded_pwa_icon)
        pwa_icon_extension = "." + pwa_icon_mimetype.split("/")[-1].split("+")[0]
        if pwa_icon_ir_attachments:
            pwa_icon_ir_attachments.unlink()
        self._write_icon_to_attachment(pwa_icon_extension, pwa_icon_mimetype)

        for size in [
            (128, 128),
            (144, 144),
            (152, 152),
            (192, 192),
            (256, 256),
            (512, 512),
        ]:
            self._write_icon_to_attachment(
                pwa_icon_extension, pwa_icon_mimetype, size=size
            )
