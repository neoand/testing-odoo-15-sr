# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ChatroomSmsApi(models.Model):
    _inherit = 'chatroom.sms.api'

    balance = fields.Float(
        string='Saldo Disponível',
        readonly=True,
        help='Saldo atual na API Kolmeya'
    )
    balance_last_update = fields.Datetime(
        string='Última Atualização',
        readonly=True,
        help='Data e hora da última consulta de saldo'
    )
    balance_warning_threshold = fields.Float(
        string='Alertar Abaixo de',
        default=100.0,
        help='Valor mínimo para enviar alerta de saldo baixo'
    )
    webhook_url = fields.Char(
        string='URL do Webhook',
        help='URL para receber notificações de status dos SMS'
    )

    def update_balance(self):
        """Consulta o saldo na API Kolmeya e atualiza o registro"""
        self.ensure_one()

        if not self.api_key:
            raise UserError(_('API Key não configurada para esta API SMS'))

        try:
            import requests

            url = f"{self.base_url}/v1/sms/balance"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            _logger.info(f"Consultando saldo na API Kolmeya: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            balance = float(data.get('balance', 0))

            # Atualiza o saldo
            self.write({
                'balance': balance,
                'balance_last_update': fields.Datetime.now()
            })

            _logger.info(f"Saldo atualizado: R$ {balance:.2f}")

            # Verifica se precisa enviar notificação de saldo baixo
            if balance < self.balance_warning_threshold:
                self._send_low_balance_notification(balance)

            return True

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erro ao consultar saldo na API Kolmeya: {str(e)}")
            raise UserError(_('Erro ao consultar saldo: %s') % str(e))
        except Exception as e:
            _logger.error(f"Erro inesperado ao atualizar saldo: {str(e)}")
            raise UserError(_('Erro inesperado: %s') % str(e))

    def _send_low_balance_notification(self, balance):
        """Cria uma atividade para o administrador quando o saldo está baixo"""
        self.ensure_one()

        try:
            # Busca o usuário administrador
            admin_user = self.env.ref('base.user_admin')

            # Cria a atividade
            activity_type = self.env.ref('mail.mail_activity_data_warning', raise_if_not_found=False)
            if not activity_type:
                activity_type = self.env['mail.activity.type'].search([('name', '=', 'To Do')], limit=1)

            self.env['mail.activity'].create({
                'activity_type_id': activity_type.id if activity_type else False,
                'res_id': self.id,
                'res_model_id': self.env['ir.model']._get('chatroom.sms.api').id,
                'user_id': admin_user.id,
                'summary': _('Saldo SMS Baixo'),
                'note': _(
                    '<p>O saldo da API SMS <strong>%s</strong> está abaixo do limite configurado.</p>'
                    '<p>Saldo atual: <strong>R$ %.2f</strong></p>'
                    '<p>Limite de alerta: <strong>R$ %.2f</strong></p>'
                    '<p>Por favor, recarregue o saldo para evitar interrupção no envio de mensagens.</p>'
                ) % (self.name, balance, self.balance_warning_threshold),
                'date_deadline': fields.Date.today(),
            })

            _logger.warning(
                f"Alerta de saldo baixo enviado para API '{self.name}': "
                f"R$ {balance:.2f} (limite: R$ {self.balance_warning_threshold:.2f})"
            )

        except Exception as e:
            _logger.error(f"Erro ao criar notificação de saldo baixo: {str(e)}")

    @api.model
    def cron_update_balance(self):
        """Job agendado para atualizar o saldo de todas as APIs ativas"""
        _logger.info("Iniciando atualização automática de saldo das APIs SMS")

        # Busca todas as APIs ativas
        apis = self.search([('active', '=', True)])

        success_count = 0
        error_count = 0

        for api in apis:
            try:
                api.update_balance()
                success_count += 1
            except Exception as e:
                _logger.error(f"Erro ao atualizar saldo da API '{api.name}': {str(e)}")
                error_count += 1

        _logger.info(
            f"Atualização de saldo concluída: {success_count} sucesso(s), "
            f"{error_count} erro(s)"
        )

        return True
