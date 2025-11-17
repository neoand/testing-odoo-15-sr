# -*- coding: utf-8 -*-
from odoo import models, api, tools
from odoo.tools.safe_eval import safe_eval


class ChatMessageWizard(models.TransientModel):
    _inherit = 'acrux.chat.message.wizard'

    @api.model
    def default_get(self, default_fields):
        vals = super(ChatMessageWizard, self).default_get(default_fields)
        if not self.use_template() and 'text' in default_fields and not vals.get('text'):
            if self.env.context.get('active_model') == 'product.product':
                tmpl_id = self.env['mail.template'].search(
                    [('model', '=', 'product.product'), ('name', 'ilike', 'ChatProduct')], limit=1)
                if tmpl_id:
                    web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    product_id = self.env['product.product'].browse(self.env.context.get('active_id'))
                    body = safe_eval(tools.html2plaintext(tmpl_id.body_html), {'object': product_id})
                    vals['text'] = body.replace('MY_ODOO_URL', web_base_url.strip('/'))
        return vals
