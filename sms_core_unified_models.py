# -*- coding: utf-8 -*-
"""
SMS Message Model - UNIFIED VERSION (Para criação no servidor)
==================================

CRITICAL FIX: Resolves action_send() method conflict between:
- sms_base_sr/models/sms_message.py (action_send() original)
- chatroom_sms_advanced/models/sms_message_advanced.py (action_send() override)

Este é o conteúdo para o arquivo /odoo/custom/addons_custom/sms_core_unified/models/sms_message.py
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


class SMSMessage(models.Model):
    """
    UNIFIED SMS Message Model

    Este model RESOLVE o CONFLITO CRÍTICO do método action_send() unificando:
    1. Funcionalidade do sms_base_sr
    2. Funcionalidade do chatroom_sms_advanced (blacklist + cost)
    3. Enhanced error handling
    4. Single source of truth
    """

    _name = 'sms.message'  # Mesmo nome - migração transparente
    _description = 'Unified SMS Message - Resolves action_send() conflicts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date DESC, id DESC'
    _rec_name = 'phone'

    # ========== CAMPOS DO CORE (sms_base_sr) ==========
    phone = fields.Char(string='Phone Number', required=True, tracking=True)
    body = fields.Text(string='Message', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('error', 'Error'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', tracking=True, index=True)

    partner_id = fields.Many2one('res.partner', string='Contact', index=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Responsible User', default=lambda self: self.env.user, tracking=True)
    provider_id = fields.Many2one('sms.provider', string='SMS Provider', required=True, tracking=True)
    template_id = fields.Many2one('sms.template', string='Template')

    # ========== CAMPOS AVANÇADOS (chatroom_sms_advanced) ==========
    campaign_id = fields.Many2one('sms.campaign', string='Campaign', ondelete='set null', index=True)
    scheduled_id = fields.Many2one('sms.scheduled', string='Scheduled Send', ondelete='set null')
    cost = fields.Float(string='Cost', digits=(10, 2), help='SMS cost calculation')
    segments = fields.Integer(string='Message Segments', help='Number of SMS segments (160 chars each)')

    # ========== CAMPOS ORIGINAIS ==========
    sent_date = fields.Datetime(string='Sent Date', readonly=True)
    delivery_date = fields.Datetime(string='Delivery Date', readonly=True)
    error_message = fields.Text(string='Error Message', readonly=True)
    retry_count = fields.Integer(string='Retry Count', default=0)
    external_id = fields.Char(string='External ID', readonly=True)

    # ========== MÉTODO action_send() UNIFICADO - CONFLITO RESOLVIDO! ==========
    def action_send(self):
        """
        MÉTODO UNIFICADO - RESOLVE CONFLITO CRÍTICO!

        Combina funcionalidade de:
        - sms_base_sr: Envio básico + lógica de provider
        - chatroom_sms_advanced: Verificação blacklist + cálculo custo

        FIM DOS CONFLITOS DE OVERRIDE!
        """
        self.ensure_one()

        _logger.info(f'🚀 SMS Unified action_send() chamado para SMS {self.id}')

        try:
            # Validação de estado
            if self.state not in ['draft', 'error']:
                raise UserError(_('Apenas SMS rascunho ou com erro podem ser enviados.'))

            # Validação de provider
            if not self.provider_id:
                raise UserError(_('Nenhum provider SMS configurado.'))

            # VERIFICAÇÃO BLACKLIST (do chatroom_sms_advanced)
            if self.phone:
                blacklisted = self.env['sms.blacklist'].search([
                    ('phone', '=', self.phone),
                    ('active', '=', True)
                ], limit=1)

                if blacklisted:
                    error_msg = _('Número bloqueado: %s') % blacklisted.reason
                    _logger.warning(f'SMS para {self.phone} BLOQUEADO - blacklist: {blacklisted.reason}')

                    self.write({
                        'state': 'error',
                        'error_message': error_msg,
                    })

                    return {'type': 'ir.actions.client', 'tag': 'display_notification',
                           'params': {'title': _('SMS Bloqueado'), 'message': error_msg, 'type': 'warning'}}

            # CÁLCULO DE CUSTO (do chatroom_sms_advanced)
            if not self.cost and self.body:
                self._calculate_cost()

            # ENVIO VIA PROVIDER (do sms_base_sr - unificado)
            _logger.info(f'Enviando SMS {self.id} via provider {self.provider_id.name}')

            self.write({
                'state': 'outgoing',
                'sent_date': fields.Datetime.now()
            })

            # Chamada unificada ao provider
            result = self.provider_id._send_sms_unified(self)

            if result.get('success'):
                self.write({
                    'state': 'sent',
                    'external_id': result.get('external_id'),
                    'error_message': False
                })

                _logger.info(f'✅ SMS {self.id} enviado com sucesso')

            else:
                error_msg = result.get('error', 'Erro desconhecido')
                self.write({
                    'state': 'error',
                    'error_message': error_msg,
                    'retry_count': self.retry_count + 1
                })

                _logger.error(f'❌ SMS {self.id} falhou: {error_msg}')
                raise UserError(_('Falha ao enviar SMS: %s') % error_msg)

        except Exception as e:
            _logger.exception(f'Exceção enviando SMS {self.id}: {str(e)}')

            self.write({
                'state': 'error',
                'error_message': str(e),
                'retry_count': self.retry_count + 1
            })

            raise

    def _calculate_cost(self):
        """Calcular custo SMS (do chatroom_sms_advanced)"""
        if self.body:
            char_count = len(self.body)
            self.segments = (char_count // 160) + (1 if char_count % 160 else 0)
            self.cost = self.segments * 0.10
        else:
            self.segments = 0
            self.cost = 0.0

    def action_cancel(self):
        """Cancelar SMS"""
        self.filtered(lambda s: s.state in ['draft', 'outgoing']).write({'state': 'canceled'})

    def action_reset_to_draft(self):
        """Resetar para rascunho"""
        self.filtered(lambda s: s.state != 'draft').write({
            'state': 'draft',
            'error_message': False,
            'retry_count': 0
        })