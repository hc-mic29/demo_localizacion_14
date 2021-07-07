# -*- coding: utf-8 -*-
{
    'name': ' VE Modo de pagos',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Modo de pagos',
    'description': """
Modo de pago que habilita la vista para que el usuario cree los modos de pagos.
    """,
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'website': 'https://www.odoo.com/page/accounting',
    'depends' : ['account_check_printing'],
    'data': [
        #'data/ve_check_printing.xml',
        #'report/print_check.xml',
        #'report/print_check_top.xml',
        #'report/print_check_middle.xml',
        #'report/print_check_bottom.xml',
        'vista/view.xml'
    ],
    'installable': True,
    'auto_install': True,
}
