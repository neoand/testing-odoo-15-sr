#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar dashboard em tempo real
FASE 1 - Funcionalidade 5
"""

import re

# 1. MELHORAR sms_dashboard.py
dashboard_file = '/tmp/sms_dashboard_current.py'
with open(dashboard_file, 'r') as f:
    dashboard_content = f.read()

# Métodos para dashboard em tempo real
dashboard_methods = """
    @api.model
    def get_realtime_stats(self):
        \"\"\"
        Get real-time statistics for dashboard
        Returns current stats without caching
        \"\"\"
        # Get stats from sms.message
        messages = self.env['sms.message']
        
        # Count by state
        total_messages = messages.search_count([])
        draft_count = messages.search_count([('state', '=', 'draft')])
        outgoing_count = messages.search_count([('state', '=', 'outgoing')])
        sent_count = messages.search_count([('state', '=', 'sent')])
        delivered_count = messages.search_count([('state', '=', 'delivered')])
        error_count = messages.search_count([('state', '=', 'error')])
        
        # Calculate costs
        all_messages = messages.search([])
        total_cost = sum(all_messages.mapped('actual_cost')) or sum(all_messages.mapped('estimated_cost')) or 0.0
        total_estimated_cost = sum(all_messages.mapped('estimated_cost')) or 0.0
        
        # Calculate segments
        total_segments = sum(all_messages.mapped('segment_count')) or 0
        
        # Get stats from campaigns
        campaigns = self.env['sms.campaign']
        total_campaigns = campaigns.search_count([])
        active_campaigns = campaigns.search_count([('state', '=', 'running')])
        
        # Get stats from providers
        providers = self.env['sms.provider']
        total_providers = providers.search_count([('active', '=', True)])
        total_balance = sum(providers.search([('active', '=', True)]).mapped('balance'))
        
        # Calculate delivery rate
        delivery_rate = 0.0
        if sent_count + delivered_count > 0:
            delivery_rate = (delivered_count / (sent_count + delivered_count)) * 100
        
        # Calculate success rate
        success_rate = 0.0
        if total_messages > 0:
            success_rate = ((sent_count + delivered_count) / total_messages) * 100
        
        # Get stats from last 24 hours
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_messages = messages.search([
            ('create_date', '>=', yesterday.strftime('%Y-%m-%d %H:%M:%S'))
        ])
        recent_sent = len(recent_messages.filtered(lambda m: m.state in ['sent', 'delivered']))
        recent_cost = sum(recent_messages.mapped('actual_cost')) or sum(recent_messages.mapped('estimated_cost')) or 0.0
        
        return {
            'total_messages': total_messages,
            'draft_count': draft_count,
            'outgoing_count': outgoing_count,
            'sent_count': sent_count,
            'delivered_count': delivered_count,
            'error_count': error_count,
            'total_cost': total_cost,
            'total_estimated_cost': total_estimated_cost,
            'total_segments': total_segments,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_providers': total_providers,
            'total_balance': total_balance,
            'delivery_rate': round(delivery_rate, 2),
            'success_rate': round(success_rate, 2),
            'recent_sent_24h': recent_sent,
            'recent_cost_24h': recent_cost,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    @api.model
    def get_trend_data(self, days=7):
        \"\"\"
        Get trend data for the last N days
        
        Args:
            days (int): Number of days to include
            
        Returns:
            list: Daily statistics
        \"\"\"
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        messages = self.env['sms.message'].search([
            ('create_date', '>=', start_date.strftime('%Y-%m-%d %H:%M:%S')),
            ('create_date', '<=', end_date.strftime('%Y-%m-%d %H:%M:%S'))
        ])
        
        # Group by date
        daily_stats = defaultdict(lambda: {
            'date': '',
            'sent': 0,
            'delivered': 0,
            'failed': 0,
            'cost': 0.0
        })
        
        for message in messages:
            date_str = message.create_date.strftime('%Y-%m-%d') if message.create_date else ''
            if not date_str:
                continue
                
            daily_stats[date_str]['date'] = date_str
            
            if message.state == 'sent':
                daily_stats[date_str]['sent'] += 1
            elif message.state == 'delivered':
                daily_stats[date_str]['delivered'] += 1
            elif message.state == 'error':
                daily_stats[date_str]['failed'] += 1
            
            daily_stats[date_str]['cost'] += message.actual_cost or message.estimated_cost or 0.0
        
        # Convert to list and sort by date
        trend_data = sorted(daily_stats.values(), key=lambda x: x['date'])
        
        return trend_data

    @api.model
    def get_provider_stats(self):
        \"\"\"
        Get statistics by provider
        
        Returns:
            list: Provider statistics
        \"\"\"
        providers = self.env['sms.provider'].search([('active', '=', True)])
        provider_stats = []
        
        for provider in providers:
            messages = self.env['sms.message'].search([
                ('provider_id', '=', provider.id)
            ])
            
            sent_count = len(messages.filtered(lambda m: m.state in ['sent', 'delivered']))
            delivered_count = len(messages.filtered(lambda m: m.state == 'delivered'))
            error_count = len(messages.filtered(lambda m: m.state == 'error'))
            total_cost = sum(messages.mapped('actual_cost')) or sum(messages.mapped('estimated_cost')) or 0.0
            
            delivery_rate = 0.0
            if sent_count > 0:
                delivery_rate = (delivered_count / sent_count) * 100
            
            provider_stats.append({
                'provider_name': provider.name,
                'provider_type': provider.provider_type,
                'total_sent': sent_count,
                'delivered': delivered_count,
                'failed': error_count,
                'total_cost': total_cost,
                'delivery_rate': round(delivery_rate, 2),
                'balance': provider.balance
            })
        
        return provider_stats

    @api.model
    def get_campaign_stats(self):
        \"\"\"
        Get statistics by campaign
        
        Returns:
            list: Campaign statistics
        \"\"\"
        campaigns = self.env['sms.campaign'].search([])
        campaign_stats = []
        
        for campaign in campaigns:
            campaign_stats.append({
                'campaign_name': campaign.name,
                'state': campaign.state,
                'sent_count': campaign.sent_count,
                'delivered_count': campaign.delivered_count,
                'failed_count': campaign.failed_count,
                'total_cost': campaign.total_cost,
                'delivery_rate': campaign.delivery_rate
            })
        
        return campaign_stats

"""

# Adicionar métodos ao final da classe, antes do último método
if 'def get_realtime_stats' not in dashboard_content:
    # Adicionar antes do último método ou no final da classe
    pattern = r'(    @api\.model\s+def get_dashboard_summary\(self.*?        \}\n)'
    if re.search(pattern, dashboard_content, re.DOTALL):
        replacement = r'\1' + dashboard_methods
        dashboard_content = re.sub(pattern, replacement, dashboard_content, flags=re.DOTALL)
        print("✅ Métodos de dashboard em tempo real adicionados")
    else:
        # Adicionar no final da classe
        pattern = r'(    @api\.model\s+def get_provider_comparison\(self.*?        return list\(provider_stats\.values\(\)\)\n    \})'
        if re.search(pattern, dashboard_content, re.DOTALL):
            replacement = r'\1' + dashboard_methods
            dashboard_content = re.sub(pattern, replacement, dashboard_content, flags=re.DOTALL)
            print("✅ Métodos de dashboard em tempo real adicionados")
        else:
            # Adicionar antes do último fechamento de classe
            dashboard_content = dashboard_content.rstrip() + '\n' + dashboard_methods + '\n'
            print("✅ Métodos de dashboard em tempo real adicionados no final")

# Salvar dashboard modificado
with open('/tmp/sms_dashboard_realtime.py', 'w') as f:
    f.write(dashboard_content)

print("\n✅ Arquivo modificado criado:")
print("   - /tmp/sms_dashboard_realtime.py")

