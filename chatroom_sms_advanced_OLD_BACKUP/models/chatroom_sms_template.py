# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re


class ChatroomSmsTemplate(models.Model):
    _name = 'chatroom.sms.template'
    _description = 'Template de SMS'
    _order = 'name'

    name = fields.Char(
        string='Nome do Template',
        required=True,
        help='Nome identificador do template'
    )
    code = fields.Char(
        string='Código',
        help='Código único para identificar o template'
    )
    message = fields.Text(
        string='Mensagem',
        required=True,
        help='Use variáveis: {nome}, {telefone}, {data}, etc.'
    )
    variables = fields.Char(
        string='Variáveis Disponíveis',
        compute='_compute_variables',
        store=False,
        help='Variáveis encontradas no template'
    )
    active = fields.Boolean(
        string='Ativo',
        default=True
    )
    usage_count = fields.Integer(
        string='Vezes Utilizado',
        compute='_compute_usage_count',
        readonly=True,
        store=False,
        help='Número de vezes que este template foi utilizado'
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'O código do template deve ser único!')
    ]

    @api.depends('message')
    def _compute_variables(self):
        """Extrai as variáveis {xxx} da mensagem do template"""
        for record in self:
            if record.message:
                # Busca padrões do tipo {variable}
                variables = re.findall(r'\{(\w+)\}', record.message)
                if variables:
                    # Remove duplicatas e ordena
                    unique_vars = sorted(set(variables))
                    record.variables = ', '.join(['{%s}' % var for var in unique_vars])
                else:
                    record.variables = 'Nenhuma variável encontrada'
            else:
                record.variables = 'Nenhuma variável encontrada'

    def _compute_usage_count(self):
        """Conta quantas vezes o template foi usado em SMS agendados"""
        for record in self:
            count = self.env['chatroom.sms.scheduled'].search_count([
                ('template_id', '=', record.id)
            ])
            record.usage_count = count

    def apply_template(self, values_dict):
        """
        Substitui as variáveis do template pelos valores fornecidos

        Args:
            values_dict (dict): Dicionário com os valores das variáveis
                                Exemplo: {'nome': 'João', 'telefone': '11999999999'}

        Returns:
            str: Mensagem com as variáveis substituídas
        """
        self.ensure_one()

        if not self.message:
            return ''

        message = self.message

        # Substitui cada variável encontrada no dicionário
        for key, value in values_dict.items():
            pattern = '{%s}' % key
            if pattern in message:
                message = message.replace(pattern, str(value))

        return message

    def action_preview_template(self):
        """Ação para visualizar preview do template"""
        self.ensure_one()

        # Cria valores de exemplo para preview
        sample_values = {
            'nome': 'João Silva',
            'telefone': '(11) 99999-9999',
            'data': fields.Date.today().strftime('%d/%m/%Y'),
            'hora': '14:30',
            'empresa': 'Minha Empresa',
            'valor': 'R$ 100,00'
        }

        preview_message = self.apply_template(sample_values)

        return {
            'name': 'Preview do Template',
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.template',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'default_preview': preview_message
            }
        }

    @api.model
    def get_template_by_code(self, code):
        """
        Busca um template pelo código

        Args:
            code (str): Código do template

        Returns:
            recordset: Template encontrado ou vazio
        """
        return self.search([('code', '=', code), ('active', '=', True)], limit=1)
