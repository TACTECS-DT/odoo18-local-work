# -*- coding: utf-8 -*-
{
    'name': "elearning hide course",


    'summary': """elearning hide course""",

    'description': """
           The following modulated, allows you to hide a course 
           from the list of courses to share the link with a user
           so that they can see it. 
           Once the user purchases the course or is a member 
           of the course, the course will appear in the list of courses

        """,
    'author': 'David Montero Crespo',
    'license': 'AGPL-3',
    'category': 'Website',
    'version': '13.0',
    'website': "https://softwareescarlata.com/",

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale_slides'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'images': ['static/description/imagen.png'],
    'currency': 'EUR',
    'price': 20,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}