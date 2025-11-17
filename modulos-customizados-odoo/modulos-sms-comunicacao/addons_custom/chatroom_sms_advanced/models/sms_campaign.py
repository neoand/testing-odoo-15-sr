# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSCampaign(models.Model):
    """
    SMS Marketing Campaigns
    - Bulk SMS sending
    - Segment-based targeting
    - Statistics tracking
    - Cost analysis
    """
    _name = 'sms.campaign'
    _description = 'SMS Campaign'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ========== BASIC INFO ==========
    name = fields.Char(
        string='Campaign Name',
        required=True,
        tracking=True
    )

    description = fields.Text(
        string='Description'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    # ========== PROVIDER & TEMPLATE ==========
    provider_id = fields.Many2one(
        'sms.provider',
        string='SMS Provider',
        required=True,
        default=lambda self: self.env['sms.provider'].search([('active', '=', True)], limit=1),
        tracking=True
    )

    template_id = fields.Many2one(
        'sms.template',
        string='Message Template',
        required=True,
        tracking=True
    )

    # ========== RECIPIENTS ==========
    partner_ids = fields.Many2many(
        'res.partner',
        'sms_campaign_partner_rel',
        'campaign_id',
        'partner_id',
        string='Recipients'
    )

    domain_filter = fields.Char(
        string='Domain Filter',
        help='Python domain to filter partners (e.g., [("customer_rank", ">", 0)])'
    )

    recipient_count = fields.Integer(
        string='Total Recipients',
        compute='_compute_recipient_count',
        store=True
    )

    # ========== STATE ==========
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    # ========== MESSAGES ==========
    sms_message_ids = fields.One2many(
        'sms.message',
        'campaign_id',
        string='SMS Messages',
        readonly=True
    )

    # ========== STATISTICS ==========
    sent_count = fields.Integer(
        string='Sent',
        compute='_compute_stats',
        store=True
    )

    delivered_count = fields.Integer(
        string='Delivered',
        compute='_compute_stats',
        store=True
    )

    failed_count = fields.Integer(
        string='Failed',
        compute='_compute_stats',
        store=True
    )

    pending_count = fields.Integer(
        string='Pending',
        compute='_compute_stats',
        store=True
    )

    delivery_rate = fields.Float(
        string='Delivery Rate (%)',
        compute='_compute_stats',
        store=True
    )

    total_cost = fields.Float(
        string='Total Cost (R$)',
        compute='_compute_stats',
        store=True,
        digits=(10, 2)
    )

    avg_cost_per_sms = fields.Float(
        string='Avg Cost per SMS (R$)',
        compute='_compute_stats',
        store=True,
        digits=(10, 4)
    )

    # ========== DATES ==========
    start_date = fields.Datetime(
        string='Start Date',
        readonly=True,
        tracking=True
    )

    end_date = fields.Datetime(
        string='End Date',
        readonly=True,
        tracking=True
    )

    # ========== COMPUTE METHODS ==========
    @api.depends('partner_ids', 'domain_filter')
    def _compute_recipient_count(self):
        """Count total recipients"""
        for campaign in self:
            if campaign.domain_filter:
                try:
                    domain = eval(campaign.domain_filter)
                    count = self.env['res.partner'].search_count(domain)
                    campaign.recipient_count = count
                except:
                    campaign.recipient_count = 0
            else:
                campaign.recipient_count = len(campaign.partner_ids)

    @api.depends('sms_message_ids.state', 'sms_message_ids.cost')
    def _compute_stats(self):
        """Compute campaign statistics"""
        for campaign in self:
            messages = campaign.sms_message_ids

            # Count by state
            campaign.sent_count = len(messages.filtered(
                lambda m: m.state in ['sent', 'delivered']
            ))
            campaign.delivered_count = len(messages.filtered(
                lambda m: m.state == 'delivered'
            ))
            campaign.failed_count = len(messages.filtered(
                lambda m: m.state in ['error', 'rejected']
            ))
            campaign.pending_count = len(messages.filtered(
                lambda m: m.state in ['draft', 'outgoing']
            ))

            # Calculate delivery rate
            if campaign.sent_count > 0:
                campaign.delivery_rate = (
                    campaign.delivered_count / campaign.sent_count
                ) * 100
            else:
                campaign.delivery_rate = 0.0

            # Calculate costs
            campaign.total_cost = sum(messages.mapped('cost'))
            if len(messages) > 0:
                campaign.avg_cost_per_sms = campaign.total_cost / len(messages)
            else:
                campaign.avg_cost_per_sms = 0.0

    # ========== ACTIONS ==========
    def action_start_campaign(self):
        """Start campaign - send SMS to all recipients"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft campaigns can be started'))

        # Get recipients
        partners = self._get_recipients()
        if not partners:
            raise UserError(_('No recipients found for this campaign'))

        # Check DND
        if self.provider_id.is_dnd_time():
            raise UserError(_(
                'Cannot send SMS during DND hours '
                '(%d:00 - %d:00)'
            ) % (self.provider_id.dnd_start_hour, self.provider_id.dnd_end_hour))

        # Update state
        self.write({
            'state': 'running',
            'start_date': fields.Datetime.now(),
        })

        # Create and send SMS for each recipient
        created_count = 0
        for partner in partners:
            phone = partner.mobile or partner.phone
            if not phone:
                _logger.warning(f"Partner {partner.name} has no phone number")
                continue

            try:
                # Render template
                body = self.template_id._render_template(
                    self.template_id.body,
                    'res.partner',
                    [partner.id]
                )[partner.id]

                # Create SMS
                sms = self.env['sms.message'].create({
                    'partner_id': partner.id,
                    'phone': phone,
                    'body': body,
                    'provider_id': self.provider_id.id,
                    'campaign_id': self.id,
                })

                # Send SMS
                sms.action_send()
                created_count += 1

            except Exception as e:
                _logger.error(f"Error sending SMS to {partner.name}: {e}")
                continue

        _logger.info(
            f"Campaign '{self.name}' started: "
            f"{created_count} SMS sent to {len(partners)} recipients"
        )

        # Mark as done
        self.write({
            'state': 'done',
            'end_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Campaign Started'),
                'message': _('%d SMS messages sent!') % created_count,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cancel(self):
        """Cancel campaign"""
        for campaign in self:
            if campaign.state not in ['draft', 'running']:
                raise UserError(_('Only draft or running campaigns can be cancelled'))

            campaign.write({
                'state': 'cancelled',
                'end_date': fields.Datetime.now() if not campaign.end_date else campaign.end_date,
            })

    def action_reset_to_draft(self):
        """Reset to draft"""
        for campaign in self:
            if campaign.state != 'cancelled':
                raise UserError(_('Only cancelled campaigns can be reset to draft'))

            campaign.write({
                'state': 'draft',
                'start_date': False,
                'end_date': False,
            })

    def action_view_messages(self):
        """View campaign messages"""
        self.ensure_one()

        return {
            'name': _('Campaign Messages'),
            'type': 'ir.actions.act_window',
            'res_model': 'sms.message',
            'view_mode': 'tree,form',
            'domain': [('campaign_id', '=', self.id)],
            'context': {
                'default_campaign_id': self.id,
                'default_provider_id': self.provider_id.id,
            }
        }

    # ========== UTILITY METHODS ==========
    def _get_recipients(self):
        """Get recipient partners based on domain or manual selection"""
        self.ensure_one()

        if self.domain_filter:
            try:
                domain = eval(self.domain_filter)
                partners = self.env['res.partner'].search(domain)
                _logger.info(f"Domain filter found {len(partners)} partners")
                return partners
            except Exception as e:
                _logger.error(f"Error evaluating domain filter: {e}")
                raise UserError(_('Invalid domain filter: %s') % str(e))
        else:
            return self.partner_ids

    @api.model
    def get_campaign_summary(self):
        """Get summary statistics for dashboard"""
        campaigns = self.search([])

        return {
            'total_campaigns': len(campaigns),
            'active_campaigns': len(campaigns.filtered(lambda c: c.state == 'running')),
            'total_sent': sum(campaigns.mapped('sent_count')),
            'total_delivered': sum(campaigns.mapped('delivered_count')),
            'total_cost': sum(campaigns.mapped('total_cost')),
            'avg_delivery_rate': sum(campaigns.mapped('delivery_rate')) / len(campaigns) if campaigns else 0,
        }
