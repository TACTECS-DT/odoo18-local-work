{
    'name': 'Material Purchase Requisitions',
    'version': '18.0.1.0.0',
    'price': 79.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Product / Material Purchase Requisition and Stock Request by User""",
    'description': """
Material Purchase Requisitions
This module allows employees to create purchase requisitions and stock requests.

**Main Features:**
- Allow employees to create purchase requisitions.
- Employees can request multiple materials/items in a single purchase requisition.
- Approval workflow:
  - Department Head approval.
  - Purchase Requisition Head approval.
- Email notifications for approvals to Department Manager and Requisition Manager.
- Request actions:
  - Internal picking/internal order.
  - Purchase orders.
- Warehouse dispatch or vendor procurement based on stock availability.

**Additional Features:**
- Complete requisition status visibility.
- Integration with inventory and purchase modules.
- Real-time email updates for stakeholders.
- Multi-level approval system.

**Use Cases:**
- Construction management.
- Real estate management.
- Factory requisitions.
- Department-level purchase requisitions.

**Extended Functionalities:**
- Internal requisitions.
- Indent stock and order management.
- Inventory replenishment requisitions.
- Inter-organization shipping network support.
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_purchase_requisitions/304',
    'category': 'Inventory/Inventory',
    'depends': [
        'stock',
        'hr',
        'purchase',
    ],
    'data': [
        'security/security.xml',
        'security/multi_company_security.xml',
        #'security/ir.model.access.csv',
        'data/purchase_requisition_sequence.xml',
        'data/employee_purchase_approval_template.xml',
        'data/confirm_template_material_purchase.xml',
        'report/purchase_requisition_report.xml',
        'views/purchase_requisition_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_department_view.xml',
        'views/stock_picking_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
