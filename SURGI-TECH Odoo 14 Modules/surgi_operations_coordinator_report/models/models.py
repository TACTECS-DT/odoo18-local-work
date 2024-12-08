from odoo import models
import datetime
from datetime import date, datetime, time, timedelta
from pytz import timezone
import xlsxwriter



class ReportOperationCoordinator(models.AbstractModel):
    _name = 'report.surgi_operations_coordinator_report.coordinator_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        x=0
        for par in partners:
            yy=str('sheet'+str(x))
            worksheet = workbook.add_worksheet(yy[:31])
            x+=1
            # worksheet.right_to_left()

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
                'border_color': 'black',})

            # worksheet.left_to_right()
            worksheet.set_column('A:A', 35)
            worksheet.set_column('B:B', 35)
            worksheet.set_column('C:C', 30)
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



            worksheet.merge_range('B1:D1', 'Operation Coordinator Excel Report', header_format2)

            worksheet.write('A6', par.sequence, header_format)

            worksheet.write('A8', 'Date Start', header_format)
            worksheet.write('A9', 'Operation Type', header_format)
            worksheet.write('A10', 'Delivery Type', header_format)
            worksheet.write('A11', 'Responsible', header_format)
            worksheet.write('A12', 'Sales Channel', header_format)
            worksheet.write('A13', 'Area Manager', header_format)
            worksheet.write('A14', 'Patient', header_format3)
            worksheet.write('A15', 'Patient Name', header_format)
            worksheet.write('A16', 'Patient National ID', header_format)
            worksheet.write('A17', 'MOH Approved Operation', header_format)
            worksheet.write('A18', 'Side', header_format)
            worksheet.write('A19', 'Patient Gender', header_format)
            worksheet.write('A20', 'Surgeon', header_format3)
            worksheet.write('A21', 'Hospital', header_format)
            worksheet.write('A22', 'Authority Type', header_format)
            worksheet.write('A23', 'Salesperson', header_format3)
            worksheet.write('A24', 'Surgeon', header_format)
            worksheet.write('A25', 'Payment Methods', header_format)
            worksheet.write('A26', 'Supply', header_format3)
            worksheet.write('A27', 'Warehouse', header_format)
            worksheet.write('A29', 'Components', header_format3)

            worksheet.write('B8', par.start_datetime, header_format)
            worksheet.write('B9', par.operation_type.name, header_format)
            worksheet.write('B10', par.operation_delivery_type, header_format)
            worksheet.write('B11', par.responsible.name, header_format)
            worksheet.write('B12', par.op_sales_area.name, header_format)
            worksheet.write('B13', par.op_area_manager.name, header_format)
            worksheet.write('B15', par.patient_name, header_format)
            worksheet.write('B16', par.patient_national_id, header_format)
            worksheet.write('B17', par.moh_approved_operation, header_format)
            if par.side=='r':
                worksheet.write('B18', "Right", header_format)
            elif par.side=='l':
                worksheet.write('B18', "Left", header_format)
            else:
                worksheet.write('B18', "", header_format)


            if par.patient_gender=='m':
                worksheet.write('B19', "Male", header_format)
            elif par.patient_gender=='f':
                worksheet.write('B19', "Female", header_format)
            else:
                worksheet.write('B19', "", header_format)

            worksheet.write('B21', par.hospital_id.name, header_format)
            worksheet.write('B22', par.authority, header_format)
            worksheet.write('B24', par.surgeon_id.name, header_format)
            worksheet.write('B25', par.payment_methods, header_format)
            worksheet.write('B27', par.warehouse_id.name, header_format)

            worksheet.write('A30', 'Barcode', header_format)
            worksheet.write('B30', 'Name', header_format)
            number = 1
            row = 30
            col = 0
            for com in par.component_ids:
                if com.barcode:
                    worksheet.write(row, col, str(com.barcode), header_format3)
                else:
                    worksheet.write(row, col,'', header_format3)

                if com.name:
                    worksheet.write(row, col+1, str(com.name), header_format3)
                else:
                    worksheet.write(row, col + 1, '', header_format3)

                number += 1
                row += 1
            worksheet.write(row+1,col, 'Product', header_format3)
            worksheet.write(row+2,col, 'Product', header_format)
            worksheet.write(row+2,col+1, 'Quantity', header_format)

            row2=row+3
            number2=number
            for com in par.product_lines:
                if com.product_id:
                    worksheet.write(row2, col, str(com.product_id.name), header_format3)
                else:
                    worksheet.write(row2, col,'', header_format3)

                if com.quantity:
                    worksheet.write(row2, col+1, str(com.quantity), header_format3)
                else:
                    worksheet.write(row2, col + 1, '', header_format3)

                number += 1
                row2 += 1

            worksheet.write(row2+2,col, 'Notes', header_format3)
            AR=row2+4
            AC=col

            mer_cell1 = 'A' + str(AR)
            mer_cell2 = 'C' + str(AR)
            position = str(mer_cell1 + ':' + mer_cell2)
            worksheet.set_row(AR-1, 70)

            worksheet.merge_range(position, par.notes, header_format)

