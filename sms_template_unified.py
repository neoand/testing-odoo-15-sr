# -*- coding: utf-8 -*-
"""
SMS Template Model - UNIFIED VERSION
====================================

From sms_base_sr with enhancements for unified system

PARA: /odoo/custom/addons_custom/sms_core_unified/models/sms_template.py
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSTemplate(models.Model):
    """
    SMS Template Model - UNIFIED VERSION
    """
    _name = 'sms.template'
    _description = 'SMS Template Management'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')

    # Template Content
    content = fields.Text(string='Message Content', required=True, help='Use {{variable}} for dynamic content')
    default_language = fields.Selection([
        ('pt_BR', 'Português (Brasil)'),
        ('en_US', 'English'),
        ('es_ES', 'Español'),
    ], string='Default Language', default='pt_BR')

    # Template Variables (for dynamic content)
    variable_ids = fields.One2many(
        'sms.template.variable',
        'template_id',
        string='Variables'
    )

    # Statistics
    usage_count = fields.Integer(string='Usage Count', readonly=True, default=0)
    last_used = fields.Datetime(string='Last Used', readonly=True)

    # Metadata
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    create_date = fields.Datetime(string='Created Date', readonly=True)

    @api.model
    def render_template(self, template_id, values):
        """
        Render template with provided values
        """
        template = self.browse(template_id)
        if not template:
            raise ValidationError(_('Template not found'))

        content = template.content

        # Replace variables
        for variable in template.variable_ids:
            var_name = variable.name
            var_value = values.get(var_name, variable.default_value)

            if var_value is not None:
                content = content.replace('{{%s}}' % var_name, str(var_value))

        return content

    def action_preview(self):
        """Preview template with sample data"""
        self.ensure_one()

        sample_values = {
            'phone': '11999999999',
            'partner_name': 'Exemplo Cliente',
            'amount': '150.00',
            'date': fields.Date.today().strftime('%d/%m/%Y'),
        }

        rendered = self.render_template(self.id, sample_values)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Template Preview'),
            'view_mode': 'form',
            'res_model': 'sms.template.preview',
            'target': 'new',
            'context': {
                'default_content': rendered,
                'default_template_id': self.id,
            }
        }

    @api.model
    def get_template_by_name(self, name):
        """Get template by name"""
        return self.search([
            ('name', '=', name),
            ('active', '=', True)
        ], limit=1)


class SMSTemplateVariable(models.Model):
    """
    SMS Template Variables
    """
    _name = 'sms.template.variable'
    _description = 'SMS Template Variables'
    _order = 'name'

    name = fields.Char(string='Variable Name', required=True, help='e.g: partner_name, amount, date')
    template_id = fields.Many2one('sms.template', string='Template', ondelete='cascade')
    default_value = fields.Char(string='Default Value', help='Default value if not provided')
    description = fields.Text(string='Description')
    required = fields.Boolean(string='Required', default=False)

    _sql_constraints = [
        ('name_template_unique', 'UNIQUE(name, template_id)', 'Variable name must be unique within template'),
    ]

    @api.constrains('name')
    def _check_name_format(self):
        """Validate variable name format"""
        for record in self:
            if record.name and not record.name.replace('_', '').isalnum():
                raise ValidationError(_('Variable name must contain only letters, numbers, and underscores'))