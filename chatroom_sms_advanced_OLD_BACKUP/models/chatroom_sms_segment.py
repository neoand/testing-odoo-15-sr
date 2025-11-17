# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import requests
import json

_logger = logging.getLogger(__name__)


class ChatroomSmsSegment(models.Model):
    _name = 'chatroom.sms.segment'
    _description = 'Segmento de SMS da Kolmeya'
    _order = 'name'

    name = fields.Char(
        string='Nome do Segmento',
        required=True,
        help='Nome do segmento de clientes'
    )
    kolmeya_id = fields.Integer(
        string='ID na Kolmeya',
        required=True,
        help='ID do segmento na plataforma Kolmeya'
    )
    description = fields.Text(
        string='Descrição',
        help='Descrição do segmento'
    )
    active = fields.Boolean(
        string='Ativo',
        default=True
    )

    # Campos auxiliares
    room_ids = fields.Many2many(
        'chatroom.room',
        'chatroom_segment_room_rel',
        'segment_id',
        'room_id',
        string='Salas',
        help='Salas associadas a este segmento'
    )
    room_count = fields.Integer(
        string='Quantidade de Salas',
        compute='_compute_room_count',
        store=False
    )
    last_sync = fields.Datetime(
        string='Última Sincronização',
        readonly=True,
        help='Data da última sincronização com a Kolmeya'
    )

    _sql_constraints = [
        ('kolmeya_id_unique', 'UNIQUE(kolmeya_id)', 'O ID da Kolmeya deve ser único!')
    ]

    @api.depends('room_ids')
    def _compute_room_count(self):
        """Calcula a quantidade de salas no segmento"""
        for record in self:
            record.room_count = len(record.room_ids)

    @api.model
    def sync_from_kolmeya(self):
        """
        Sincroniza os segmentos da API Kolmeya

        Busca todos os segmentos disponíveis na API e atualiza/cria
        os registros correspondentes no Odoo
        """
        _logger.info('Iniciando sincronização de segmentos da Kolmeya')

        # Busca a configuração da API
        sms_api = self.env['chatroom.sms.api'].search([
            ('active', '=', True)
        ], limit=1)

        if not sms_api:
            raise UserError(_('Nenhuma API de SMS está configurada!'))

        if not sms_api.api_key:
            raise UserError(_('API Key não configurada!'))

        try:
            # Endpoint para buscar segmentos (ajustar conforme documentação Kolmeya)
            url = '%s/segments' % sms_api.api_url.rstrip('/')

            headers = {
                'Authorization': 'Bearer %s' % sms_api.api_key,
                'Content-Type': 'application/json'
            }

            _logger.info('Buscando segmentos em: %s', url)

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                error_msg = 'Erro ao buscar segmentos: HTTP %s - %s' % (
                    response.status_code,
                    response.text
                )
                _logger.error(error_msg)
                raise UserError(_(error_msg))

            data = response.json()

            # Processa a resposta (ajustar conforme estrutura da API)
            segments_data = data.get('segments', []) or data.get('data', []) or []

            if not isinstance(segments_data, list):
                segments_data = [data]

            created_count = 0
            updated_count = 0

            for segment_info in segments_data:
                kolmeya_id = segment_info.get('id')
                name = segment_info.get('name') or segment_info.get('nome')
                description = segment_info.get('description') or segment_info.get('descricao', '')

                if not kolmeya_id or not name:
                    _logger.warning('Segmento sem ID ou nome, ignorando: %s', segment_info)
                    continue

                # Busca se o segmento já existe
                existing_segment = self.search([
                    ('kolmeya_id', '=', kolmeya_id)
                ], limit=1)

                values = {
                    'name': name,
                    'description': description,
                    'last_sync': fields.Datetime.now()
                }

                if existing_segment:
                    existing_segment.write(values)
                    updated_count += 1
                    _logger.info('Segmento atualizado: %s (ID: %s)', name, kolmeya_id)
                else:
                    values['kolmeya_id'] = kolmeya_id
                    self.create(values)
                    created_count += 1
                    _logger.info('Segmento criado: %s (ID: %s)', name, kolmeya_id)

            message = _('Sincronização concluída!\nCriados: %s\nAtualizados: %s\nTotal: %s') % (
                created_count,
                updated_count,
                created_count + updated_count
            )

            _logger.info(message)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sincronização Completa'),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            error_msg = 'Erro de conexão com a API Kolmeya: %s' % str(e)
            _logger.exception(error_msg)
            raise UserError(_(error_msg))

        except Exception as e:
            error_msg = 'Erro ao sincronizar segmentos: %s' % str(e)
            _logger.exception(error_msg)
            raise UserError(_(error_msg))

    def action_view_rooms(self):
        """Ação para visualizar as salas do segmento"""
        self.ensure_one()

        return {
            'name': _('Salas do Segmento: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.room',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.room_ids.ids)],
            'context': {'default_segment_id': self.id}
        }

    def action_sync_segment(self):
        """Ação para sincronizar um segmento específico"""
        return self.sync_from_kolmeya()
