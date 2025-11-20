# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSMessage(models.Model):
    _name = 'sms.message'
    _description = 'SMS Message'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date DESC, id DESC'
    _rec_name = 'phone'

    # Relations
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        index=True,
        tracking=True,
        help='Partner associated with this SMS'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        tracking=True
    )
    provider_id = fields.Many2one(
        'sms.provider',
        string='SMS Provider',
        tracking=True
    )

    # Content
    phone = fields.Char(
        'Phone Number',
        required=True,
        index=True,
        help='Phone number in international format (e.g., 5548991910234)'
    )
    body = fields.Text(
        'Message Content',
        required=True,
        help='SMS message text'
    )
    direction = fields.Selection([
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming')
    ], string='Direction', default='outgoing', required=True, tracking=True)

    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('error', 'Error'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', required=True, tracking=True, index=True)

    # Provider-specific fields
    provider_message_id = fields.Char(
        'Provider Message ID',
        index=True,
        help='Unique message ID from SMS provider'
    )
    provider_job_id = fields.Char(
        'Provider Job ID',
        help='Batch/Job ID from SMS provider'
    )
    parent_id = fields.Many2one('sms.message', 'Parent Message',
                                   help='Original message if this is a reply',
                                   ondelete='set null', index=True)

    provider_reference = fields.Char(
        'Provider Reference',
        help='Custom reference sent to provider'
    )

    # Dates
    sent_date = fields.Datetime('Sent Date', readonly=True)
    delivered_date = fields.Datetime('Delivered Date', readonly=True)

    # Error handling
    error_message = fields.Text('Error Message', readonly=True)
    retry_count = fields.Integer('Retry Count', default=0, readonly=True)

    # Statistics
    char_count = fields.Integer('Character Count', compute='_compute_char_count', store=True)
    sms_count = fields.Integer('SMS Count', compute='_compute_sms_count', store=True,
                                help='Number of SMS segments (160 chars each)')

    # Cost tracking
    cost = fields.Float('Cost', default=0.10, help='Cost in BRL')

    @api.depends('body')
    def _compute_char_count(self):
        for rec in self:
            rec.char_count = len(rec.body) if rec.body else 0

    @api.depends('char_count')
    def _compute_sms_count(self):
        for rec in self:
            if rec.char_count == 0:
                rec.sms_count = 0
            else:
                # Standard SMS: 160 chars, extended: 153 chars per segment
                chars_per_sms = 160 if rec.char_count <= 160 else 153
                rec.sms_count = (rec.char_count + chars_per_sms - 1) // chars_per_sms

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-populate phone number when partner is selected"""
        if self.partner_id:
            # Priority: mobile first, then phone, then empty
            if self.partner_id.mobile:
                self.phone = self.partner_id.mobile
            elif self.partner_id.phone:
                self.phone = self.partner_id.phone
            else:
                self.phone = False
        else:
            self.phone = False

    @api.model
    def create(self, vals):
        """Log SMS creation in partner chatter"""
        sms = super(SMSMessage, self).create(vals)

        # Post in partner chatter if partner exists
        if sms.partner_id:
            icon = '📤' if sms.direction == 'outgoing' else '📥'
            truncated_body = sms.body[:100] + '...' if len(sms.body) > 100 else sms.body
            sms.partner_id.message_post(
                body=f"{icon} <strong>SMS {sms.direction}</strong><br/>{truncated_body}",
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

        return sms

    def write(self, vals):
        """Log status changes in chatter"""
        result = super(SMSMessage, self).write(vals)

        if 'state' in vals:
            status_icons = {
                'outgoing': '🔄',
                'sent': '📤',
                'delivered': '✅',
                'error': '❌',
                'rejected': '⛔',
                'expired': '⏰',
                'canceled': '🚫'
            }

            for sms in self:
                icon = status_icons.get(sms.state, '🔄')
                sms.message_post(
                    body=f"{icon} Status changed to: <strong>{sms.state}</strong>",
                    message_type='notification'
                )

        return result

    def action_send(self):
        """Send SMS via provider"""
        self.ensure_one()

        if self.state not in ['draft', 'error']:
            raise UserError(_('Only draft or failed SMS can be sent.'))

        if not self.provider_id:
            raise UserError(_('No SMS provider configured.'))

        try:
            # Call provider send method
            self.provider_id._send_sms(self)
            self.write({
                'state': 'outgoing',
                'sent_date': fields.Datetime.now()
            })
        except Exception as e:
            _logger.error(f"Failed to send SMS {self.id}: {e}")
            self.write({
                'state': 'error',
                'error_message': str(e),
                'retry_count': self.retry_count + 1
            })
            raise

    def action_cancel(self):
        """Cancel SMS"""
        self.filtered(lambda s: s.state in ['draft', 'outgoing']).write({'state': 'canceled'})

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft', 'error_message': False})

    @api.constrains('phone')
    def _check_phone(self):
        """Validate phone number format"""
        for rec in self:
            if rec.phone:
                # Remove common separators
                clean_phone = rec.phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                if not clean_phone.isdigit():
                    raise ValidationError(_('Phone number must contain only digits.'))
                if len(clean_phone) < 10 or len(clean_phone) > 15:
                    raise ValidationError(_('Phone number must be between 10 and 15 digits.'))