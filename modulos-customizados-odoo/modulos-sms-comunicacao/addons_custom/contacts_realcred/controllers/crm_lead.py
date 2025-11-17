from odoo import http, _
import logging
import json
from odoo.http import HttpRequest, request, JsonRequest, Response
from odoo.tools import date_utils
import datetime  
from werkzeug.exceptions import BadRequest
import re
import simplejson
_logger = logging.getLogger(__name__)

def alternative_json_response(self, result=None, error=None):
    if error is not None:
        response = error
    if result is not None:
        response = result
    mime = 'application/json'
    body = json.dumps(response, default=date_utils.json_default)
    return Response(
        body, status=error and error.pop('http_status', 200) or 200,
        headers=[('Content-Type', mime), ('Content-Length', len(body))]
    )

class Odoo3cxCrm(http.Controller):

    @http.route('/api/crm', auth='public', csrf=False, type='http')
    def odoo_api_crm (self, ** kw):

        token = "0816a247-2e3d-44b6-a501-de3eb9e281c3" #request.env.ref('crm.token_crm').sudo().value
        #request._json_response = alternative_json_response.__get__(request, JsonRequest)
        #datas = json.loads(request.httprequest.data) 
        apikey = request.httprequest.headers.get('apikey')
        _logger.info(token)
        data = [] 
        if apikey:
            if not apikey == token:
                return BadRequest('Wrong APIKEY')
            else:
                 #opportunity lead
                fecha_modificacion = kw.get('ultima_modificacao')
                fecha_creacion = kw.get('fecha_creacion')
                _logger.info(fecha_modificacion)
                crm_leads = []
                if(fecha_modificacion):
                    try:
                        fecha_hora_dt = datetime.datetime.strptime(fecha_modificacion, '%Y-%m-%dT%H:%M:%S')
                    except ValueError:
                        fecha_hora_dt = datetime.datetime.strptime(fecha_modificacion, '%Y-%m-%d') + datetime.timedelta(hours=0)
                        
                    crm_leads = request.env['crm.lead'].with_user(2).search([
                        #('create_date', '>=', fecha_inicio),
                        ('write_date', '>=', fecha_hora_dt),
                        ('team_id', '=', 11),
                        ('type', '=', 'opportunity'),
                        ('url_origen','!=',False)
                    ])

                elif(fecha_creacion):
                    try:
                        fecha_hora_dt = datetime.datetime.strptime(fecha_creacion, '%Y-%m-%dT%H:%M:%S')
                    except ValueError:
                        fecha_hora_dt = datetime.datetime.strptime(fecha_creacion, '%Y-%m-%d') + datetime.timedelta(hours=0)
                        
                    crm_leads = request.env['crm.lead'].with_user(2).search([
                        #('create_date', '>=', fecha_inicio),
                        ('create_date', '>=', fecha_hora_dt),
                        ('team_id', '=', 11),
                        ('type', '=', 'opportunity'),
                        ('url_origen','!=',False)
                    ])
                else:
                    crm_leads = request.env['crm.lead'].with_user(2).search([('url_origen','!=',False),('team_id','=', 11 ), ('type' ,'=','opportunity')])
                if crm_leads :
                     
                    for crm_lead in crm_leads :
                        b = crm_lead
                        #link = f"web#id={b.id}&model=res.partner&view_type=form&action={partner_action_id.id}"
                        write_date = b.write_date

                        if write_date:
                            # Convertimos la fecha y hora a un objeto datetime
                            dt = datetime.datetime.strptime(write_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

                            # Convertimos el objeto datetime a una cadena ISO 8601
                            dt_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
                        else:
                            # Si write_date está vacío, asignamos None a dt_str
                            dt_str = None
                        
                        createDate=b.create_date
                        create_date = datetime.datetime.strptime(createDate.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        create_date = create_date.strftime('%Y-%m-%dT%H:%M:%S')

                        dataCrm={
                            'id': f"L{b.id}",
                            #'type' : b.type,
                            #'name' :  b.contact_name if b.contact_name else b.name,
                            #'contact_name': b.name if b.name  else '',
                            'valor_desejado': b.expected_revenue if b.expected_revenue else '',
                            'valor_contratado' : '' ,
                            'resultado_negociacao'  : '' ,
                            'perfil' :  b.perfil if b.perfil else '',
                            'produto_contratado' :  b.producto if b.producto else '',
                            'banco_contrato'  : '' ,
                            #'phone' : b.phone if b.phone else '',
                            'ultima_modificacao' : dt_str  ,
                            'fecha_creacion' : create_date  ,
                            'link_conversao': b.url_origen  if b.url_origen else '',  #f"{request.httprequest.url_root}{link}"
                        }
                        data.append(dataCrm)
                    return Response(simplejson.dumps({'total' : len(data)  , 'data':data}),
                                content_type='application/json;charset=utf-8',
                                status=200)
            
        return Response(simplejson.dumps({'total' : len(data)  , 'data':data}),
                                content_type='application/json;charset=utf-8',
                                status=404)