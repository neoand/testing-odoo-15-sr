# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ChatroomSmsScheduled(models.Model):
    _name = 'chatroom.sms.scheduled'
    _description = 'SMS Agendado'
    _order = 'scheduled_date desc'

    name = fields.Char(
        string='Nome',
        required=True,
        help='Nome identificador do agendamento'
    )
    room_id = fields.Many2one(
        'chatroom.room',
        string='Sala',
        required=True,
        ondelete='cascade',
        help='Sala para qual o SMS será enviado'
    )
    template_id = fields.Many2one(
        'chatroom.sms.template',
        string='Template',
        ondelete='set null',
        help='Template de mensagem a ser utilizado'
    )
    message = fields.Text(
        string='Mensagem',
        required=True,
        help='Mensagem que será enviada'
    )
    scheduled_date = fields.Datetime(
        string='Data/Hora Agendada',
        required=True,
        help='Data e hora em que o SMS será enviado'
    )
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('scheduled', 'Agendado'),
        ('sent', 'Enviado'),
        ('cancelled', 'Cancelado'),
        ('failed', 'Falhou')
    ], string='Status', default='draft', required=True)
    sent_at = fields.Datetime(
        string='Enviado em',
        readonly=True,
        help='Data e hora em que o SMS foi efetivamente enviado'
    )
    result_message = fields.Text(
        string='Resultado',
        readonly=True,
        help='Mensagem de resultado do envio'
    )

    # Campos auxiliares
    user_id = fields.Many2one(
        'res.users',
        string='Criado por',
        default=lambda self: self.env.user,
        readonly=True
    )
    phone = fields.Char(
        related='room_id.phone',
        string='Telefone',
        readonly=True,
        store=True
    )

    @api.constrains('scheduled_date')
    def _check_scheduled_date(self):
        """Valida que a data agendada não seja no passado"""
        for record in self:
            if record.scheduled_date and record.state == 'draft':
                if record.scheduled_date < fields.Datetime.now():
                    raise ValidationError(
                        _('A data agendada não pode ser no passado!')
                    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Preenche a mensagem quando um template é selecionado"""
        if self.template_id and self.room_id:
            # Prepara valores para o template
            values = {
                'nome': self.room_id.name or '',
                'telefone': self.room_id.phone or '',
                'data': fields.Date.today().strftime('%d/%m/%Y')
            }
            self.message = self.template_id.apply_template(values)

    def action_schedule(self):
        """Agenda o SMS para envio"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Apenas SMS em rascunho podem ser agendados!'))

            if record.scheduled_date < fields.Datetime.now():
                raise UserError(_('A data agendada não pode ser no passado!'))

            record.write({
                'state': 'scheduled',
                'result_message': 'SMS agendado para %s' % record.scheduled_date
            })

        return True

    def action_send_now(self):
        """Envia o SMS imediatamente"""
        for record in self:
            if record.state not in ['draft', 'scheduled']:
                raise UserError(_('Este SMS não pode ser enviado!'))

            try:
                # Busca a API de SMS configurada
                sms_api = self.env['chatroom.sms.api'].search([
                    ('active', '=', True)
                ], limit=1)

                if not sms_api:
                    raise UserError(_('Nenhuma API de SMS está configurada!'))

                # Envia o SMS
                result = sms_api.send_sms(
                    phone=record.room_id.phone,
                    message=record.message,
                    room_id=record.room_id.id
                )

                if result.get('success'):
                    record.write({
                        'state': 'sent',
                        'sent_at': fields.Datetime.now(),
                        'result_message': 'SMS enviado com sucesso! ID: %s' % result.get('message_id', '')
                    })

                    _logger.info('SMS agendado #%s enviado com sucesso para %s',
                                record.id, record.room_id.phone)
                else:
                    record.write({
                        'state': 'failed',
                        'result_message': 'Erro ao enviar SMS: %s' % result.get('error', 'Erro desconhecido')
                    })

                    _logger.error('Erro ao enviar SMS agendado #%s: %s',
                                 record.id, result.get('error'))

            except Exception as e:
                record.write({
                    'state': 'failed',
                    'result_message': 'Exceção ao enviar SMS: %s' % str(e)
                })
                _logger.exception('Exceção ao enviar SMS agendado #%s', record.id)

        return True

    def action_cancel(self):
        """Cancela o agendamento"""
        for record in self:
            if record.state not in ['draft', 'scheduled']:
                raise UserError(_('Apenas SMS em rascunho ou agendados podem ser cancelados!'))

            record.write({
                'state': 'cancelled',
                'result_message': 'SMS cancelado pelo usuário em %s' % fields.Datetime.now()
            })

        return True

    def action_set_to_draft(self):
        """Retorna o SMS para rascunho"""
        for record in self:
            if record.state != 'cancelled':
                raise UserError(_('Apenas SMS cancelados podem retornar para rascunho!'))

            record.write({
                'state': 'draft',
                'result_message': False,
                'sent_at': False
            })

        return True

    @api.model
    def cron_send_scheduled_sms(self):
        """
        Método chamado pelo cron para enviar SMS agendados
        Procura por SMS agendados cuja data/hora já passou
        """
        _logger.info('Iniciando cron de envio de SMS agendados')

        now = fields.Datetime.now()

        # Busca SMS agendados cuja data já passou
        scheduled_sms = self.search([
            ('state', '=', 'scheduled'),
            ('scheduled_date', '<=', now)
        ])

        _logger.info('Encontrados %s SMS para enviar', len(scheduled_sms))

        sent_count = 0
        failed_count = 0

        for sms in scheduled_sms:
            try:
                sms.action_send_now()
                if sms.state == 'sent':
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                _logger.error('Erro ao enviar SMS agendado #%s: %s', sms.id, str(e))
                failed_count += 1

        _logger.info(
            'Cron finalizado. Enviados: %s, Falhados: %s',
            sent_count, failed_count
        )

        return {
            'sent': sent_count,
            'failed': failed_count,
            'total': len(scheduled_sms)
        }

    def unlink(self):
        """Previne exclusão de SMS já enviados"""
        for record in self:
            if record.state == 'sent':
                raise UserError(_('Não é possível excluir SMS já enviados!'))
        return super(ChatroomSmsScheduled, self).unlink()
