# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import requests
import re

_logger = logging.getLogger(__name__)


class ChatroomSmsTest(models.TransientModel):
    _name = 'chatroom.sms.test'
    _description = 'Teste de Envio de SMS'

    # Campos principais
    phone = fields.Char(
        string='Telefone de Teste',
        required=True,
        help='Número de telefone para enviar o SMS de teste (com código do país)'
    )
    message = fields.Text(
        string='Mensagem de Teste',
        required=True,
        default='Teste de SMS do Odoo',
        help='Mensagem que será enviada no teste'
    )
    api_id = fields.Many2one(
        'chatroom.sms.api',
        string='API SMS',
        required=True,
        domain=[('active', '=', True)],
        help='API que será utilizada para o teste'
    )

    # Campos de resultado
    result = fields.Text(
        string='Resultado',
        readonly=True,
        help='Resultado do teste de envio'
    )
    state = fields.Selection(
        [
            ('draft', 'Rascunho'),
            ('sent', 'Enviado'),
            ('error', 'Erro')
        ],
        string='Status',
        default='draft',
        required=True
    )

    # Campos auxiliares
    request_id = fields.Char(
        string='Request ID',
        readonly=True,
        help='ID da requisição retornado pela API'
    )
    message_id = fields.Char(
        string='Message ID',
        readonly=True,
        help='ID da mensagem retornado pela API'
    )
    status_code = fields.Integer(
        string='Código HTTP',
        readonly=True,
        help='Código de status HTTP da resposta'
    )

    @api.model
    def default_get(self, fields_list):
        """Define valores padrão"""
        res = super(ChatroomSmsTest, self).default_get(fields_list)

        # Seleciona automaticamente a primeira API ativa
        if 'api_id' in fields_list and not res.get('api_id'):
            api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
            if api:
                res['api_id'] = api.id

        return res

    @api.onchange('phone')
    def _onchange_phone(self):
        """Valida e formata o telefone"""
        if self.phone:
            # Remove caracteres não numéricos
            phone = re.sub(r'\D', '', self.phone)

            # Verifica se começa com código do país
            if not phone.startswith('55') and len(phone) == 11:
                phone = '55' + phone
                self.phone = phone

            # Valida tamanho
            if len(phone) < 12 or len(phone) > 13:
                return {
                    'warning': {
                        'title': _('Telefone Inválido'),
                        'message': _(
                            'O telefone deve ter o formato: 5511999999999\n'
                            '(código país + DDD + número)'
                        )
                    }
                }

    @api.constrains('phone')
    def _check_phone(self):
        """Valida o formato do telefone"""
        for record in self:
            if record.phone:
                # Remove caracteres não numéricos
                phone = re.sub(r'\D', '', record.phone)

                if len(phone) < 12 or len(phone) > 13:
                    raise ValidationError(
                        _('O telefone deve ter entre 12 e 13 dígitos (com código do país)')
                    )

    def action_send_test(self):
        """Envia o SMS de teste"""
        self.ensure_one()

        if not self.api_id:
            raise UserError(_('Selecione uma API SMS para o teste.'))

        if not self.api_id.api_key or not self.api_id.base_url:
            raise UserError(_('A API selecionada não está configurada corretamente.'))

        # Limpa telefone
        phone = re.sub(r'\D', '', self.phone)

        _logger.info(f"Enviando SMS de teste para {phone}")

        try:
            # Monta a requisição
            url = f"{self.api_id.base_url.rstrip('/')}/v1/sms/send"
            headers = {
                'Authorization': f'Bearer {self.api_id.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'phone': phone,
                'message': self.message,
                'reference': f'test_{self.id}_{fields.Datetime.now().timestamp()}'
            }

            # Envia a requisição
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            # Processa resposta
            self.status_code = response.status_code

            if response.status_code in (200, 201):
                data = response.json()

                self.write({
                    'state': 'sent',
                    'request_id': data.get('request_id', ''),
                    'message_id': data.get('message_id', ''),
                    'result': _(
                        'SMS enviado com sucesso!\n\n'
                        'Request ID: %s\n'
                        'Message ID: %s\n'
                        'Status HTTP: %s\n'
                        'Telefone: %s\n'
                        'Mensagem: %s\n\n'
                        'Resposta completa:\n%s'
                    ) % (
                        data.get('request_id', 'N/A'),
                        data.get('message_id', 'N/A'),
                        response.status_code,
                        phone,
                        self.message,
                        response.text
                    )
                })

                _logger.info(f"SMS de teste enviado com sucesso. Request ID: {data.get('request_id')}")

                # Cria log do envio
                self._create_test_log(phone, data, success=True)

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Sucesso!'),
                        'message': _(
                            'SMS de teste enviado com sucesso!\n'
                            'Request ID: %s'
                        ) % data.get('request_id', 'N/A'),
                        'type': 'success',
                        'sticky': True,
                    }
                }

            else:
                error_message = _(
                    'Erro ao enviar SMS de teste!\n\n'
                    'Status HTTP: %s\n'
                    'Telefone: %s\n'
                    'Mensagem: %s\n\n'
                    'Resposta da API:\n%s'
                ) % (
                    response.status_code,
                    phone,
                    self.message,
                    response.text
                )

                self.write({
                    'state': 'error',
                    'result': error_message
                })

                _logger.error(f"Erro ao enviar SMS de teste: {response.text}")

                # Cria log do envio
                self._create_test_log(phone, {'error': response.text}, success=False)

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Erro ao Enviar'),
                        'message': _(
                            'Erro HTTP %s\n%s'
                        ) % (response.status_code, response.text[:200]),
                        'type': 'danger',
                        'sticky': True,
                    }
                }

        except requests.exceptions.Timeout:
            error_message = _('Timeout: A API não respondeu em 30 segundos.')
            self._handle_test_error(phone, error_message)
            raise UserError(error_message)

        except requests.exceptions.ConnectionError as e:
            error_message = _('Erro de conexão: Não foi possível conectar à API.\n%s') % str(e)
            self._handle_test_error(phone, error_message)
            raise UserError(error_message)

        except requests.exceptions.RequestException as e:
            error_message = _('Erro na requisição: %s') % str(e)
            self._handle_test_error(phone, error_message)
            raise UserError(error_message)

        except Exception as e:
            error_message = _('Erro inesperado: %s') % str(e)
            self._handle_test_error(phone, error_message)
            _logger.exception("Erro inesperado ao enviar SMS de teste")
            raise UserError(error_message)

    def _handle_test_error(self, phone, error_message):
        """Trata erros no envio de teste"""
        self.write({
            'state': 'error',
            'result': error_message
        })
        _logger.error(f"Erro ao enviar SMS de teste para {phone}: {error_message}")

    def _create_test_log(self, phone, response_data, success=True):
        """Cria um log do teste"""
        try:
            log_vals = {
                'phone': phone,
                'message': self.message,
                'status': 'sent' if success else 'failed',
                'request_id': response_data.get('request_id'),
                'message_id': response_data.get('message_id'),
                'reference': f'test_{self.id}',
                'status_code': self.status_code,
            }

            if success:
                log_vals['sent_at'] = fields.Datetime.now()
                log_vals['status_message'] = 'Teste de SMS enviado com sucesso'
            else:
                log_vals['error_message'] = response_data.get('error', 'Erro desconhecido')

            self.env['chatroom.sms.log'].create(log_vals)

        except Exception as e:
            _logger.warning(f"Não foi possível criar log do teste: {str(e)}")

    def action_check_balance(self):
        """Verifica o saldo da API"""
        self.ensure_one()

        if not self.api_id:
            raise UserError(_('Selecione uma API SMS.'))

        try:
            # Tenta atualizar o saldo
            if hasattr(self.api_id, 'update_balance'):
                self.api_id.update_balance()

                balance = self.api_id.balance if hasattr(self.api_id, 'balance') else 0
                last_update = self.api_id.balance_last_update if hasattr(self.api_id, 'balance_last_update') else None

                message = _(
                    'Saldo Atual: R$ %.2f\n'
                    'Última atualização: %s\n'
                    'API: %s'
                ) % (
                    balance,
                    last_update.strftime('%d/%m/%Y %H:%M:%S') if last_update else 'N/A',
                    self.api_id.name
                )

                self.result = message

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Saldo da API'),
                        'message': message,
                        'type': 'info',
                        'sticky': True,
                    }
                }
            else:
                raise UserError(_('A API selecionada não suporta consulta de saldo.'))

        except Exception as e:
            _logger.error(f"Erro ao verificar saldo: {str(e)}")
            raise UserError(_('Erro ao verificar saldo: %s') % str(e))

    def action_test_webhook(self):
        """Testa se o webhook está acessível"""
        self.ensure_one()

        if not self.api_id:
            raise UserError(_('Selecione uma API SMS.'))

        webhook_url = self.api_id.webhook_url if hasattr(self.api_id, 'webhook_url') else None

        if not webhook_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Webhook não configurado'),
                    'message': _('A API selecionada não possui uma URL de webhook configurada.'),
                    'type': 'warning',
                    'sticky': True,
                }
            }

        try:
            # Tenta fazer uma requisição HEAD para verificar se o webhook está acessível
            response = requests.head(webhook_url, timeout=10)

            if response.status_code < 500:
                message = _(
                    'Webhook acessível!\n\n'
                    'URL: %s\n'
                    'Status HTTP: %s\n'
                    'O webhook está respondendo corretamente.'
                ) % (webhook_url, response.status_code)

                self.result = message

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Webhook OK'),
                        'message': message,
                        'type': 'success',
                        'sticky': True,
                    }
                }
            else:
                error_message = _(
                    'Webhook com erro!\n\n'
                    'URL: %s\n'
                    'Status HTTP: %s\n'
                    'O webhook não está acessível.'
                ) % (webhook_url, response.status_code)

                self.result = error_message

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Webhook com Erro'),
                        'message': error_message,
                        'type': 'warning',
                        'sticky': True,
                    }
                }

        except requests.exceptions.Timeout:
            error_message = _(
                'Timeout ao testar webhook!\n\n'
                'URL: %s\n'
                'O webhook não respondeu em 10 segundos.'
            ) % webhook_url

            self.result = error_message

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Timeout'),
                    'message': error_message,
                    'type': 'warning',
                    'sticky': True,
                }
            }

        except requests.exceptions.ConnectionError:
            error_message = _(
                'Erro de conexão!\n\n'
                'URL: %s\n'
                'Não foi possível conectar ao webhook.'
            ) % webhook_url

            self.result = error_message

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Erro de Conexão'),
                    'message': error_message,
                    'type': 'danger',
                    'sticky': True,
                }
            }

        except Exception as e:
            error_message = _('Erro ao testar webhook: %s') % str(e)
            self.result = error_message

            _logger.error(f"Erro ao testar webhook: {str(e)}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Erro'),
                    'message': error_message,
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_reset(self):
        """Reseta o wizard para fazer um novo teste"""
        self.ensure_one()

        self.write({
            'state': 'draft',
            'result': False,
            'request_id': False,
            'message_id': False,
            'status_code': False,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.test',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
