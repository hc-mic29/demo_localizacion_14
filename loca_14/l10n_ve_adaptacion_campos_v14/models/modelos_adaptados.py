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

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat', 'country_id')
    def check_vat(self):
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company = self.env.company
        if company.vat_check_vies:
            # force full VIES online check
            check_func = self.vies_vat_check
        else:
            # quick and partial off-line checksum validation
            check_func = self.simple_vat_check
        for partner in self:
            if not partner.vat:
                continue
            #check with country code as prefix of the TIN
            vat_country, vat_number = self._split_vat(partner.vat)
            if not check_func(vat_country, vat_number):
                #if fails, check with country code from country
                country_code = partner.commercial_partner_id.country_id.code
                if country_code:
                    if not check_func(country_code.lower(), partner.vat):
                        pass
                        #msg = partner._construct_constraint_msg(country_code.lower())
                        #raise ValidationError(msg)
    
