# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api

import logging
from odoo.exceptions import UserError

from odoo.http import Response


class operation_stage(models.Model):
    _inherit = 'operation.operation'
    is_tender=fields.Boolean(related='operation_type.is_tender')
    def make_response(self, data, headers=None, cookies=None):
        """ Helper for non-HTML responses, or HTML responses with custom
        response headers or cookies.

        While handlers can just return the HTML markup of a page they want to
        send as a string if non-HTML data is returned they need to create a
        complete response object, or the returned data will not be correctly
        interpreted by the clients.

        :param basestring data: response body
        :param headers: HTTP headers to set on the response
        :type headers: ``[(name, value)]``
        :param collections.Mapping cookies: cookies to set on the client
        """
        response = Response(data, headers=headers)
        if cookies:
            for k, v in cookies.items():
                response.set_cookie(k, v)
        return response

    def send_waitinglist_sales_order(self):
        invoice = self.env['sale.order'].sudo().search([("operation_id", "=", self.id)])

        # sql = "select * from sale_order where operation_id = %d" % self.id
        # self.env.cr.execute(sql)
        # invoice=self.env.cr.dictfetchone()
        # invoiceid=invoice['id']
        if invoice:
            report = self.env.ref('surgi_waitinglist.report_saleorderwaitinginhert',False)
            if report:
                pdf_content, content_type = report.sudo()._render_qweb_pdf(invoice.id)

            else:
                raise UserError('No Report.')
            attachment = self.env['ir.attachment'].sudo().create({
                'name': str(invoice.patient_name)+" - "+str(invoice.operation_id.patient_national_id)+" Invoice"+".pdf",
                'type': 'binary',
                'datas': base64.encodebytes(pdf_content),
                'res_model': 'sale.order',#invoice._name,
                'res_id': invoice.id
            })

            subject = '%s, Sales Order' % (invoice.patient_name)
            template = self.env.ref('surgi_waitinglist.sales_report_waiting_mail', raise_if_not_found=False)
            if template:
                email_values = {
                    'attachment_ids': attachment,
                }

                template.sudo().send_mail(
                    invoice.id,
                    email_values=email_values,
                    notif_layout='mail.mail_notification_light')

            else:
                raise UserError('No Sales Order.')


            return True
        else:
            raise UserError('No Sales Order.')
        pass
    def send_waitinglist_sales_order1(self):
        invoice=self.env['sale.order'].search([("operation_id","=",self.id)])
        sql="select * from sale_order where operation_id = %s"%self.id
        invoice=self.env.cr.execute(sql)
        if invoice:
            template_id = self.env['ir.model.data'].get_object_reference('surgi_waitinglist','sales_report_waiting_mail')[1]
            email_template_obj = self.env['mail.template'].browse(template_id)
            logger = logging.getLogger(__name__)

            logger.debug("EEEEEEEEE> %s TTT %s AAAAAAAAAAAAAA %s",(email_template_obj, template_id, invoice.id))
            print(email_template_obj, 'EEEEEEEEE', template_id, 'TTT', invoice.id, 'AAAAAAAAAAAAAA')
            if template_id:
                values = email_template_obj.generate_email(invoice.id, ['subject', 'body_html', 'email_from', 'email_to',
                                                                  'partner_to', 'email_cc', 'reply_to',
                                                                  'scheduled_date'])
                pdf, _ = self.env.ref('sale.action_report_saleorder')._render_qweb_pdf([invoice.id])
                report_template_id=pdf
                data_record = base64.b64encode(report_template_id)
                ir_values = {
                    'name': "operation sales order report",
                    'type': 'binary',
                    'datas': data_record,
                    # 'datas_fname': "operation sales order report" + '.pdf',
                    'store_fname': data_record,
                    'mimetype': 'application/x-pdf',
                }
                vals = {
                    'name': invoice.name,
                    'type': 'binary',
                    'store_fname': values['attachments'][0][0],
                    'datas': values['attachments'][0][1],
                    'res_id': invoice.id,
                    'res_model': 'sale.order',
                }
                attachment_id = self.env['ir.attachment'].create(vals)
                raise UserError('Done.')
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                msg_id.attachment_ids = [(6, 0, [attachment_id.id])]
                if msg_id:
                    mail_mail_obj.send([msg_id])



            # # invoice=invoice[0]
            # pdf, _ = self.env.ref('sale.action_report_saleorder').sudo()._render_qweb_pdf([invoice.id])
            # pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            # #return self.make_response(pdf, headers=pdfhttpheaders)
            #
            # #report_template_id = self.env.ref('sale.report_saleorder').render_qweb_pdf(invoice.id)
            # report_template_id=pdf
            # #raise UserError('Done.')
            # data_record = base64.b64encode(report_template_id)
            # ir_values = {
            #     'name': "operation sales order report",
            #     'type': 'binary',
            #     'datas': data_record,
            #     # 'datas_fname': "operation sales order report" + '.pdf',
            #     'store_fname': data_record,
            #     'mimetype': 'application/x-pdf',
            # }
            # data_id = self.env['ir.attachment'].create(ir_values)
            # #return data_id
            # #template = self.template_id
            # template = self.env.ref(['surgi_waitinglist.sales_report_waiting_mail']).id
            # template.attachment_ids = [(6, 0, [data_id.id])]
            # #self.partner_id.email
            # email_values = {'email_to':'ahmed887463@gmail.com' ,
            #                 'email_from': self.env.user.email}
            # self.env['mail.template'].browse(template).send_mail(self.id, email_values=email_values, force_send=True)
            # template.attachment_ids = [(3, data_id.id)]

            return True
        else:
            raise UserError('No Sales Order.')
        pass
