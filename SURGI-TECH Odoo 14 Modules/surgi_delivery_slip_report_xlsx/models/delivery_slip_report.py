from odoo import models
import datetime
from datetime import date, datetime, time, timedelta
from pytz import timezone
import xlsxwriter



class ReportDeliverySlipExcel(models.AbstractModel):
    _name = 'report.surgi_delivery_slip_report_xlsx.delivery_slip_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        x=0
        for par in partners:
            yy=str('sheet'+str(x))
            worksheet = workbook.add_worksheet(yy[:31])
            x+=1
            header_format = workbook.add_format({
                'font_size': 16,
                'border': 1,
                'align': 'left',
                'font_color': 'black',
                'bold': True,
                'valign': 'vcenter',
                'border_color': 'black',
                'fg_color': '#C0C0C0'})
            header_format2 = workbook.add_format({
                'font_size': 18,
                'border': 1,
                'align': 'center',
                'font_color': 'white',
                'bold': True,
                'valign': 'vcenter',
                'border_color': 'black',
                'fg_color': '#C0C0C0'})
            header_format3 = workbook.add_format({
                'font_size': 14,
                'border': 1,
                'align': 'left',
                'font_color': 'black',
                'bold': True,
                'valign': 'vcenter',
                })

            # worksheet.left_to_right()
            worksheet.set_column('A:A', 40)
            worksheet.set_column('B:B', 40)
            worksheet.set_column('C:C', 40)
            worksheet.set_column('D:D', 30)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('G:G', 50)
            worksheet.set_column('F:F', 50)
            worksheet.set_column('H:H', 50)
            worksheet.set_column('I:I', 20)
            worksheet.set_column('J:J', 20)
            worksheet.set_column('K:K', 20)
            worksheet.set_column('L:L', 20)
            worksheet.set_column('M:M', 20)



            domain = []
            worksheet.set_row(0, 40)
            worksheet.set_default_row(25)



            worksheet.merge_range('B1:D1', 'Delivery Slip Report', header_format2)

            worksheet.write('C3', par.name, header_format)

            worksheet.write('B5', 'Partner', header_format)
            worksheet.write('B6', par.partner_id.name, header_format3)
            worksheet.write('C5', 'Effective Date', header_format)

            date_done=''
            if par.date_done:
                date_done = datetime.strptime(str(par.date_done).split(".")[0],
                                                      '%Y-%m-%d %H:%M:%S')
                worksheet.write('C6', str(date_done), header_format3)

            worksheet.write('A8', 'Product', header_format)
            worksheet.write('B8', 'Lot/Serial Number', header_format)
            worksheet.write('C8', 'Done', header_format)
            number = 1
            row = 8
            col=0
            for line in par.move_line_nosuggest_ids:
                if line.product_id:
                    product=""
                    if line.product_id.default_code:
                        product="["+line.product_id.default_code+"] "+line.product_id.name
                    else:
                        product= line.product_id.name
                    worksheet.write(row, col, str(product), header_format3)
                if line.lot_id:
                    worksheet.write(row, col+1, str(line.lot_id.name), header_format3)
                if line.qty_done:
                    worksheet.write(row, col+2, str(line.qty_done), header_format3)

                number += 1
                row += 1
