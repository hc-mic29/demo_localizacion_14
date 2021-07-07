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

    @api.depends('posted_before', 'state', 'journal_aux_id', 'date')
    def _compute_name(self):
        def journal_key(move):
            return (move.journal_aux_id, move.journal_aux_id.refund_sequence and move.move_type)

        def date_key(move):
            return (move.date.year, move.date.month)

        grouped = defaultdict(  # key: journal_id, move_type
            lambda: defaultdict(  # key: first adjacent (date.year, date.month)
                lambda: {
                    'records': self.env['account.move'],
                    'format': False,
                    'format_values': False,
                    'reset': False
                }
            )
        )
        self = self.sorted(lambda m: (m.date, m.ref or '', m.id))
        highest_name = self[0]._get_last_sequence() if self else False

        # Group the moves by journal and month
        for move in self:
            if not highest_name and move == self[0] and not move.posted_before:
                # In the form view, we need to compute a default sequence so that the user can edit
                # it. We only check the first move as an approximation (enough for new in form view)
                pass
            elif (move.name and move.name != '/') or move.state != 'posted':
                # Has already a name or is not posted, we don't add to a batch
                continue
            group = grouped[journal_key(move)][date_key(move)]
            if not group['records']:
                # Compute all the values needed to sequence this whole group
                move._set_next_sequence()
                group['format'], group['format_values'] = move._get_sequence_format_param(move.name)
                group['reset'] = move._deduce_sequence_number_reset(move.name)
            group['records'] += move

        # Fusion the groups depending on the sequence reset and the format used because `seq` is
        # the same counter for multiple groups that might be spread in multiple months.
        final_batches = []
        for journal_group in grouped.values():
            for date_group in journal_group.values():
                if not final_batches or final_batches[-1]['format'] != date_group['format']:
                    final_batches += [date_group]
                elif date_group['reset'] == 'never':
                    final_batches[-1]['records'] += date_group['records']
                elif (
                    date_group['reset'] == 'year'
                    and final_batches[-1]['records'][0].date.year == date_group['records'][0].date.year
                ):
                    final_batches[-1]['records'] += date_group['records']
                else:
                    final_batches += [date_group]

        # Give the name based on previously computed values
        for batch in final_batches:
            for move in batch['records']:
                move.name = batch['format'].format(**batch['format_values'])
                batch['format_values']['seq'] += 1
            batch['records']._compute_split_sequence()

        self.filtered(lambda m: not m.name).name = '/'