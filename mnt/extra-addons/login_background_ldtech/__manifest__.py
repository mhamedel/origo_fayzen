# -*- encoding: utf-8 -*-
{
    'name': 'Odoo Login page background',
    'summary': 'The new configurable Odoo Web Login Screen',
    'version': '17.0.1.0.0',
    'category': 'website',
    'license': 'LGPL-3',
    'depends': ['base', 'base_setup', 'web', 'auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/login_image.xml',
        'templates/assets.xml',
        'templates/left_login_template.xml',
        'templates/right_login_template.xml',
        'templates/middle_login_template.xml',
    ],
    'qweb': [
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}

