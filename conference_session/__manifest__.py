{
    'name': 'Conference Sessions',
    'version': '17.0.1.0.0',
    'summary': 'Track sessions for conferences and training events',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/conference_session_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
