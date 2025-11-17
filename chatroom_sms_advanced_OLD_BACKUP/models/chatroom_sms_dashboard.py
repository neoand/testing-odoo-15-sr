# -*- coding: utf-8 -*-

from odoo import models, fields, tools


class ChatroomSmsDashboard(models.Model):
    _name = 'chatroom.sms.dashboard'
    _description = 'Dashboard de SMS'
    _auto = False
    _order = 'period desc'

    period = fields.Date(
        string='Período',
        readonly=True,
        help='Data do período analisado'
    )
    total_sent = fields.Integer(
        string='Total Enviado',
        readonly=True,
        help='Total de SMS enviados no período'
    )
    total_delivered = fields.Integer(
        string='Total Entregue',
        readonly=True,
        help='Total de SMS entregues com sucesso'
    )
    total_failed = fields.Integer(
        string='Total Falhou',
        readonly=True,
        help='Total de SMS que falharam na entrega'
    )
    delivery_rate = fields.Float(
        string='Taxa de Entrega (%)',
        readonly=True,
        digits=(5, 2),
        help='Percentual de SMS entregues com sucesso'
    )
    total_replies = fields.Integer(
        string='Total de Respostas',
        readonly=True,
        help='Total de respostas recebidas dos clientes'
    )
    total_cost = fields.Float(
        string='Custo Total',
        readonly=True,
        digits=(12, 2),
        help='Custo total dos SMS enviados no período'
    )

    # Campos adicionais para análise
    avg_delivery_time = fields.Float(
        string='Tempo Médio de Entrega (min)',
        readonly=True,
        digits=(8, 2),
        help='Tempo médio de entrega em minutos'
    )

    def init(self):
        """
        Cria a view SQL para o dashboard de SMS

        Esta view agrega dados dos logs de SMS por período (dia),
        calculando métricas importantes como total enviado, entregue,
        taxa de entrega, etc.
        """
        tools.drop_view_if_exists(self.env.cr, self._table)

        query = """
            CREATE OR REPLACE VIEW chatroom_sms_dashboard AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY DATE(csl.sent_at)) AS id,
                    DATE(csl.sent_at) AS period,
                    COUNT(csl.id) AS total_sent,
                    COUNT(CASE WHEN csl.status = 'delivered' THEN 1 END) AS total_delivered,
                    COUNT(CASE WHEN csl.status IN ('failed', 'undelivered') THEN 1 END) AS total_failed,
                    CASE
                        WHEN COUNT(csl.id) > 0 THEN
                            ROUND(
                                (COUNT(CASE WHEN csl.status = 'delivered' THEN 1 END)::numeric / COUNT(csl.id)::numeric) * 100,
                                2
                            )
                        ELSE 0
                    END AS delivery_rate,
                    COUNT(CASE WHEN cc.is_customer_message = TRUE THEN 1 END) AS total_replies,
                    SUM(COALESCE(csl.cost, 0)) AS total_cost,
                    CASE
                        WHEN COUNT(CASE WHEN csl.status = 'delivered' AND csl.delivered_at IS NOT NULL THEN 1 END) > 0 THEN
                            ROUND(
                                AVG(
                                    CASE
                                        WHEN csl.status = 'delivered' AND csl.delivered_at IS NOT NULL
                                        THEN EXTRACT(EPOCH FROM (csl.delivered_at - csl.sent_at)) / 60
                                        ELSE NULL
                                    END
                                )::numeric,
                                2
                            )
                        ELSE 0
                    END AS avg_delivery_time
                FROM
                    chatroom_sms_log csl
                LEFT JOIN
                    chatroom_conversation cc ON (
                        cc.room_id = csl.room_id
                        AND DATE(cc.date) = DATE(csl.sent_at)
                        AND cc.is_customer_message = TRUE
                    )
                WHERE
                    csl.sent_at IS NOT NULL
                GROUP BY
                    DATE(csl.sent_at)
                ORDER BY
                    period DESC
            )
        """

        self.env.cr.execute(query)

    def action_view_sms_logs(self):
        """Ação para visualizar os logs de SMS do período"""
        self.ensure_one()

        return {
            'name': 'Logs de SMS - %s' % self.period,
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.log',
            'view_mode': 'tree,form',
            'domain': [
                ('sent_at', '>=', self.period),
                ('sent_at', '<', fields.Date.add(self.period, days=1))
            ],
            'context': {'default_period': self.period}
        }

    def action_view_conversations(self):
        """Ação para visualizar as conversas do período"""
        self.ensure_one()

        return {
            'name': 'Conversas - %s' % self.period,
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.conversation',
            'view_mode': 'tree,form',
            'domain': [
                ('date', '>=', self.period),
                ('date', '<', fields.Date.add(self.period, days=1))
            ],
            'context': {'default_period': self.period}
        }

    @api.model
    def get_dashboard_data(self, period_start=None, period_end=None):
        """
        Retorna dados agregados do dashboard para um período específico

        Args:
            period_start (date): Data inicial do período
            period_end (date): Data final do período

        Returns:
            dict: Dicionário com os dados agregados
        """
        domain = []

        if period_start:
            domain.append(('period', '>=', period_start))
        if period_end:
            domain.append(('period', '<=', period_end))

        records = self.search(domain)

        if not records:
            return {
                'total_sent': 0,
                'total_delivered': 0,
                'total_failed': 0,
                'delivery_rate': 0,
                'total_replies': 0,
                'total_cost': 0,
                'avg_delivery_time': 0
            }

        return {
            'total_sent': sum(records.mapped('total_sent')),
            'total_delivered': sum(records.mapped('total_delivered')),
            'total_failed': sum(records.mapped('total_failed')),
            'delivery_rate': sum(records.mapped('delivery_rate')) / len(records) if records else 0,
            'total_replies': sum(records.mapped('total_replies')),
            'total_cost': sum(records.mapped('total_cost')),
            'avg_delivery_time': sum(records.mapped('avg_delivery_time')) / len(records) if records else 0
        }
