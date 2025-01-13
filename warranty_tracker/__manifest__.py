{
    'name': 'Warranty Tracker',
    'version': '1.0',
    "description": """
    This module is for  odoo-17 taining purposes 
    """,
    'depends': ['base','web','mail',"account"],
    "license": "LGPL-3",
    "author": "anowarul karim",
    'data': [
        'security/warranty_tracker_security.xml',
        'security/ir.model.access.csv',
        'data/warranty_data.xml',
        'data/warranty_claim_data.xml',
        'data/warranty_data.csv',
        'views/warranty.xml',
        'views/warranty_claim_views.xml',
        'views/warranty_tracker_menus.xml',
        # 'views/inherited_employe_view.xml',
    ],
    'application': True,
}