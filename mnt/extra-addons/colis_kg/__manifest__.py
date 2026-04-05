# -*- coding: utf-8 -*-
{ 
    # this module is for customizing the unity and KG in sales , purchase order and invoice and avoir
    'name': "Colis KG Customization",

    'summary': "Customize Login Page",


    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_form.xml',
        # 'reports/custom_invoice_report.xml',
    ],
}

