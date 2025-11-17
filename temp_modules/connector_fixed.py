# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AcruxChatConnector(models.Model):
    """
    Extensão do Connector do AcruxLab para suportar SMS
    """
    _inherit = 'acrux.chat.connector'

    def assert_id(self, key):
        """
        Validação de número para SMS (mais flexível que WhatsApp)
        """
        self.ensure_one()

        # Se for connector SMS, permite qualquer número válido
        if self.connector_type == 'sms':
            # SMS é mais flexível - apenas verifica se tem dígitos
            if key and any(c.isdigit() for c in str(key)):
                return True
            else:
                # Se não tem dígitos, usa validação padrão
                return super(AcruxChatConnector, self).assert_id(key)

        # Para outros tipos (WhatsApp, etc), usa validação original
        return super(AcruxChatConnector, self).assert_id(key)

    def clean_id(self, key):
        """
        Clean phone number for SMS
        """
        self.ensure_one()

        if self.connector_type == 'sms':
            # Remove tudo exceto dígitos
            return ''.join(filter(str.isdigit, str(key)))

        return super(AcruxChatConnector, self).clean_id(key)

    def format_id(self, key):
        """
        Format phone number for SMS
        """
        self.ensure_one()

        if self.connector_type == 'sms':
            # Para SMS, mantém formato simples: +5511999887766
            cleaned = self.clean_id(key)
            if cleaned and not cleaned.startswith('+'):
                return '+' + cleaned
            return cleaned if cleaned else key

        return super(AcruxChatConnector, self).format_id(key)

    def ca_get_status(self):
        """
        Verifica status do connector SMS

        Chamado quando usuário clica em "Check Status" no formulário
        """
        self.ensure_one()

        # Se for SMS, verifica provider ao invés de API do WhatsApp
        if self.connector_type == 'sms':
            Pop = self.env['acrux.chat.pop.message']

            if not self.sms_provider_id:
                raise UserError(_('No SMS provider configured for this connector.'))

            provider = self.sms_provider_id

            # Verifica se provider tem as configurações necessárias
            # Campos corretos: kolmeya_api_token e kolmeya_segment_id
            if not provider.kolmeya_api_token or not provider.kolmeya_segment_id:
                raise UserError(_(
                    'SMS Provider "%s" is not configured.\n'
                    'Please configure API Token and Segment ID.'
                ) % provider.name)

            # Tenta buscar saldo de créditos (se provider suportar)
            try:
                from odoo.addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI

                # Construtor correto: KolmeyaAPI(token, segment_id)
                api = KolmeyaAPI(
                    token=provider.kolmeya_api_token,
                    segment_id=provider.kolmeya_segment_id
                )

                # Tenta buscar saldo
                balance = api.get_balance()
                saldo = balance.get('saldo', 0.0)

                # Atualiza status do connector
                self.ca_status = True
                self.message = False

                # Retorna popup com mensagem de sucesso
                message = _('SMS Provider Status')
                detail = _('<b>Connected successfully!</b><br/>'
                          'Provider: %s<br/>'
                          'Balance: R$ %.2f') % (provider.name, saldo)

                return Pop.message(message, detail)

            except Exception as e:
                # Atualiza status do connector para erro
                self.ca_status = False
                self.message = str(e)

                # Retorna popup com erro
                message = _('SMS Provider Error')
                detail = _('<b>Failed to connect</b><br/>%s') % str(e)
                return Pop.message(message, detail)

        # Para outros tipos, usa método original
        return super(AcruxChatConnector, self).ca_get_status()

    def ca_request(self, path, data={}, params={}, timeout=False, ignore_exception=False):
        """
        Faz requisição para API externa

        IMPORTANTE: Signature deve ser EXATAMENTE igual ao método original
        para compatibilidade com todos os módulos WhatsApp

        Para SMS: não faz sentido (não há API de status direto)
        Para WhatsApp: usa método original
        """
        self.ensure_one()

        # Se for SMS, levanta erro amigável
        if self.connector_type == 'sms':
            raise UserError(_(
                'Direct API requests are not supported for SMS connectors.\n'
                'Use "Check Status" button instead.'
            ))

        # Para outros tipos, usa método original COM MESMA SIGNATURE
        return super(AcruxChatConnector, self).ca_request(
            path, data, params, timeout, ignore_exception
        )
