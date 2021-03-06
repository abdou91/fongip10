# -*- coding: utf-8 -*-
{
    'name': "Recettes-Dépenses",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Abdou Mbar Ly",
    'website': "http://www.fongip.sn",

    # Categories can be used to filter modules in modules listing
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'mail',
        'contracts',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/credit_advice.xml',
        'views/dat.xml',
        #'report/hr_pointage_reports.xml',
        #'report/hr_presence_templates.xml',
        #'data/mail_templates.xml',
        #'views/hr_horaire_views.xml',
        #'views/hr_absence_views.xml',
        #'data/hr_pointage_ir_cron.xml',
    ],
    
    'qweb' : [
    
    ],
    'license': 'LGPL-3',
}
