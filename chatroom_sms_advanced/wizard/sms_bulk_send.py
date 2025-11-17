# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSBulkSend(models.TransientModel):
    """
    Wizard for sending bulk SMS
    - Manual recipient selection or domain filter
    - Template support
    - Cost estimation
    - Campaign integration
    - Blacklist filtering
    """
    _name = 'sms.bulk.send'
    _description = 'Send Bulk SMS Wizard'

    # ========== SELECTION METHOD ==========
    selection_type = fields.Selection([
        ('manual', 'Manual Selection'),
        ('domain', 'Domain Filter'),
    ], string='Selection Type', default='manual', required=True)

    # ========== RECIPIENTS ==========
    partner_ids = fields.Many2many(
        'res.partner',
        'sms_bulk_send_partner_rel',
        'wizard_id',
        'partner_id',
        string='Recipients',
        help='Select partners to send SMS to'
    )

    domain_filter = fields.Char(
        string='Domain Filter',
        help='Python domain to filter partners (e.g., [("customer_rank", ">", 0)])'
    )

    # ========== MESSAGE ==========
    template_id = fields.Many2one(
        'sms.template',
        string='Template',
        help='SMS template to use'
    )

    body = fields.Text(
        string='Message',
        required=True,
        help='SMS message body (variables will be replaced per recipient)'
    )

    # ========== PROVIDER ==========
    provider_id = fields.Many2one(
        'sms.provider',
        string='SMS Provider',
        required=True,
        default=lambda self: self.env['sms.provider'].search([('active', '=', True)], limit=1)
    )

    # ========== CAMPAIGN ==========
    create_campaign = fields.Boolean(
        string='Create Campaign',
        default=False,
        help='Create a campaign to track these messages'
    )

    campaign_id = fields.Many2one(
        'sms.campaign',
        string='Existing Campaign',
        help='Link messages to existing campaign'
    )

    campaign_name = fields.Char(
        string='Campaign Name',
        help='Name for the new campaign'
    )

    # ========== OPTIONS ==========
    skip_blacklist = fields.Boolean(
        string='Skip Blacklisted Numbers',
        default=True,
        help='Automatically skip numbers in blacklist'
    )

    skip_no_phone = fields.Boolean(
        string='Skip Partners Without Phone',
        default=True,
        help='Skip partners that have no phone number'
    )

    # ========== STATISTICS ==========
    total_recipients = fields.Integer(
        string='Total Recipients',
        compute='_compute_statistics'
    )

    estimated_cost = fields.Float(
        string='Estimated Cost (R$)',
        compute='_compute_statistics',
        digits=(10, 2)
    )

    estimated_segments = fields.Integer(
        string='Estimated SMS Segments',
        compute='_compute_statistics',
        help='Total SMS segments (1 segment = 160 chars)'
    )

    # ========== COMPUTE METHODS ==========
    @api.depends('partner_ids', 'domain_filter', 'selection_type', 'body')
    def _compute_statistics(self):
        """Calculate statistics for the bulk send"""
        for wizard in self:
            # Get recipients
            recipients = wizard._get_recipients()
            wizard.total_recipients = len(recipients)

            # Calculate segments
            if wizard.body:
                char_count = len(wizard.body)
                segments_per_sms = (char_count // 160) + (1 if char_count % 160 else 0)
            else:
                segments_per_sms = 1

            wizard.estimated_segments = wizard.total_recipients * segments_per_sms

            # Calculate cost (R$ 0.10 per segment)
            wizard.estimated_cost = wizard.estimated_segments * 0.10

    # ========== ONCHANGE METHODS ==========
    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Load template body when template is selected"""
        if self.template_id:
            # Get template body
            # If template has a preview method, use it
            if hasattr(self.template_id, 'body'):
                self.body = self.template_id.body
            else:
                self.body = ''

    @api.onchange('selection_type')
    def _onchange_selection_type(self):
        """Clear recipients when changing selection type"""
        if self.selection_type == 'manual':
            self.domain_filter = False
        else:
            self.partner_ids = False

    @api.onchange('create_campaign')
    def _onchange_create_campaign(self):
        """Clear campaign fields based on selection"""
        if self.create_campaign:
            self.campaign_id = False
        else:
            self.campaign_name = False

    # ========== VALIDATION ==========
    @api.constrains('domain_filter')
    def _check_domain_filter(self):
        """Validate domain filter syntax"""
        for wizard in self:
            if wizard.domain_filter:
                try:
                    eval(wizard.domain_filter)
                except Exception as e:
                    raise ValidationError(_('Invalid domain filter: %s') % str(e))

    # ========== UTILITY METHODS ==========
    def _get_recipients(self):
        """Get recipient partners based on selection type"""
        self.ensure_one()

        if self.selection_type == 'manual':
            return self.partner_ids
        elif self.selection_type == 'domain' and self.domain_filter:
            try:
                domain = eval(self.domain_filter)
                return self.env['res.partner'].search(domain)
            except Exception as e:
                _logger.error(f"Error evaluating domain filter: {e}")
                return self.env['res.partner']
        else:
            return self.env['res.partner']

    def _create_or_get_campaign(self):
        """Create new campaign or return existing one"""
        self.ensure_one()

        if self.campaign_id:
            return self.campaign_id

        if self.create_campaign and self.campaign_name:
            campaign = self.env['sms.campaign'].create({
                'name': self.campaign_name,
                'provider_id': self.provider_id.id,
                'template_id': self.template_id.id if self.template_id else False,
                'state': 'draft',
            })
            return campaign

        return False

    # ========== ACTION METHODS ==========
    def action_send_bulk(self):
        """
        Send bulk SMS to all recipients
        Main action method
        """
        self.ensure_one()

        # Validation
        if not self.body:
            raise UserError(_('Message body is required'))

        # Get recipients
        recipients = self._get_recipients()
        if not recipients:
            raise UserError(_('No recipients selected'))

        # Check DND
        if self.provider_id.is_dnd_time():
            raise UserError(_(
                'Cannot send SMS during DND hours (%d:00 - %d:00)'
            ) % (self.provider_id.dnd_start_hour, self.provider_id.dnd_end_hour))

        # Get or create campaign
        campaign = self._create_or_get_campaign()
        if campaign:
            campaign.state = 'running'

        # Send SMS to each recipient
        sent_count = 0
        skipped_count = 0
        failed_count = 0

        for partner in recipients:
            # Get phone number
            phone = partner.mobile or partner.phone

            # Skip if no phone
            if not phone:
                if self.skip_no_phone:
                    skipped_count += 1
                    continue
                else:
                    _logger.warning(f"Partner {partner.name} has no phone number")
                    failed_count += 1
                    continue

            # Check blacklist
            if self.skip_blacklist:
                is_blacklisted, reason = self.env['sms.blacklist'].is_blacklisted(phone)
                if is_blacklisted:
                    _logger.info(f"Skipping blacklisted number {phone}: {reason}")
                    skipped_count += 1
                    continue

            try:
                # Render message body for this partner
                if self.template_id and hasattr(self.template_id, '_render_template'):
                    body = self.template_id._render_template(
                        self.template_id.body,
                        'res.partner',
                        [partner.id]
                    )[partner.id]
                else:
                    # Simple variable replacement
                    body = self.body
                    body = body.replace('{name}', partner.name or '')
                    body = body.replace('{phone}', phone or '')

                # Create SMS message
                sms = self.env['sms.message'].create({
                    'partner_id': partner.id,
                    'phone': phone,
                    'body': body,
                    'provider_id': self.provider_id.id,
                    'campaign_id': campaign.id if campaign else False,
                })

                # Send SMS
                sms.action_send()
                sent_count += 1

            except Exception as e:
                _logger.error(f"Error sending SMS to {partner.name}: {e}")
                failed_count += 1
                continue

        # Update campaign state
        if campaign:
            campaign.state = 'done'

        # Log results
        _logger.info(
            f"Bulk SMS completed: {sent_count} sent, "
            f"{skipped_count} skipped, {failed_count} failed"
        )

        # Return notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk SMS Completed'),
                'message': _(
                    'Sent: %d\nSkipped: %d\nFailed: %d'
                ) % (sent_count, skipped_count, failed_count),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_preview(self):
        """Preview message for first recipient"""
        self.ensure_one()

        recipients = self._get_recipients()
        if not recipients:
            raise UserError(_('No recipients to preview'))

        partner = recipients[0]

        # Render preview
        if self.template_id and hasattr(self.template_id, '_render_template'):
            preview = self.template_id._render_template(
                self.template_id.body,
                'res.partner',
                [partner.id]
            )[partner.id]
        else:
            preview = self.body
            preview = preview.replace('{name}', partner.name or '')
            preview = preview.replace('{phone}', partner.mobile or partner.phone or '')

        # Show preview in a message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Message Preview for %s') % partner.name,
                'message': preview,
                'type': 'info',
                'sticky': True,
            }
        }
