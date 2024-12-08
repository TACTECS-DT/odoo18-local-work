from odoo import http, _
from operator import itemgetter
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time
from collections import OrderedDict
from collections import namedtuple
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.http import request ,Response
from odoo.osv.expression import OR
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime , timedelta
from odoo.tools import groupby as groupbyelem
from werkzeug.utils import secure_filename, redirect
from odoo.fields import Datetime
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from odoo import http, _, fields
import werkzeug
import binascii
import json
from odoo.addons.portal.controllers.mail import _message_post_helper

from odoo.exceptions import AccessError, MissingError

@http.route(['/my/operation/<int:request_id>'], type='http', auth="public", website=True)
def portal_operation_page(self, request_id, report_type=None, access_token=None, message=False,
                                    download=False, **kw):
    user = request.env.user
    if not user.operation_portal_access:
        return redirect('/my/access-denied')

    try:
        request_sudo = self._document_check_access('operation.operation', request_id,
                                                   access_token=access_token)
    except (AccessError, MissingError):
        return request.redirect('/my/home')

    if request_sudo and self._should_log_view(request_sudo, access_token):
        self._log_request_view(request_sudo, access_token)

    values = self._operation_get_page_view_values(request_sudo, access_token, **kw)
    values['message'] = message
    return request.render('surgi_operation_portal.portal_my_operations_view', values)


def _should_log_view(self, request_sudo, access_token):
    now = fields.Date.today().isoformat()
    session_obj_date = request.session.get('view_request_%s' % request_sudo.id)
    return session_obj_date != now and request.env.user.share and access_token


def _log_request_view(self, request_sudo, access_token):
    request.session['view_request_%s' % request_sudo.id] = fields.Date.today().isoformat()
    body = _('Request viewed by Employee %s', request_sudo.employee_id.name)
    _message_post_helper(
        "operation.operation",
        request_sudo.id,
        body,
        token=request_sudo.access_token,
        message_type="notification",
        subtype_xmlid="mail.mt_note",
        partner_ids=request_sudo.employee_id.user_id.sudo().partner_id.ids,
    )

def _operation_get_page_view_values(self, order, access_token, **kwargs):
    operationQuantities = http.request.env['stock.quant'].sudo().search(
        [("id", '=', order.id), ('location_id', '=', order.location_id.id), ('quantity', '>', 0)], limit=100)

    values = {
            'operation': order,
            'token': access_token,
            'return_url': '/my/operation',
            'bootstrap_formatting': True,
            'partner_id': request.env.user.partner_id.id,
        "operationQuantities": operationQuantities,

    }

    history = request.session.get('my_operation_history', [])
    values.update(get_records_pager(history, order))

        # Convert the date fields from order to Python datetime objects if needed

    return values
