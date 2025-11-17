# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import requests

_logger = logging.getLogger(__name__)


class ChatroomSendBulkSms(models.TransientModel):
    _name = 'chatroom.send.bulk.sms'
    _description = 'Envio de SMS em Massa'

    # Campos principais
    room_ids = fields.Many2many(
        'chatroom.room',
        string='Salas Selecionadas',
        required=True,
        help='Salas que receberão o SMS em massa'
    )
    template_id = fields.Many2one(
        'chatroom.sms.template',
        string='Template',
        help='Template de mensagem a ser utilizado'
    )
    message = fields.Text(
        string='Mensagem',
        required=True,
        help='Mensagem que será enviada para todas as salas'
    )
    segment_id = fields.Many2one(
        'chatroom.sms.segment',
        string='Centro de Custo',
        help='Centro de custo/segmento para contabilização'
    )

    # Opções de envio
    test_mode = fields.Boolean(
        string='Modo Teste (5 contatos)',
        default=False,
        help='Envia apenas para os 5 primeiros contatos como teste'
    )
    skip_blacklist = fields.Boolean(
        string='Pular Blacklist',
        default=True,
        help='Não envia para números que estão na blacklist'
    )
    skip_not_disturb = fields.Boolean(
        string='Pular Não Perturbe',
        default=True,
        help='Não envia para números cadastrados no "Não Perturbe" (SP)'
    )
    schedule_send = fields.Boolean(
        string='Agendar Envio',
        default=False,
        help='Agenda o envio para uma data/hora específica'
    )
    scheduled_date = fields.Datetime(
        string='Data/Hora de Envio',
        help='Data e hora em que os SMS serão enviados'
    )

    # Campos computados - Estatísticas
    total_rooms = fields.Integer(
        string='Total Salas',
        compute='_compute_totals',
        help='Total de salas selecionadas'
    )
    valid_rooms = fields.Integer(
        string='Válidos para Envio',
        compute='_compute_totals',
        help='Número de salas válidas para envio (sem blacklist, etc)'
    )
    estimated_cost = fields.Float(
        string='Custo Estimado (R$)',
        compute='_compute_totals',
        digits=(10, 2),
        help='Custo estimado do envio em lote'
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Preenche a mensagem quando um template é selecionado"""
        if self.template_id:
            # Preenche com valores de exemplo
            sample_values = {
                'nome': '[Nome do Contato]',
                'telefone': '[Telefone]',
                'data': fields.Date.today().strftime('%d/%m/%Y'),
                'hora': fields.Datetime.now().strftime('%H:%M'),
                'empresa': self.env.company.name or '[Nome da Empresa]',
            }
            self.message = self.template_id.apply_template(sample_values)

    @api.onchange('room_ids', 'skip_blacklist', 'skip_not_disturb')
    def _onchange_room_filters(self):
        """Recalcula totais quando os filtros mudam"""
        self._compute_totals()

    @api.depends('room_ids', 'skip_blacklist', 'skip_not_disturb', 'message', 'test_mode')
    def _compute_totals(self):
        """Calcula estatísticas de envio"""
        for wizard in self:
            wizard.total_rooms = len(wizard.room_ids)

            if not wizard.room_ids:
                wizard.valid_rooms = 0
                wizard.estimated_cost = 0.0
                continue

            # Filtra salas válidas
            valid_rooms = wizard.room_ids

            # Filtra por telefone
            valid_rooms = valid_rooms.filtered(lambda r: r.phone)

            # Filtra blacklist
            if wizard.skip_blacklist:
                valid_rooms = valid_rooms.filtered(lambda r: not r.phone_blacklisted)

            # Filtra não perturbe
            if wizard.skip_not_disturb:
                valid_rooms = valid_rooms.filtered(lambda r: not r.phone_not_disturb)

            # Se modo teste, limita a 5
            if wizard.test_mode:
                valid_rooms = valid_rooms[:5]

            wizard.valid_rooms = len(valid_rooms)

            # Calcula custo estimado (assumindo R$ 0.10 por SMS)
            # Calcula número de partes SMS
            message_length = len(wizard.message) if wizard.message else 0
            if message_length <= 160:
                sms_parts = 1
            else:
                # Mensagens concatenadas usam 153 caracteres por parte
                sms_parts = (message_length + 152) // 153

            cost_per_sms = 0.10  # R$ 0.10 por SMS
            wizard.estimated_cost = wizard.valid_rooms * sms_parts * cost_per_sms

    @api.constrains('scheduled_date', 'schedule_send')
    def _check_scheduled_date(self):
        """Valida a data de agendamento"""
        for wizard in self:
            if wizard.schedule_send:
                if not wizard.scheduled_date:
                    raise ValidationError(
                        _('Você deve informar a data/hora de envio quando agendar o envio!')
                    )
                if wizard.scheduled_date < fields.Datetime.now():
                    raise ValidationError(
                        _('A data de agendamento não pode ser no passado!')
                    )

    def _get_valid_rooms(self):
        """Retorna as salas válidas para envio"""
        self.ensure_one()

        valid_rooms = self.room_ids

        # Filtra por telefone
        valid_rooms = valid_rooms.filtered(lambda r: r.phone)

        # Filtra blacklist
        if self.skip_blacklist:
            valid_rooms = valid_rooms.filtered(lambda r: not r.phone_blacklisted)

        # Filtra não perturbe
        if self.skip_not_disturb:
            valid_rooms = valid_rooms.filtered(lambda r: not r.phone_not_disturb)

        # Se modo teste, limita a 5
        if self.test_mode:
            valid_rooms = valid_rooms[:5]

        return valid_rooms

    def send_bulk_sms(self):
        """Método principal que envia SMS em lotes"""
        self.ensure_one()

        if not self.message:
            raise UserError(_('A mensagem não pode estar vazia!'))

        # Se for agendamento, cria registros agendados
        if self.schedule_send:
            return self._create_scheduled_sms()

        # Busca a API SMS ativa
        api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
        if not api:
            raise UserError(_('Nenhuma API SMS configurada.'))

        # Verifica saldo
        if hasattr(api, 'balance') and api.balance and api.balance <= 0:
            raise UserError(_('Saldo insuficiente na API SMS.'))

        # Obtém salas válidas
        valid_rooms = self._get_valid_rooms()

        if not valid_rooms:
            raise UserError(_('Nenhuma sala válida para envio!'))

        _logger.info(
            f"Iniciando envio em massa de SMS para {len(valid_rooms)} salas"
        )

        # Envia em lotes de 1000
        batch_size = 1000
        total_sent = 0
        total_failed = 0
        results = []

        for i in range(0, len(valid_rooms), batch_size):
            batch = valid_rooms[i:i + batch_size]
            _logger.info(f"Processando lote {i // batch_size + 1}: {len(batch)} SMS")

            batch_result = self._send_batch(batch, api)
            results.extend(batch_result)

            total_sent += sum(1 for r in batch_result if r.get('success'))
            total_failed += sum(1 for r in batch_result if not r.get('success'))

        # Cria logs dos envios
        self._create_log_entries(results, valid_rooms)

        # Atualiza saldo da API
        if hasattr(api, 'update_balance'):
            try:
                api.update_balance()
            except Exception as e:
                _logger.warning(f"Não foi possível atualizar saldo: {str(e)}")

        _logger.info(
            f"Envio em massa concluído. Enviados: {total_sent}, Falhados: {total_failed}"
        )

        # Retorna resultado
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Envio Concluído'),
                'message': _(
                    'SMS enviados: %d\n'
                    'Falhas: %d\n'
                    'Total: %d'
                ) % (total_sent, total_failed, len(valid_rooms)),
                'type': 'success' if total_failed == 0 else 'warning',
                'sticky': True,
            }
        }

    def _send_batch(self, rooms, api):
        """Envia um lote de SMS"""
        results = []

        for room in rooms:
            try:
                # Prepara a mensagem com variáveis
                message = self._prepare_message(room)

                # Chama a API para enviar
                result = self._send_single_sms(room, message, api)
                results.append({
                    'room_id': room.id,
                    'phone': room.phone,
                    'message': message,
                    'success': result.get('success', False),
                    'request_id': result.get('request_id'),
                    'message_id': result.get('message_id'),
                    'error': result.get('error'),
                    'status_code': result.get('status_code'),
                })

            except Exception as e:
                _logger.error(f"Erro ao enviar SMS para {room.phone}: {str(e)}")
                results.append({
                    'room_id': room.id,
                    'phone': room.phone,
                    'message': self.message,
                    'success': False,
                    'error': str(e),
                })

        return results

    def _prepare_message(self, room):
        """Prepara a mensagem substituindo variáveis"""
        message = self.message

        # Substitui variáveis comuns
        replacements = {
            '{nome}': room.name or '',
            '{telefone}': room.phone or '',
            '{data}': fields.Date.today().strftime('%d/%m/%Y'),
            '{hora}': fields.Datetime.now().strftime('%H:%M'),
            '{empresa}': self.env.company.name or '',
        }

        for key, value in replacements.items():
            message = message.replace(key, str(value))

        return message

    def _send_single_sms(self, room, message, api):
        """Envia um único SMS através da API"""
        if not api.api_key or not api.base_url:
            return {
                'success': False,
                'error': 'API não configurada corretamente'
            }

        try:
            url = f"{api.base_url.rstrip('/')}/v1/sms/send"
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'phone': room.phone,
                'message': message,
            }

            # Adiciona segment_id se informado
            if self.segment_id and self.segment_id.kolmeya_id:
                payload['segment_id'] = self.segment_id.kolmeya_id

            # Adiciona referência
            payload['reference'] = f'bulk_{self.id}_{room.id}'

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code in (200, 201):
                data = response.json()
                return {
                    'success': True,
                    'request_id': data.get('request_id'),
                    'message_id': data.get('message_id'),
                    'status_code': response.status_code,
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code,
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _create_log_entries(self, results, rooms):
        """Cria entradas de log para os envios"""
        SmsLog = self.env['chatroom.sms.log']

        for result in results:
            try:
                log_vals = {
                    'room_id': result.get('room_id'),
                    'phone': result.get('phone'),
                    'message': result.get('message'),
                    'segment_id': self.segment_id.id if self.segment_id else False,
                    'status': 'sent' if result.get('success') else 'failed',
                    'request_id': result.get('request_id'),
                    'message_id': result.get('message_id'),
                    'status_code': result.get('status_code'),
                    'reference': f'bulk_{self.id}',
                }

                if result.get('success'):
                    log_vals['sent_at'] = fields.Datetime.now()
                else:
                    log_vals['error_message'] = result.get('error', 'Erro desconhecido')

                SmsLog.create(log_vals)

            except Exception as e:
                _logger.error(f"Erro ao criar log para {result.get('phone')}: {str(e)}")

    def _create_scheduled_sms(self):
        """Cria registros de SMS agendados"""
        self.ensure_one()

        valid_rooms = self._get_valid_rooms()

        if not valid_rooms:
            raise UserError(_('Nenhuma sala válida para agendamento!'))

        ScheduledSms = self.env['chatroom.sms.scheduled']
        created_count = 0

        for room in valid_rooms:
            try:
                # Prepara a mensagem
                message = self._prepare_message(room)

                # Cria o agendamento
                ScheduledSms.create({
                    'name': f'Envio em massa - {room.name}',
                    'room_id': room.id,
                    'template_id': self.template_id.id if self.template_id else False,
                    'message': message,
                    'scheduled_date': self.scheduled_date,
                    'state': 'scheduled',
                })
                created_count += 1

            except Exception as e:
                _logger.error(f"Erro ao agendar SMS para {room.phone}: {str(e)}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Agendamento Concluído'),
                'message': _(
                    '%d SMS agendados para %s'
                ) % (created_count, self.scheduled_date.strftime('%d/%m/%Y %H:%M')),
                'type': 'success',
                'sticky': True,
            }
        }

    def action_preview(self):
        """Preview da mensagem antes de enviar"""
        self.ensure_one()

        if not self.room_ids:
            raise UserError(_('Selecione ao menos uma sala para preview.'))

        # Pega a primeira sala como exemplo
        sample_room = self.room_ids[0]
        preview_message = self._prepare_message(sample_room)

        message = _(
            'Preview da Mensagem:\n\n'
            '━━━━━━━━━━━━━━━━━━━━\n'
            '%s\n'
            '━━━━━━━━━━━━━━━━━━━━\n\n'
            'Exemplo de contato: %s\n'
            'Telefone: %s\n\n'
            'Total de salas selecionadas: %d\n'
            'Salas válidas para envio: %d\n'
            'Custo estimado: R$ %.2f'
        ) % (
            preview_message,
            sample_room.name,
            sample_room.phone,
            self.total_rooms,
            self.valid_rooms,
            self.estimated_cost
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Preview do Envio em Massa'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
