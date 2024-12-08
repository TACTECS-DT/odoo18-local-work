# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
import json

from odoo.http import Controller, request, route


class PWA(Controller):
    def get_asset_urls(self, asset_xml_id):
        qweb = request.env["ir.qweb"].sudo()
        assets = qweb._get_asset_nodes(asset_xml_id, {}, True, True)
        urls = []
        for asset in assets:
            if asset[0] == "link":
                urls.append(asset[1]["href"])
            if asset[0] == "script":
                urls.append(asset[1]["src"])
        return urls

    @route("/service-worker.js", type="http", auth="public")
    def service_worker(self):
        qweb = request.env["ir.qweb"].sudo()
        urls = []
        urls.extend(self.get_asset_urls("web.assets_common"))
        urls.extend(self.get_asset_urls("web.assets_backend"))
        version_list = []
        for url in urls:
            version_list.append(url.split("/")[3])
        cache_version = "-".join(version_list)
        mimetype = "text/javascript;charset=utf-8"
        content = qweb._render(
            "portal_attendance_knk.service_worker",
            {"pwa_cache_name": cache_version, "pwa_files_to_cache": urls},
        )
        return request.make_response(content, [("Content-Type", mimetype)])

    def _get_pwa_manifest_icons(self, pwa_icon):
        icons = []
        if not pwa_icon:
            for size in [
                (128, 128),
                (144, 144),
                (152, 152),
                (192, 192),
                (256, 256),
                (512, 512),
            ]:
                icons.append(
                    {
                        "src": "/portal_attendance_knk/static/img/icons/icon-%sx%s.png"
                        % (str(size[0]), str(size[1])),
                        "sizes": "%sx%s" % (str(size[0]), str(size[1])),
                        "type": "image/png",
                    }
                )
        elif not pwa_icon.mimetype.startswith("image/svg"):
            all_icons = (
                request.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("url", "like", "/portal_attendance_knk/icon"),
                        (
                            "url",
                            "not like",
                            "/portal_attendance_knk/icon.",
                        ),  # Get only resized icons
                    ]
                )
            )
            for icon in all_icons:
                icon_size_name = icon.url.split("/")[-1].lstrip("icon").split(".")[0]
                icons.append(
                    {
                        "src": icon.url,
                        "sizes": icon_size_name,
                        "type": icon.mimetype,
                    }
                )
        else:
            icons = [
                {
                    "src": pwa_icon.url,
                    "sizes": "128x128 144x144 152x152 192x192 256x256 512x512",
                    "type": pwa_icon.mimetype,
                }
            ]
        return icons

    def _get_pwa_manifest(self):
        """Webapp manifest"""
        config_param_sudo = request.env["ir.config_parameter"].sudo()
        pwa_name = config_param_sudo.get_param("pwa.manifest.name", "Odoo Attendance")
        pwa_short_name = config_param_sudo.get_param(
            "pwa.manifest.short_name", "Odoo Attendance"
        )
        pwa_icon = (
            request.env["ir.attachment"]
            .sudo()
            .search([("url", "like", "/portal_attendance_knk/icon.")])
        )
        background_color = config_param_sudo.get_param(
            "pwa.manifest.background_color", "#2E69B5"
        )
        theme_color = config_param_sudo.get_param("pwa.manifest.theme_color", "#2E69B5")
        return {
            "name": pwa_name,
            "short_name": pwa_short_name,
            "icons": self._get_pwa_manifest_icons(pwa_icon),
            "start_url": '/my/attendance',
            "display": "standalone",
            "background_color": background_color,
            "theme_color": theme_color,
        }

    @route("/portal_attendance_knk/manifest.json", type="http", auth="public")
    def manifest(self):
        return request.make_response(
            json.dumps(self._get_pwa_manifest()),
            headers=[("Content-Type", "application/json;charset=utf-8")],
        )
