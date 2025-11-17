# -*- coding: utf-8 -*-

{
    "name" : "Contacts realcred",
    "summary" : "Contacts realcred",
    "version" : "15.0",
    "description": """

    """,
    'author' : '',
    'support': '',
    'license' : 'OPL-1',
    'images': [],
    "depends" : ['report_xlsx','crm'],
    "data" : [  'security/group.xml',
                'security/ir.model.access.csv',
                'data/ir_cron.xml',
                'data/server_action.xml',
                'views/contacts_realcred_view.xml',
                'views/contacts_realcred_campaign_view.xml',
                'views/menu.xml',
                'views/crm.xml',
                'views/res_partner.xml',
                #'views/view_order_purchase.xml',
                #'views/purchase_order.xml',
                #'views/report_order_purchase.xml',
                'report/report_report.xml',
            ],
    "auto_install": False,
    "installable": True,
}
