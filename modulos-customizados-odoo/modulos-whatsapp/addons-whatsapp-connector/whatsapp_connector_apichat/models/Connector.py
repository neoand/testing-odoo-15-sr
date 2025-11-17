# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.whatsapp_connector.tools import log_request_error


class AcruxChatConnector(models.Model):
    _inherit = 'acrux.chat.connector'

    is_direct_connection = fields.Boolean('Direct apichat.io', default=True)

    @api.constrains('is_direct_connection', 'connector_type', 'endpoint')
    def constrains_is_direct_connection(self):
        for r in self:
            if r.is_direct_connection:
                if r.connector_type != 'apichat.io':
                    raise ValidationError(_('You have checked \'Direct Connect\'. '
                                            'In field \'Connect to\' select ApiChat.io'))
                endpoint = (r.endpoint or '').strip('/')
                regex = r"^http:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/v1$"
                if endpoint != 'https://api.apichat.io/v1' and not re.match(regex, endpoint):
                    raise ValidationError(_('Please check your api endpoint. Enter https://api.apichat.io/v1 or IP'))

    def get_headers(self, path=''):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            out = self.apichat_get_headers()
        else:
            out = super(AcruxChatConnector, self).get_headers(path)
        return out

    def get_api_url(self, path=''):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            out = self.apichat_api_url(path)
        else:
            out = super(AcruxChatConnector, self).get_api_url(path)
        return out

    def ca_get_status(self):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            out = self.apichat_get_status()
        else:
            out = super(AcruxChatConnector, self).ca_get_status()
        return out

    def ca_set_logout(self):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            out = self.apichat_set_logout()
        else:
            out = super(AcruxChatConnector, self).ca_set_logout()
        return out

    def get_actions(self):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            out = self.apichat_get_actions()
        else:
            out = super(AcruxChatConnector, self).get_actions()
        return out

    def ca_set_settings(self):
        '''
            :overide
        '''
        self.ensure_one()
        out = None
        if self.apichat_is_direct():
            out = self.apichat_set_settings()
        else:
            out = super(AcruxChatConnector, self).ca_set_settings()
        return out

    def hook_request_args(self, args):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            out = args
        else:
            out = super(AcruxChatConnector, self).hook_request_args(args)
        return out

    def ca_get_chat_list(self):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            self.apichat_get_chat_list()
        else:
            super(AcruxChatConnector, self).ca_get_chat_list()

    def response_handler(self, req):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            if req.status_code == 200:
                try:
                    out = req.json()
                except ValueError as _e:
                    out = {}
                if out and 'send' in req.url:
                    out['msg_id'] = out['id']
                    del out['id']
            else:
                log_request_error([req.text or req.reason], req)
                raise ValidationError(req.text or req.reason)
        else:
            out = super(AcruxChatConnector, self).response_handler(req)
        return out

    def ca_request(self, path, data={}, params={}, timeout=False, ignore_exception=False):
        '''
            :overide
        '''
        self.ensure_one()
        if self.apichat_is_direct():
            if path == 'send':
                path = 'send' + data['type'].title()
                if 'quote_msg_id' in data:
                    del data['quote_msg_id']
                if 'quote_msg_obj' in data:
                    data['quote_msg'] = {
                        'from_me': data['quote_msg_obj'].from_me,
                        'number': data['quote_msg_obj'].contact_id.number,
                        'msg_id': data['quote_msg_obj'].msgid
                    }
                    del data['quote_msg_obj']
                del data['type']
            elif path == 'msg_set_read':
                path = 'readChat'
                data['number'] = data['phone']
                del data['phone']
            elif path == 'delete_message':
                path = 'deleteMessage'
                params = {
                    'number': params.get('number'),
                    'msgId': params.get('msg_id'),
                    'fromMe': params.get('from_me'),
                    'forMe': params.get('for_me'),
                }
        vals = {
            'path': path,
            'data': data,
            'params': params,
            'timeout': timeout,
            'ignore_exception': ignore_exception
        }
        return super(AcruxChatConnector, self).ca_request(**vals)

    def apichat_is_direct(self):
        self.ensure_one()
        return self.is_direct_connection and self.connector_type == 'apichat.io'

    def apichat_get_headers(self):
        self.ensure_one()
        return {
            'Accept': 'application/json',
            'token': self.token,
            'client-id': self.uuid,
            'Content-Type': 'application/json'
        }

    def apichat_api_url(self, path):
        self.ensure_one()
        return '%s/%s' % (self.endpoint.strip('/'), path)

    @api.model
    def apichat_get_actions(self):
        return {
            'status': 'get',
            'account': 'put',
            'logout': 'post',
            'conversations': 'get',
            'sendText': 'post',
            'sendAudio': 'post',
            'sendFile': 'post',
            'sendImage': 'post',
            'sendVideo': 'post',
            'sendLocation': 'post',
            'readChat': 'post',
            'deleteMessage': 'delete',
        }

    def apichat_set_logout(self):
        self.ensure_one()
        self.ca_request('logout', timeout=20)
        self.ca_status = False
        self.ca_qr_code = False

    def apichat_get_status(self):
        self.ensure_one()
        if self.connector_type == 'not_set':
            raise ValidationError(_('"Connect to" is not set, check out your config.'))
        Pop = self.env['acrux.chat.pop.message']
        message = detail = False
        self.ca_qr_code = False
        data = self.ca_request('status', timeout=20)
        if 'is_connected' in data:
            if data['is_connected']:
                detail = _('Connected.')
                message = 'Status'
                self.ca_status = True
                self.message = detail
                self.ca_set_settings()
            else:
                message = 'Status'
                detail = data.get('reason', _('An unexpected error occurred'))
                self.ca_status = False
                self.message = detail
        elif 'qr' in data:
            self.ca_status = False
            qrCode = data.get('qr')
            self.ca_qr_code = qrCode.split('base64,')[1]
            self.message = 'Please Scan QR code'
        else:
            self.ca_status = False
            message = 'An unexpected error occurred. Please try again.'
            self.message = message
        return Pop.message(message, detail) if message else True

    def apichat_set_settings(self):
        self.env.cr.commit()
        self.ensure_one()
        data = {
            'webhook': '%s/apichat/whatsapp_connector/%s' % (self.odoo_url.rstrip('/'), self.uuid),
            'notify_ack': False,
            'notify_phone_status': True,
            'is_chatapi': False,
            'notify_chat_update': False,
            'notify_from_me_message': False,
            'tz': self.tz,
            'notify_format': {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': '%s',
                'id': False
            }
        }
        self.ca_request('account', data)

    def apichat_get_chat_list(self):
        self.ensure_one()
        values = {}
        index = 0
        data = self.ca_request('conversations', params={'page': index})
        while data:
            vals = {
                user['number']: {
                    'name': user.get('name'),
                    'image_url': user.get('image'),
                } for user in data
            }
            values.update(vals)
            index = index + 1
            data = self.ca_request('conversations', params={'page': index})
        if values:
            self.process_chat_list(vals)
