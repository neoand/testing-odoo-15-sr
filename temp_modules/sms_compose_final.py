# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import logging

_logger = logging.getLogger(__name__)


class SMSComposer(models.TransientModel):
    _name = 'sms.compose'
    _description = 'SMS Composer Wizard'

    template_id = fields.Many2one('sms.template', 'Template')
    partner_ids = fields.Many2many('res.partner', string='Recipients', required=True)
    phone_numbers = fields.Text('Phone Numbers', compute='_compute_phone_numbers', store=False)
    body = fields.Text('Message', required=True)
    provider_id = fields.Many2one('sms.provider', 'SMS Provider', required=True,
                                 default=lambda self: self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1))
    char_count = fields.Integer('Characters', compute='_compute_char_count')

    @api.model
    def default_get(self, fields_list):
        """Override to populate partner_ids from context"""
        res = super(SMSComposer, self).default_get(fields_list)

        # Get active_id from context (when opened from partner form)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        if active_model == 'res.partner' and active_id:
            res['partner_ids'] = [(6, 0, [active_id])]

        # Also check for default_partner_ids in context
        if self.env.context.get('default_partner_ids'):
            res['partner_ids'] = self.env.context.get('default_partner_ids')

        return res

    @api.depends('partner_ids')
    def _compute_phone_numbers(self):
        """Display phone numbers of selected partners"""
        for rec in self:
            phones = []
            for partner in rec.partner_ids:
                phone = partner.mobile or partner.phone
                if phone:
                    phones.append(f"{partner.name}: {phone}")
                else:
                    phones.append(f"{partner.name}: [SEM TELEFONE]")
            rec.phone_numbers = '\n'.join(phones) if phones else 'Nenhum destinatário selecionado'

    @api.depends('body')
    def _compute_char_count(self):
        for rec in self:
            rec.char_count = len(rec.body or '')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Render template for first partner when template is selected"""
        if self.template_id and self.partner_ids:
            # Get first partner for preview
            partner = self.partner_ids[0]
            try:
                # Render template using Odoo's mail.render.mixin
                rendered = self.template_id._render_field('body', [partner.id])
                # Get rendered text for first partner and strip HTML
                body_html = rendered.get(partner.id, '')
                self.body = html2plaintext(body_html) if body_html else self.template_id.body
            except Exception as e:
                _logger.warning(f"Error rendering template: {e}")
                self.body = self.template_id.body
        elif self.template_id:
            self.body = self.template_id.body

    def action_send_sms(self):
        """Send SMS to all selected partners"""
        self.ensure_one()

        phones = []
        for partner in self.partner_ids:
            phone = partner.mobile or partner.phone
            if phone:
                phones.append({'partner': partner, 'phone': phone})
            else:
                raise UserError(_('Partner %s has no phone number') % partner.name)

        if not phones:
            raise UserError(_('No phone numbers found'))

        sms_messages = self.env['sms.message']
        for phone_data in phones:
            partner = phone_data['partner']

            # Render template for each partner if template is selected
            body = self.body
            if self.template_id:
                try:
                    rendered = self.template_id._render_field('body', [partner.id])
                    body_html = rendered.get(partner.id, self.body)
                    body = html2plaintext(body_html) if body_html else self.body
                except Exception as e:
                    _logger.warning(f"Error rendering template for {partner.name}: {e}")
                    body = self.body

            sms = self.env['sms.message'].create({
                'partner_id': partner.id,
                'phone': phone_data['phone'],
                'body': body,
                'direction': 'outgoing',
                'state': 'draft',
                'provider_id': self.provider_id.id,
            })
            sms.action_send()
            sms_messages |= sms

        # Return action that closes the wizard and shows notification
        return {
            'type': 'ir.actions.act_window_close',
        }
