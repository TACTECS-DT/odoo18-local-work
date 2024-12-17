from odoo import models, fields


class SalesReport(models.Model):
    _name = 'sales.report'
    _description = 'Sales Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    bill_doc = fields.Char("Bill Doc")
    material_group_desc = fields.Char("Material Group Desc")
    sales_employee_name = fields.Text("Sales Employee Name")
    ship_to_name = fields.Text("Ship to Name")
    material = fields.Char("Material")
    material_description = fields.Text("Material Description")
    total_amount = fields.Float("Total Amount")
    tax_amount = fields.Float("Tax Amount")
    net_value = fields.Float("Net Value")
    cost = fields.Float("Cost")
    profit = fields.Float("Profit")
    payer = fields.Char("Payer")
    sales_office = fields.Char("Sales Office")
    delivery_number = fields.Char("Delivery Number")
    sales_order_number = fields.Char("Sales Order Number")
    standard_price = fields.Float("Standard Price")
    accounting_document = fields.Char("Accounting Document")
    min_price = fields.Float("Min Price")
    purchase_price_per_c = fields.Float("Purchase Price Per C")
    material_group = fields.Char("Material Group")
    billing_discerption = fields.Text("Billing Discerption")
    sales_unit = fields.Char("Sales Unit")
    customer_group = fields.Char("Customer Group")
    customer_grp_Descrip = fields.Text("Customer Grp Descrip")
    payer_name = fields.Text("Payer Name")
    billed_quantity = fields.Float("Billed Quantity")
    ship_to = fields.Char("Ship To")
    sales_employee = fields.Char("Sales Employee")
    vendors_description = fields.Char("Vendors Description")
    billing_status = fields.Char("Billing Status")
    billing_status_descr = fields.Char("Billing Status Descr")
    payment_terms = fields.Char("Payment Terms")
    item = fields.Char("Item")
    business_units_descr = fields.Text("Business Units Descr")
    vendors = fields.Char("Vendors")
    business_units = fields.Char("Business Units")
    tax_number = fields.Char("Tax Number")
    customer_tax_status = fields.Char("Customer Tax Status")
    material_type = fields.Char("Material Type")
    billing_type = fields.Char("Billing Type")
    payment_terms_descri = fields.Char("Payment Terms Descri")
    billing_date = fields.Datetime("Billing Date")
    currency = fields.Selection(selection=[
        ('egp', 'EGP'),
        ('eur', 'EUR'),
        ('usd', 'USD'),
    ], string="currency", default="egp")

