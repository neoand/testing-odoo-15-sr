# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSTemplate(models.Model):
    _name = 'sms.template'
    _description = 'SMS Template'
    _order = 'name'

    name = fields.Char('Template Name', required=True)
    code = fields.Char('Template Code', required=True, help='Unique code for this template')

    # Template content
    message_template = fields.Text(
        'Message Template',
        required=True,
        help='Use Python string formatting: {name}, {cpf}, {value}, etc.'
    )

    # Preview
    message_preview = fields.Text('Preview', compute='_compute_preview')

    # Application context
    applies_to = fields.Selection([
        ('res_partner', 'Contacts'),
        ('contacts_realcred', 'RealCred Database'),
        ('crm_lead', 'Opportunities'),
        ('all', 'All')
    ], string='Applies To', default='all', required=True)

    # Control
    active = fields.Boolean('Active', default=True)
    admin_only = fields.Boolean('Admin Only', default=True, help='Only admin can edit this template')

    # Statistics
    use_count = fields.Integer('Times Used', compute='_compute_use_count')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Template code must be unique!')
    ]

    @api.depends('message_template')
    def _compute_preview(self):
        """Generate preview with sample data"""
        for template in self:
            try:
                # Sample data for preview
                sample_data = {
                    'name': 'João Silva',
                    'cpf': '123.456.789-00',
                    'value': 'R$ 1.500,00',
                    'phone': '(48) 99999-9999',
                    'user': 'Vendedora Ana'
                }
                preview = template.message_template.format(**sample_data)
                template.message_preview = preview
            except Exception as e:
                template.message_preview = f"Error in template: {str(e)}"

    def _compute_use_count(self):
        """Count how many times this template was used"""
        for template in self:
            # This would need to be implemented based on actual usage tracking
            template.use_count = 0

    def render(self, data_dict):
        """
        Render template with actual data

        Args:
            data_dict: dict with keys matching template variables

        Returns:
            str: Rendered message
        """
        self.ensure_one()
        try:
            return self.message_template.format(**data_dict)
        except KeyError as e:
            raise ValidationError(_('Missing template variable: %s') % str(e))
        except Exception as e:
            raise ValidationError(_('Template rendering error: %s') % str(e))

    @api.constrains('message_template')
    def _check_template_syntax(self):
        """Validate template syntax"""
        for template in self:
            if template.message_template:
                try:
                    # Test with empty dict to check syntax
                    template.message_template.format()
                except (KeyError, IndexError):
                    # KeyError/IndexError expected if template has variables
                    pass
                except Exception as e:
                    raise ValidationError(_('Invalid template syntax: %s') % str(e))
