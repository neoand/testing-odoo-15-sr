# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class SMSDashboard(models.Model):
    """
    SMS Dashboard - SQL VIEW for Analytics
    Aggregates statistics from sms.message for reporting
    """
    _name = 'sms.dashboard'
    _description = 'SMS Dashboard Statistics'
    _auto = False  # This is a SQL view, not a regular table
    _order = 'period desc'

    # ========== GROUPING ==========
    period = fields.Date(
        string='Period',
        readonly=True,
        help='Date of the statistics'
    )

    provider_id = fields.Many2one(
        'sms.provider',
        string='Provider',
        readonly=True
    )

    campaign_id = fields.Many2one(
        'sms.campaign',
        string='Campaign',
        readonly=True
    )

    # ========== COUNTS ==========
    total_sent = fields.Integer(
        string='Total Sent',
        readonly=True,
        help='Total SMS sent (includes delivered, pending, etc)'
    )

    total_delivered = fields.Integer(
        string='Total Delivered',
        readonly=True,
        help='Total SMS successfully delivered'
    )

    total_failed = fields.Integer(
        string='Total Failed',
        readonly=True,
        help='Total SMS failed (error + rejected)'
    )

    total_pending = fields.Integer(
        string='Total Pending',
        readonly=True,
        help='Total SMS pending delivery'
    )

    # ========== RATES ==========
    delivery_rate = fields.Float(
        string='Delivery Rate (%)',
        readonly=True,
        digits=(5, 2),
        help='Percentage of delivered messages'
    )

    failure_rate = fields.Float(
        string='Failure Rate (%)',
        readonly=True,
        digits=(5, 2),
        help='Percentage of failed messages'
    )

    # ========== COSTS ==========
    total_cost = fields.Float(
        string='Total Cost (R$)',
        readonly=True,
        digits=(10, 2),
        help='Total cost of all SMS in this period'
    )

    avg_cost_per_sms = fields.Float(
        string='Avg Cost per SMS (R$)',
        readonly=True,
        digits=(10, 4),
        help='Average cost per SMS'
    )

    # ========== ADDITIONAL METRICS ==========
    total_messages = fields.Integer(
        string='Total Messages',
        readonly=True,
        help='Total number of SMS records'
    )

    unique_recipients = fields.Integer(
        string='Unique Recipients',
        readonly=True,
        help='Number of unique phone numbers'
    )

    # ========== VIEW INITIALIZATION ==========
    def init(self):
        """
        Create SQL VIEW for dashboard statistics
        Aggregates data from sms.message table
        """
        tools.drop_view_if_exists(self.env.cr, self._table)

        # Create the view
        query = """
            CREATE OR REPLACE VIEW {table} AS (
                SELECT
                    -- Unique ID for each row
                    ROW_NUMBER() OVER (
                        ORDER BY DATE(create_date) DESC, provider_id, campaign_id
                    ) as id,

                    -- Grouping fields
                    DATE(create_date) as period,
                    provider_id,
                    campaign_id,

                    -- Total counts
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT phone) as unique_recipients,

                    -- State counts
                    SUM(CASE
                        WHEN state IN ('sent', 'delivered')
                        THEN 1 ELSE 0
                    END) as total_sent,

                    SUM(CASE
                        WHEN state = 'delivered'
                        THEN 1 ELSE 0
                    END) as total_delivered,

                    SUM(CASE
                        WHEN state IN ('error', 'rejected')
                        THEN 1 ELSE 0
                    END) as total_failed,

                    SUM(CASE
                        WHEN state IN ('draft', 'outgoing', 'sent')
                        THEN 1 ELSE 0
                    END) as total_pending,

                    -- Delivery rate calculation
                    ROUND(
                        CAST(
                            SUM(CASE WHEN state = 'delivered' THEN 1 ELSE 0 END) AS NUMERIC
                        ) / NULLIF(
                            SUM(CASE WHEN state IN ('sent', 'delivered') THEN 1 ELSE 0 END), 0
                        ) * 100,
                        2
                    ) as delivery_rate,

                    -- Failure rate calculation
                    ROUND(
                        CAST(
                            SUM(CASE WHEN state IN ('error', 'rejected') THEN 1 ELSE 0 END) AS NUMERIC
                        ) / NULLIF(COUNT(*), 0) * 100,
                        2
                    ) as failure_rate,

                    -- Cost calculations
                    COALESCE(SUM(cost), 0) as total_cost,
                    COALESCE(AVG(cost), 0) as avg_cost_per_sms

                FROM sms_message
                WHERE create_date IS NOT NULL
                GROUP BY
                    DATE(create_date),
                    provider_id,
                    campaign_id
            )
        """.format(table=self._table)

        self.env.cr.execute(query)

    # ========== UTILITY METHODS ==========
    @api.model
    def get_dashboard_summary(self, period_start=None, period_end=None):
        """
        Get summary statistics for dashboard widgets

        Args:
            period_start: Start date for filtering (optional)
            period_end: End date for filtering (optional)

        Returns:
            dict with summary statistics
        """
        domain = []
        if period_start:
            domain.append(('period', '>=', period_start))
        if period_end:
            domain.append(('period', '<=', period_end))

        records = self.search(domain)

        if not records:
            return {
                'total_messages': 0,
                'total_sent': 0,
                'total_delivered': 0,
                'total_failed': 0,
                'total_cost': 0.0,
                'avg_delivery_rate': 0.0,
                'unique_recipients': 0,
            }

        return {
            'total_messages': sum(records.mapped('total_messages')),
            'total_sent': sum(records.mapped('total_sent')),
            'total_delivered': sum(records.mapped('total_delivered')),
            'total_failed': sum(records.mapped('total_failed')),
            'total_cost': sum(records.mapped('total_cost')),
            'avg_delivery_rate': sum(records.mapped('delivery_rate')) / len(records),
            'unique_recipients': sum(records.mapped('unique_recipients')),
        }

    @api.model
    def get_provider_comparison(self, period_start=None, period_end=None):
        """
        Get comparison data between providers

        Returns:
            list of dicts with provider statistics
        """
        domain = []
        if period_start:
            domain.append(('period', '>=', period_start))
        if period_end:
            domain.append(('period', '<=', period_end))

        records = self.search(domain)

        # Group by provider
        provider_stats = {}
        for record in records:
            provider_id = record.provider_id.id
            if provider_id not in provider_stats:
                provider_stats[provider_id] = {
                    'provider_name': record.provider_id.name,
                    'total_sent': 0,
                    'total_delivered': 0,
                    'total_failed': 0,
                    'total_cost': 0.0,
                }

            provider_stats[provider_id]['total_sent'] += record.total_sent
            provider_stats[provider_id]['total_delivered'] += record.total_delivered
            provider_stats[provider_id]['total_failed'] += record.total_failed
            provider_stats[provider_id]['total_cost'] += record.total_cost

        # Calculate rates
        for stats in provider_stats.values():
            if stats['total_sent'] > 0:
                stats['delivery_rate'] = (
                    stats['total_delivered'] / stats['total_sent']
                ) * 100
            else:
                stats['delivery_rate'] = 0.0

        return list(provider_stats.values())

    @api.model
    def get_trend_data(self, days=30):
        """
        Get trend data for the last N days

        Args:
            days: Number of days to include

        Returns:
            list of dicts with daily statistics
        """
        from datetime import datetime, timedelta

        end_date = fields.Date.today()
        start_date = end_date - timedelta(days=days)

        records = self.search([
            ('period', '>=', start_date),
            ('period', '<=', end_date),
        ], order='period asc')

        # Group by date
        trend_data = {}
        for record in records:
            date_str = str(record.period)
            if date_str not in trend_data:
                trend_data[date_str] = {
                    'date': date_str,
                    'total_sent': 0,
                    'total_delivered': 0,
                    'total_failed': 0,
                    'total_cost': 0.0,
                }

            trend_data[date_str]['total_sent'] += record.total_sent
            trend_data[date_str]['total_delivered'] += record.total_delivered
            trend_data[date_str]['total_failed'] += record.total_failed
            trend_data[date_str]['total_cost'] += record.total_cost

        return list(trend_data.values())
