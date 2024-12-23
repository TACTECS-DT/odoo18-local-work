{
    'name': 'Inventory Count 18 Changes',
    'version': '18.1',
    'depends': ['base',"setu_inventory_count_management_18","web"],
    'data': [
        'views/inventory_count.xml',
        'views/scan_action.xml',
        'views/inventory_count_session.xml',
        'views/stock_inventory.xml',
    ],



'assets': {
            'web.assets_backend':[
             
                'inventory_count_management_18_changes/static/src/js/scan.js',
                'inventory_count_management_18_changes/static/src/xml/wizard.xml',
                'inventory_count_management_18_changes/static/src/xml/scan.xml',
                
                ],
         
              },

}
