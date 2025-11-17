# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class SMSScheduled(models.Model):
    """
    Scheduled SMS Tasks
    - One-time scheduling
    - Recurring scheduling (daily, weekly, monthly)
    - Auto-execution via cron
    """
    _name = 'sms.scheduled'
    _description = 'Scheduled SMS'
    _order = 'next_run desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ========== BASIC INFO ==========
    name = fields.Char(
        string='Description',
        required=True,
        tracking=True
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )

    # ========== PROVIDER & TEMPLATE ==========
    provider_id = fields.Many2one(
        'sms.provider',
        string='SMS Provider',
        required=True,
        tracking=True
    )

    template_id = fields.Many2one(
        'sms.template',
        string='Message Template',
        required=True,
        tracking=True
    )

    # ========== SCHEDULE SETTINGS ==========
    schedule_type = fields.Selection([
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], string='Schedule Type', required=True, default='once', tracking=True)

    schedule_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )

    schedule_time = fields.Float(
        string='Time (Hours)',
        default=9.0,
        help='Time in 24h format (e.g., 9.5 = 09:30)',
        tracking=True
    )

    interval = fields.Integer(
        string='Interval',
        default=1,
        help='Repeat every X days/weeks/months',
        tracking=True
    )

    # ========== RUN TRACKING ==========
    next_run = fields.Datetime(
        string='Next Run',
        compute='_compute_next_run',
        store=True,
        index=True
    )

    last_run = fields.Datetime(
        string='Last Run',
        readonly=True
    )

    # ========== STATE ==========
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)

    # ========== RECIPIENTS ==========
    partner_ids = fields.Many2many(
        'res.partner',
        'sms_scheduled_partner_rel',
        'scheduled_id',
        'partner_id',
        string='Recipients',
        help='Partners to send SMS to'
    )

    domain_filter = fields.Char(
        string='Domain Filter',
        help='Python domain to filter partners dynamically (e.g., [("customer_rank", ">", 0)])'
    )

    recipient_count = fields.Integer(
        string='Recipient Count',
        compute='_compute_recipient_count'
    )

    # ========== STATISTICS ==========
    total_sent = fields.Integer(
        string='Total Sent',
        readonly=True
    )

    total_runs = fields.Integer(
        string='Total Runs',
        readonly=True
    )

    # ========== COMPUTE METHODS ==========
    @api.depends('schedule_date', 'schedule_time', 'schedule_type', 'last_run', 'interval')
    def _compute_next_run(self):
        """Calculate next run datetime"""
        for record in self:
            if record.state not in ['active', 'draft']:
                record.next_run = False
                continue

            if not record.schedule_date:
                record.next_run = False
                continue

            # Convert time float to hours and minutes
            hours = int(record.schedule_time)
            minutes = int((record.schedule_time - hours) * 60)

            if record.last_run:
                # Calculate next run based on last run
                base_datetime = record.last_run

                if record.schedule_type == 'daily':
                    next_datetime = base_datetime + relativedelta(days=record.interval)
                elif record.schedule_type == 'weekly':
                    next_datetime = base_datetime + relativedelta(weeks=record.interval)
                elif record.schedule_type == 'monthly':
                    next_datetime = base_datetime + relativedelta(months=record.interval)
                else:  # once
                    record.next_run = False
                    continue

                record.next_run = next_datetime
            else:
                # First run - use schedule_date + schedule_time
                next_datetime = fields.Datetime.to_datetime(record.schedule_date)
                next_datetime = next_datetime.replace(hour=hours, minute=minutes, second=0)
                record.next_run = next_datetime

    @api.depends('partner_ids', 'domain_filter')
    def _compute_recipient_count(self):
        """Count total recipients"""
        for record in self:
            if record.domain_filter:
                try:
                    domain = eval(record.domain_filter)
                    count = self.env['res.partner'].search_count(domain)
                    record.recipient_count = count
                except:
                    record.recipient_count = 0
            else:
                record.recipient_count = len(record.partner_ids)

    # ========== CONSTRAINTS ==========
    @api.constrains('schedule_time')
    def _check_schedule_time(self):
        """Validate schedule time"""
        for record in self:
            if not (0 <= record.schedule_time < 24):
                raise ValidationError(_('Schedule time must be between 0 and 24 hours'))

    @api.constrains('interval')
    def _check_interval(self):
        """Validate interval"""
        for record in self:
            if record.interval < 1:
                raise ValidationError(_('Interval must be at least 1'))

    # ========== ACTIONS ==========
    def action_activate(self):
        """Activate scheduled task"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft tasks can be activated'))

            record.write({
                'state': 'active',
                'last_run': False,
                'total_runs': 0,
                'total_sent': 0,
            })

    def action_cancel(self):
        """Cancel scheduled task"""
        self.write({'state': 'cancelled'})

    def action_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft'})

    def action_run_now(self):
        """Execute immediately (manual trigger)"""
        self.ensure_one()
        if self.state not in ['active', 'draft']:
            raise UserError(_('Cannot run cancelled or completed tasks'))

        return self._execute_scheduled_task()

    # ========== EXECUTION ==========
    def _execute_scheduled_task(self):
        """Execute the scheduled task - send SMS to all recipients"""
        self.ensure_one()

        # Get recipients
        partners = self._get_recipients()
        if not partners:
            _logger.warning(f"Scheduled task {self.name} has no recipients")
            return

        # Check DND
        if self.provider_id.is_dnd_time():
            _logger.info(
                f"Scheduled task {self.name} skipped - DND time "
                f"({self.provider_id.dnd_start_hour}h - {self.provider_id.dnd_end_hour}h)"
            )
            return

        sent_count = 0
        for partner in partners:
            phone = partner.mobile or partner.phone
            if not phone:
                continue

            try:
                # Render template
                body = self.template_id._render_template(
                    self.template_id.body,
                    'res.partner',
                    [partner.id]
                )[partner.id]

                # Create SMS message
                sms = self.env['sms.message'].create({
                    'partner_id': partner.id,
                    'phone': phone,
                    'body': body,
                    'provider_id': self.provider_id.id,
                    'scheduled_id': self.id,
                })

                # Send immediately
                sms.action_send()
                sent_count += 1

            except Exception as e:
                _logger.error(f"Error sending scheduled SMS to {partner.name}: {e}")
                continue

        # Update statistics
        self.write({
            'last_run': fields.Datetime.now(),
            'total_runs': self.total_runs + 1,
            'total_sent': self.total_sent + sent_count,
        })

        # Mark as done if one-time schedule
        if self.schedule_type == 'once':
            self.state = 'done'

        _logger.info(
            f"Scheduled task '{self.name}' executed: "
            f"{sent_count} SMS sent to {len(partners)} recipients"
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Executed'),
                'message': _('%d SMS sent successfully') % sent_count,
                'type': 'success',
            }
        }

    def _get_recipients(self):
        """Get recipient partners based on domain or manual selection"""
        self.ensure_one()

        if self.domain_filter:
            try:
                domain = eval(self.domain_filter)
                return self.env['res.partner'].search(domain)
            except Exception as e:
                _logger.error(f"Error evaluating domain filter: {e}")
                return self.partner_ids
        else:
            return self.partner_ids

    # ========== CRON ==========
    @api.model
    def cron_process_scheduled_sms(self):
        """
        Cron job to process scheduled SMS
        Runs every 5 minutes
        """
        now = fields.Datetime.now()

        # Find tasks that should run now
        tasks = self.search([
            ('state', '=', 'active'),
            ('next_run', '<=', now),
        ])

        _logger.info(f"Processing {len(tasks)} scheduled SMS tasks")

        for task in tasks:
            try:
                task._execute_scheduled_task()
            except Exception as e:
                _logger.error(f"Error executing scheduled task {task.name}: {e}")
                # Create activity to notify about error
                task.activity_schedule(
                    'mail.mail_activity_data_warning',
                    summary=_('Scheduled SMS Task Failed'),
                    note=_('Error: %s') % str(e)
                )

        return True
