# -*- coding: utf-8 -*-

{
    "name" : "CRM PRODUCTS",
    "summary" : "CRM PRODUCTS",
    "version" : "15.0",
    "description": """

    """,
    'author' : '',
    'support': '',
    'license' : 'OPL-1',
    'images': [],
    "depends" : ['crm','purchase','sale','utm'],
    "data" : [
                'security/ir.model.access.csv',
                'views/product.xml',
                'views/crm.xml',
                'views/sale_order_notes.xml',
                'views/permissions.xml'
            ],
    "auto_install": False,
    "installable": True,
}
