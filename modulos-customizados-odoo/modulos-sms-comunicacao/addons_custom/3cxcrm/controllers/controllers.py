from odoo import http, _
import logging
import json
from odoo.http import HttpRequest, request, JsonRequest, Response
from odoo.tools import date_utils
import datetime  
from werkzeug.exceptions import BadRequest


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
    @http.route('/api/3cx/crm', auth='public', csrf=False, type='json', methods=['POST'])
    def odoo_3cx_query (self, ** kw):
        
        token = request.env.ref('3cxcrm.token_3cx_crm').sudo().value
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        data = json.loads(request.httprequest.data) 
        apikey = request.httprequest.headers.get('apikey')
        _logger.debug("+++++++++++++++++++++REQUEST+++++++++++++++++++++++")
        _logger.debug(data)

        number = str(data.get('number'))
        if apikey:
            if not apikey == token:
                return BadRequest('Wrong APIKEY')
            else:
                return self.search_contact(number)

        return BadRequest('ApiKey not set')
          
    @http.route('/3cx', auth='public', csrf=False, type='http', methods=['GET'])
    def odoo_3cx_get_partner(self, number=None, **kw):
        number = str(number)
        if number:
            data = self.search_contact(number)
            if 'web_url' in data:
                return request.redirect(data['web_url'])
            else:
                return BadRequest('web_url not available')
        return BadRequest('Number not provided')
    
    def search_contact(self,number):
        partner_action_id = request.env.ref('contacts.action_contacts')
        contact_realcred = request.env['contacts.realcred.batch'].with_user(1).search(
            [ '|' ,  ('telefone1','=', number) ,  ('whatsapp1','=', number)]
            ,order='create_date DESC',limit=1)
        res_partner = request.env['res.partner'].with_user(1).search([('phone_mobile_search','=', number)],limit=1)

        _logger.info("++++++++++++++++++++++++++++++++++++++++")
        _logger.info(number)
        _logger.info(contact_realcred)
        _logger.info(res_partner)
        #validacion si existe en contact_realcred y en res_partner
        if contact_realcred :
            if res_partner :
                print('res_partner', res_partner)
                #self.write_partner_from_batch(contact_realcred,res_partner)
                b = res_partner
                link = f"web#id={b.id}&model=res.partner&view_type=form&action={partner_action_id.id}"
                company = ""
                if b.company_type == "company":
                    company = b.name
                else:
                    company = ""
                data={
                    'partner_id': f"{b.id}",
                    'type' : b.type,
                    #'firstname' :  b.firstname if b.firstname else '',
                    #'lastname': b.lastname if b.lastname  else '',
                    'mobile': b.mobile if b.mobile else '',
                    'phone' : b.phone if b.phone else '',
                    'email': b.email if b.email else '',
                    'web_url': f"{request.httprequest.url_root}{link}",
                    'company_type': b.company_type if b.company_type == "company" else '',
                    'name': company,
                    # 'link_end': 'link_end'
                }
                self.create_lead(b,number)
                return data
            else:

                
                new_partner = self.create_partner_from_batch(contact_realcred)
                link = f"web#id={new_partner.id}&model=res.partner&view_type=form&action={partner_action_id.id}"
                data={
                    'partner_id': f"L{new_partner.id}",
                    'type' : new_partner.type,
                    'name' :  new_partner.name if new_partner.name else new_partner.name,
                    'contact_name': new_partner.name if new_partner.name  else '',
                    'mobile': new_partner.mobile if new_partner.mobile else '',
                    'phone' : new_partner.phone if new_partner.phone else '',
                    'web_url': f"{request.httprequest.url_root}{link}",
                    'link_end': 'link_end'
                }
                self.create_lead(new_partner,number)
                return data
        
        


        
        #crm_lead = request.env['crm.lead'].with_user(1).search([('phone_mobile_search','ilike', number)],limit=1)
        
        partner_action_id = request.env.ref('contacts.action_contacts')
        crm_action_id = request.env.ref('crm.crm_lead_all_leads')
        
        if res_partner:
            print('res_partner', res_partner)
            b = res_partner
            link = f"web#id={b.id}&model=res.partner&view_type=form&action={partner_action_id.id}"
            company = ""
            if b.company_type == "company":
                company = b.name
            else:
                company = ""
            data={
                'partner_id': f"{b.id}",
                'type' : b.type,
                #'firstname' :  b.firstname if b.firstname else '',
                #'lastname': b.lastname if b.lastname  else '',
                'mobile': b.mobile if b.mobile else '',
                'phone' : b.phone if b.phone else '',
                'email': b.email if b.email else '',
                'web_url': f"{request.httprequest.url_root}{link}",
                'company_type': b.company_type if b.company_type == "company" else '',
                'name': company,
                # 'link_end': 'link_end'
            }
            self.create_lead(b,number)
            return data
            """
            
            elif crm_lead:
                print('crm_lead',crm_lead)
                b = crm_lead
                if b.type == 'lead':
                    link = f"web#id={b.id}&model=crm.lead&view_type=form&action={crm_action_id.id}"
                elif b.type == 'opportunity':
                    link = f"web#id={b.id}&model=crm.lead&view_type=form&action={crm_action_id.id}"

                data={
                    'partner_id': f"L{b.id}",
                    'type' : b.type,
                    'name' :  b.contact_name if b.contact_name else b.name,
                    'contact_name': b.name if b.name  else '',
                    'mobile': b.mobile if b.mobile else '',
                    'phone' : b.phone if b.phone else '',
                    'web_url': f"{request.httprequest.url_root}{link}",
                    'link_end': 'link_end'
                }
                return data
            """
        else:
            partner_action_id = request.env.ref('contacts.action_contacts')
            new_partner = request.env['res.partner'].with_user(1).create(
                {
                    'name' : '3CX Contact',
                    'mobile' : number ,
                    'phone' : number 
                }
            )
            link = f"web#id={new_partner.id}&model=res.partner&view_type=form&action={partner_action_id.id}"
            data={
                'partner_id': f"L{new_partner.id}",
                'type' : new_partner.type,
                'name' :  new_partner.name if new_partner.name else new_partner.name,
                'contact_name': new_partner.name if new_partner.name  else '',
                'mobile': new_partner.mobile if new_partner.mobile else '',
                'phone' : new_partner.phone if new_partner.phone else '',
                'web_url': f"{request.httprequest.url_root}{link}",
                'link_end': 'link_end'
            }
            self.create_lead(new_partner,number)
            return data
        
    def create_partner_from_batch(self,contact_batch):

        new_partner = request.env['res.partner'].with_user(1).create({
            'name': contact_batch.name,
            'phone_mobile_search': contact_batch.telefone1,
            'phone': contact_batch.telefone1,
            'mobile': contact_batch.whatsapp1,
            'mother_name': contact_batch.nome_mae,
            'cpf': contact_batch.cpf,
            #'cnpj_cpf': contact_batch.cpf,
            'date_birth': contact_batch.date_birth,
            'especie_beneficio': contact_batch.especie,
            'numero_matricula': contact_batch.nb,
            'nb': contact_batch.nb,
            'situacao_beneficio': contact_batch.situacao_cpf,
            'data_despacho_beneficio': str(contact_batch.data_ddb),
            'data_ddb': contact_batch.data_ddb,
            'salario': contact_batch.salario,
            'marital': contact_batch.type_sex,
        })

        return new_partner
    
    
    def write_partner_from_batch(self,contact_batch,partner):

        write_partner = partner.with_user(1).write({
            'name': contact_batch.name,
            'phone_mobile_search': contact_batch.telefone1,
            'phone': contact_batch.telefone1,
            'mobile': contact_batch.whatsapp1,
            'mother_name': contact_batch.nome_mae,
            'cpf': contact_batch.cpf,
            #'cnpj_cpf': contact_batch.cpf,
            'date_birth': contact_batch.date_birth,
            'especie_beneficio': contact_batch.especie,
            'numero_matricula': contact_batch.nb,
            'nb': contact_batch.nb,
            'situacao_beneficio': contact_batch.situacao_cpf,
            'data_despacho_beneficio': str(contact_batch.data_ddb),
            'data_ddb': contact_batch.data_ddb,
            'salario': contact_batch.salario,
            'marital': contact_batch.type_sex,
            
        })

        return write_partner
    
    def create_lead(self, data,number):
        try:
            return
            name_lead = f"Chamadas 800- {number}"
            exists_lead = request.env['crm.lead'].with_user(1).search([('name','=', name_lead)],limit=1)
            if not exists_lead:
                crm = request.env['crm.lead'].with_user(1).create(
                    {
                    'team_id' : 11,
                    'stage_id': 76,
                    'type' : 'opportunity',
                    'name' : name_lead, 
                    #'cpf'  : contact_realcred.cpf if contact_realcred.cpf  else None,
                    'partner_id' : data.id , 
                    #'expected_revenue' : valor_numerico,
                    'phone' : number,
                    #'kolmeya_id' : response["id"],
                    #'kolmeya_job_id' : response["job"]
                    }
                )

        except:
            pass

    ####odoo crm.lead search lead
    #query = request.env['crm.lead'].with_user(1).search([('phone_mobile_search','ilike', '39358')])



        # dato = data.get('messages','')
        # print(dato)
        # for msg in dato:
        #     date = datetime.datetime.fromtimestamp( msg.get('date','') ) 
        #     request.env['wa.message'].sudo().create({
        #         'id_mp': msg.get('id',''),
        #         'messenger': msg.get('messenger',''),
        #         'usernumber': msg.get('usernumber',''),
        #         'date': date,
        #         'attachment': msg.get('attachment',''),
        #         'attachment_type': msg.get('attachment_type',''),
        #         'text': msg.get('text',''),
        #         'welcome': msg.get('welcome',''),
        #         'userstatus': msg.get('userstatus',''),
        #         'chatid': msg.get('chat_id',''),
        #         'is_retry': msg.get('is_retry',''),
        #         'ticket_id': msg.get('ticket_id',''),
        #         'ticket_status': msg.get('ticket_status',''),
        #         'agent_id': msg.get('agent_id',''),
        #         'inbound': True,
        #         'outbound': False
                
                
        #     })
        # sender =  msg.get('usernumber','')
        # exist_channel = request.env['mail.channel'].sudo().search([('sender', '=', sender)])
        # print('exist_channel',exist_channel)
        # if exist_channel:
        #     self.send_to_channel( msg.get('text',''), exist_channel.id)
        # else:
        #     aaa = self.search_sender(sender)
            
            
        #     new_channel = self.channel_create( aaa+" "+sender, sender, privacy='public')
            
        #     self.send_to_channel( msg.get('text',''), new_channel.get('id',''))
        #print("response", response)


   

 
    @http.route('/api/cw', auth='public', csrf=False, type='json', methods=['POST'])
    def odoo_cw_post(self, **kw):
        try:
            _logger.debug("+++++++++++++++++++++REQUEST POST+++++++++++++++++++++++")
            data = request.jsonrequest
            _logger.debug(data)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/cw', auth='public', csrf=False, type='http', methods=['GET'])
    def odoo_cw_get(self, **kw):
        try:
            _logger.debug("+++++++++++++++++++++REQUEST GET+++++++++++++++++++++++")
            data = request.params
            _logger.debug(data)
            return request.make_response(
                json.dumps({"status": "success", "data": data}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
    