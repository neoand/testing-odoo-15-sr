from odoo import models, fields, api
import json
import requests
import logging

_logger = logging.getLogger(__name__)

class JsonRequestLog(models.Model):
    _name = 'json.request.log'
    _description = 'JSON Request and Response Log'

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL', required=True)
    method = fields.Char(string='HTTP Method', required=True)
    request_data = fields.Text(string='Request Data') 
    response_data = fields.Text(string='Response Data')
    status_code = fields.Integer(string='Response Status Code')
    headers = fields.Text(string='Headers')
    execution_time = fields.Float(string='Execution Time (s)')
    request_time = fields.Datetime(string='Request Time', default=fields.Datetime.now)



class InherintAcruxChatConnector(models.Model):
    _inherit = 'acrux.chat.connector'
    def log_data(self, req_type, url, param, data, header):
        try:
            _logger.debug("****************************************")
            # Registrar los datos de la solicitud
            request_data = {
                'method': req_type,
                'url': url,
                'params': param,
                'data': data,
                'headers': header
            }
            # Convertir los datos a JSON y guardarlos en el log
            self.env['json.request.log'].sudo().create({
                'name': 'API Request Log',
                'url': url,
                'method': req_type,
                'request_data': json.dumps(request_data),
                'headers': json.dumps(header),
                'request_time': fields.Datetime.now()
            })
            self.env.cr.commit()
            _logger.debug(json.dumps(request_data))
            _logger.debug("****************************************")
        except Exception as e:
            # Capturar cualquier excepción y loguearla sin interrumpir la ejecución
            _logger.error(f"Error logging request data: {str(e)}")

    def log_result(self, req_type, url, result, param, data, req):
        try:
            # Registrar los datos de la respuesta
            response_data = {
                'status_code': req.status_code if req else 'N/A',
                'response_body': result
            }
            # Convertir la respuesta a JSON y guardarla en el log
            self.env['json.request.log'].sudo().create({
                'name': 'API Response Log',
                'url': url,
                'method': req_type,
                'response_data': json.dumps(response_data),
                'status_code': req.status_code if req else 'N/A',
                'request_time': fields.Datetime.now()
            })
            self.env.cr.commit()
        except Exception as e:
            # Capturar cualquier excepción y loguearla sin interrumpir la ejecución
            _logger.error(f"Error logging response data: {str(e)}")


