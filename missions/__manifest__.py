# -*- coding: utf-8 -*-
{
    'name' : 'Missions',
    'version' : '0.1',
    #'sequence': 165,
    'author': "Abdou Mbar Ly",
    'website': "http://www.fongip.sn",
    'category': 'Human Resources/Missions',
    'website' : 'http://dev.com',
    'summary' : 'Gestion de missions',
    'description' : """
Missions , ordres de missions et les couts liés aux missions
==================================
Ce module vous aide à gérer les missions de votre entreprise.
Main Features
-------------
* Créer une mission .
* Calculer les perdiums

""",
    'depends': [
        'base',
        'mail',
        'hr',
        'fleet',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/template_etat_liquidatif.xml',
        'report/template_ordre_mission.xml',
        'report/report.xml',
        #'views/fleet_vehicle_views.xml',
        #'views/fleet_vehicle_cost_views.xml',
        #'views/fleet_board_view.xml',
        #'views/mail_activity_views.xml',
        'views/mission.xml',
        'views/vehicle.xml',
        'views/carburant.xml',
        'data/ir_sequence_data.xml',
        #'data/fleet_data.xml',
        #'data/mail_data.xml',
    ],
    'qweb' : [
    
    ],
    'license': 'LGPL-3',

    #'demo': ['data/fleet_demo.xml'],

    'installable': True,
    'application': True,
}
