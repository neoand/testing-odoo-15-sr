# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ChatroomRoom(models.Model):
    _inherit = 'chatroom.room'

    phone_blacklisted = fields.Boolean(
        string='Em Blacklist',
        default=False,
        help='Indica se o número está na blacklist da Kolmeya (não pode receber SMS)'
    )
    phone_not_disturb = fields.Boolean(
        string='Não Perturbe (SP)',
        default=False,
        help='Indica se o número está cadastrado no "Não Perturbe" (São Paulo)'
    )
    phone_status_checked_at = fields.Datetime(
        string='Status Checado Em',
        help='Data e hora da última verificação de status do telefone'
    )
    sms_count_sent = fields.Integer(
        string='SMS Enviados',
        compute='_compute_sms_stats',
        help='Total de SMS enviados para este número'
    )
    sms_count_delivered = fields.Integer(
        string='SMS Entregues',
        compute='_compute_sms_stats',
        help='Total de SMS entregues para este número'
    )

    @api.depends('phone')
    def _compute_sms_stats(self):
        """Calcula estatísticas de SMS a partir do log"""
        for room in self:
            if room.phone:
                # Conta SMS enviados
                room.sms_count_sent = self.env['chatroom.sms.log'].search_count([
                    ('room_id', '=', room.id),
                    ('status', 'in', ['sent', 'delivered'])
                ])

                # Conta SMS entregues
                room.sms_count_delivered = self.env['chatroom.sms.log'].search_count([
                    ('room_id', '=', room.id),
                    ('status', '=', 'delivered')
                ])
            else:
                room.sms_count_sent = 0
                room.sms_count_delivered = 0

    def add_to_blacklist(self, document=None):
        """Adiciona o número à blacklist da Kolmeya"""
        self.ensure_one()

        if not self.phone:
            raise UserError(_('Este contato não possui um número de telefone cadastrado.'))

        if self.phone_blacklisted:
            raise UserError(_('Este número já está na blacklist.'))

        try:
            # Busca a API SMS ativa
            api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
            if not api:
                raise UserError(_('Nenhuma API SMS configurada.'))

            import requests

            url = f"{api.base_url}/v1/sms/blacklist"
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'phone': self.phone,
            }

            if document:
                payload['document'] = document

            _logger.info(f"Adicionando número à blacklist: {self.phone}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            # Atualiza o registro
            self.write({
                'phone_blacklisted': True,
                'phone_status_checked_at': fields.Datetime.now()
            })

            _logger.info(f"Número {self.phone} adicionado à blacklist com sucesso")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sucesso'),
                    'message': _('Número adicionado à blacklist com sucesso.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erro ao adicionar à blacklist: {str(e)}")
            raise UserError(_('Erro ao adicionar à blacklist: %s') % str(e))

    def remove_from_blacklist(self):
        """Remove o número da blacklist da Kolmeya"""
        self.ensure_one()

        if not self.phone:
            raise UserError(_('Este contato não possui um número de telefone cadastrado.'))

        if not self.phone_blacklisted:
            raise UserError(_('Este número não está na blacklist.'))

        try:
            # Busca a API SMS ativa
            api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
            if not api:
                raise UserError(_('Nenhuma API SMS configurada.'))

            import requests

            url = f"{api.base_url}/v1/sms/blacklist/{self.phone}"
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }

            _logger.info(f"Removendo número da blacklist: {self.phone}")
            response = requests.delete(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Atualiza o registro
            self.write({
                'phone_blacklisted': False,
                'phone_status_checked_at': fields.Datetime.now()
            })

            _logger.info(f"Número {self.phone} removido da blacklist com sucesso")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sucesso'),
                    'message': _('Número removido da blacklist com sucesso.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erro ao remover da blacklist: {str(e)}")
            raise UserError(_('Erro ao remover da blacklist: %s') % str(e))

    def can_send_sms(self):
        """Verifica se pode enviar SMS para este número"""
        self.ensure_one()

        if not self.phone:
            return (False, _('Número de telefone não cadastrado'))

        if self.phone_blacklisted:
            return (False, _('Número está na blacklist'))

        if self.phone_not_disturb:
            return (
                False,
                _('Número cadastrado no "Não Perturbe" (SP). '
                  'Não é permitido enviar SMS de marketing.')
            )

        # Verifica se tem saldo na API
        api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
        if not api:
            return (False, _('Nenhuma API SMS configurada'))

        if api.balance and api.balance <= 0:
            return (False, _('Saldo insuficiente na API SMS'))

        return (True, _('OK'))

    def action_check_phone_status(self):
        """Verifica o status do telefone na API (blacklist, não perturbe, etc)"""
        self.ensure_one()

        if not self.phone:
            raise UserError(_('Este contato não possui um número de telefone cadastrado.'))

        try:
            # Busca a API SMS ativa
            api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
            if not api:
                raise UserError(_('Nenhuma API SMS configurada.'))

            import requests

            url = f"{api.base_url}/v1/sms/phone/status/{self.phone}"
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }

            _logger.info(f"Verificando status do telefone: {self.phone}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Atualiza os campos
            self.write({
                'phone_blacklisted': data.get('blacklisted', False),
                'phone_not_disturb': data.get('not_disturb', False),
                'phone_status_checked_at': fields.Datetime.now()
            })

            status_message = _('Status do telefone atualizado:\n')
            if data.get('blacklisted'):
                status_message += _('- Em blacklist: Sim\n')
            else:
                status_message += _('- Em blacklist: Não\n')

            if data.get('not_disturb'):
                status_message += _('- Não Perturbe (SP): Sim\n')
            else:
                status_message += _('- Não Perturbe (SP): Não\n')

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Status Atualizado'),
                    'message': status_message,
                    'type': 'info',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erro ao verificar status do telefone: {str(e)}")
            raise UserError(_('Erro ao verificar status: %s') % str(e))

    def action_view_sms_logs(self):
        """Abre a visualização dos logs de SMS enviados para este número"""
        self.ensure_one()

        return {
            'name': _('Logs de SMS'),
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.log',
            'view_mode': 'tree,form',
            'domain': [('room_id', '=', self.id)],
            'context': {'default_room_id': self.id},
        }
