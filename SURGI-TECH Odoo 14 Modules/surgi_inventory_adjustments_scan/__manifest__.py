{
    'name':'Surgi inventory adjustment Scan',
    'version' : '1.2',
    'category':'stock',
    'depends': ['stock','sale', 'product'],
    'data':[
        'security/ir.model.access.csv',
        'security/stock_inventory_security.xml',

        'view/stock_inventory_changes_view.xml'
    ],
'qweb': [
    'static/src/xml/Ahmed_button.xml',
    'static/src/xml/stock.xml',
]
}