# -*- coding: utf-8 -*-


from datetime import datetime
from odoo import api, models, fields, _



class Payment(models.Model):
    _inherit = 'account.payment'

    payment_date = fields.Date(string='Registrarion Date', required="True", default=datetime.now())
    move_name = fields.Char()

class Diarios(models.Model):
    _inherit = 'account.journal'

    default_debit_account_id = fields.Many2one('account.account',compute='_compute_cuenta_debit')

    #@api.onchange('default_account_id')
    @api.depends('default_account_id')
    def _compute_cuenta_debit(self):
        self.default_debit_account_id=self.default_account_id

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_payment_state = fields.Char()
    type_aux = fields.Char(compute='_compute_move_type')
    type = fields.Char()

    @api.depends('move_type')
    def _compute_move_type(self):
        self.type_aux=self.move_type
        self.type=self.move_type
    
