# -*- coding: utf-8 -*-
# Template para criação de novos models Odoo

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class TemplateName(models.Model):
    """
    Descrição do modelo.

    Este modelo é responsável por...
    """
    _name = 'module.model_name'
    _description = 'Descrição do Modelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Opcional: tracking e atividades
    _order = 'create_date desc'

    # ===========================
    # CAMPOS BÁSICOS
    # ===========================

    name = fields.Char(
        string='Nome',
        required=True,
        tracking=True,
        help='Nome principal do registro'
    )

    active = fields.Boolean(
        string='Ativo',
        default=True,
        help='Desmarque para arquivar'
    )

    description = fields.Text(
        string='Descrição',
        help='Descrição detalhada'
    )

    # ===========================
    # CAMPOS RELACIONAIS
    # ===========================

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Parceiro',
        required=False,
        ondelete='restrict',
        tracking=True
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsável',
        default=lambda self: self.env.user,
        tracking=True
    )

    # ===========================
    # CAMPOS DE SELEÇÃO
    # ===========================

    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('confirmed', 'Confirmado'),
        ('done', 'Concluído'),
        ('cancel', 'Cancelado'),
    ], string='Status', default='draft', required=True, tracking=True)

    # ===========================
    # CAMPOS COMPUTADOS
    # ===========================

    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True,
        help='Total calculado'
    )

    # ===========================
    # CONSTRAINTS
    # ===========================

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'O nome deve ser único!'),
    ]

    # ===========================
    # MÉTODOS COMPUTE
    # ===========================

    @api.depends('partner_id')
    def _compute_total(self):
        """Calcula o total baseado em..."""
        for record in self:
            # Lógica de cálculo
            record.total = 0.0

    # ===========================
    # ONCHANGE
    # ===========================

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Atualiza campos quando partner muda"""
        if self.partner_id:
            # Lógica onchange
            pass

    # ===========================
    # CONSTRAINTS PYTHON
    # ===========================

    @api.constrains('name')
    def _check_name(self):
        """Valida o nome"""
        for record in self:
            if record.name and len(record.name) < 3:
                raise ValidationError('Nome deve ter no mínimo 3 caracteres!')

    # ===========================
    # CRUD OVERRIDES
    # ===========================

    @api.model
    def create(self, vals):
        """Override create para lógica adicional"""
        # Lógica antes de criar
        record = super(TemplateName, self).create(vals)
        # Lógica após criar
        return record

    def write(self, vals):
        """Override write para lógica adicional"""
        # Lógica antes de atualizar
        result = super(TemplateName, self).write(vals)
        # Lógica após atualizar
        return result

    def unlink(self):
        """Override unlink para validações antes de deletar"""
        for record in self:
            if record.state != 'draft':
                raise UserError('Não é possível deletar registros confirmados!')
        return super(TemplateName, self).unlink()

    # ===========================
    # MÉTODOS DE AÇÃO
    # ===========================

    def action_confirm(self):
        """Confirma o registro"""
        self.ensure_one()
        self.write({'state': 'confirmed'})
        return True

    def action_done(self):
        """Marca como concluído"""
        self.ensure_one()
        self.write({'state': 'done'})
        return True

    def action_cancel(self):
        """Cancela o registro"""
        self.ensure_one()
        self.write({'state': 'cancel'})
        return True

    # ===========================
    # MÉTODOS AUXILIARES
    # ===========================

    def _method_name(self):
        """Método auxiliar privado"""
        self.ensure_one()
        # Lógica
        pass
