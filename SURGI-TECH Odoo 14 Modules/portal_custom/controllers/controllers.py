import base64
import logging
import json
from xml import dom
import werkzeug
from odoo.exceptions import AccessError
from datetime import datetime
from odoo import _
import odoo.http as http
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.web.controllers.main import Home
_logger = logging.getLogger(__name__)
