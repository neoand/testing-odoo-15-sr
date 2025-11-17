/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

/**
 * SMS Dashboard Widget
 * Provides enhanced dashboard functionality for SMS statistics
 */

export class SMSDashboardWidget extends Component {
    setup() {
        this.state = {
            stats: {},
            loading: false,
        };
    }

    /**
     * Load dashboard statistics
     */
    async loadStats() {
        this.state.loading = true;
        try {
            const result = await this.rpc({
                model: 'sms.dashboard',
                method: 'get_dashboard_summary',
                args: [],
            });
            this.state.stats = result;
        } catch (error) {
            console.error('Error loading SMS dashboard stats:', error);
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Refresh dashboard
     */
    async onRefresh() {
        await this.loadStats();
    }
}

SMSDashboardWidget.template = "chatroom_sms_advanced.SMSDashboardWidget";

// Register the widget
registry.category("fields").add("sms_dashboard_widget", SMSDashboardWidget);

/**
 * Helper functions for SMS formatting
 */
export const SMSHelpers = {
    /**
     * Format phone number for display
     */
    formatPhone(phone) {
        if (!phone) return '';

        // Remove non-digits
        const cleaned = phone.replace(/\D/g, '');

        // Format Brazilian phone: +55 (11) 99999-9999
        if (cleaned.startsWith('55') && cleaned.length === 13) {
            return `+55 (${cleaned.substr(2, 2)}) ${cleaned.substr(4, 5)}-${cleaned.substr(9)}`;
        }

        return phone;
    },

    /**
     * Calculate SMS segments
     */
    calculateSegments(message) {
        if (!message) return 0;
        const length = message.length;
        return Math.ceil(length / 160);
    },

    /**
     * Estimate SMS cost (R$ 0.10 per segment)
     */
    estimateCost(message, recipients = 1) {
        const segments = this.calculateSegments(message);
        return (segments * recipients * 0.10).toFixed(2);
    },

    /**
     * Format delivery rate as percentage
     */
    formatDeliveryRate(delivered, sent) {
        if (!sent || sent === 0) return '0%';
        const rate = (delivered / sent) * 100;
        return rate.toFixed(1) + '%';
    },
};

// Export to global scope for use in templates
window.SMSHelpers = SMSHelpers;

console.log('SMS Advanced Dashboard JS loaded');
