# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict


_logger = logging.getLogger('__name__')

class AccountMove(models.Model):
    _inherit = 'account.move'

    journal_aux_id = fields.Many2one('account.journal', string='Diario Aux',compute='_compute_invoice_filter_type_doc')   

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True)

    @api.depends('type')
    def _compute_invoice_filter_type_doc(self):

        ejecuta="no"
        if self.type=="in_invoice":
            tipo_doc="fc"
            typo="purchase"
            ejecuta="si"
        if self.type=="in_refund":
            tipo_doc="nc"
            typo="purchase"
            ejecuta="si"
        if self.type=="in_receipt":
            tipo_doc="nb"
            typo="purchase"
            ejecuta="si"

        if self.type=="out_invoice":
            tipo_doc="fc"
            typo="sale"
            ejecuta="si"
        if self.type=="out_refund":
            tipo_doc="nc"
            typo="sale"
            ejecuta="si"
        if self.type=="out_receipt":
            tipo_doc="nb"
            typo="sale"
            ejecuta="si"
        
        if ejecuta=="si":
            busca_diarios = self.env['account.journal'].search([('tipo_doc','=',tipo_doc),('type','=',typo)])
            for det in busca_diarios:
                file=det.id
            self.journal_aux_id=file
            self.journal_id=file
        else:
            busca_diarios = self.env['account.journal'].search([('type','=','general')])
            for det in busca_diarios:
                file=det.id
            self.journal_aux_id=file
        #self.invoice_filter_type_doc= file

   