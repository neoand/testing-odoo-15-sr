import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
from itertools import groupby
import calendar
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import json
import logging
_logger = logging.getLogger(__name__)
import xmlrpc.client
import base64
import requests
import re
import pytz

URL_ASSERTIVA = 'https://api.assertivasolucoes.com.br/oauth2/v3/token'
USERNAME_ASSERTIVA = '/HZQkb+a9RwtrAYya0sGugxrz9hZfjdR3QrGgkihDfkUgiHi3m8aSYmcpET8yOv5haHzXTwKiTHejxrBgj1CRQ=='
PASSWORD_ASSERTIVA = 'G0H+NHtiVKJOxPlQTInPXVlfW1IUT+U66kvZ7w5EfZMVS6+h2x62T13O0E0uu835yKa4APE5pwo1WAgMyyrGqQ=='



class MailMessage(models.Model):
    _inherit = 'mail.message'


    @api.model
    def create(self, vals):
        
        _logger.info("*********************Creando mail message****************")
        _logger.info( self )
        _logger.info( vals )
        res = super(MailMessage, self).create(vals)
        #self._cr.commit()
        try:
            if 'email_from' in vals :
                email_from = vals.get('email_from') 
                match = re.search(r'[\w\.-]+@[\w\.-]+', email_from)
                if match and match.group() == 'crmodoo@realcredemprestimo.com.br':
                    _logger.info("*********************realcredemprestimo****************")

                    # self.env['mail.message']
                    email_body = res.body if res.body else False
                    if email_body:

                        _logger.info("*********************body****************")
                        _logger.info(email_body)
                        lineas = email_body.split("\n")
                        # Crear un diccionario para almacenar los valores
                        valores = {}
                        lineas = email_body.split("<br>")
                        for linea in lineas:
                            indice = linea.find(":")
                            if indice != -1:
                                clave = linea[:indice].strip()
                                clave = re.sub(r'[^\w\s]', '', clave).strip().lower().replace(' ', '_')
                                valor = linea[indice+1:].strip()
                                valores[clave] = valor
                        _logger.info(valores)
                        email_message = self.env['crm.lead'].browse(res.res_id)
                        email_message = self.env['crm.lead'].browse(res.res_id)
                        if 'pquanto_você_precisa' in valores:
                            valor_str = valores['pquanto_você_precisa']
                            valor_str = valor_str.replace('.', '')
                            valor_str = valor_str.replace(',', '.')
                            valores['pquanto_você_precisa'] = float(valor_str)  # Convertir la cadena a un flotante
                        if 'telefone' in valores:
                            valores['telefone'] = re.sub(r"\D", "", valores['telefone'])

                        nome_completo = ""
                        if 'nome' in valores:
                            nome_completo += valores['nome']
                        if 'pnome' in valores:
                            nome_completo += " " + valores['pnome']

                        email_message.update({
                            'name': f"{email_message.name} - {nome_completo}",
                            'partner_id' : self.validatePartner(valores) , 
                            'cpf'  :  valores.get('cpf') if valores.get('cpf') else None   ,
                            'perfil'  :  valores.get('qual_o_seu_perfil') if valores.get('qual_o_seu_perfil') else None   ,
                            'expected_revenue': valores.get('pquanto_você_precisa'),
                            'phone' : valores.get('telefone') , 
                            'url_origen' : valores.get('url_da_página') 
                        })
                        _logger.info("*********************crm lead****************")
                        _logger.info(email_message)
                        _logger.info(valores)

        except Exception as e:
            _logger.info("*********ERROR*********")
            _logger.info(e)
            pass  # or you could use 'continue'

        return res

    def validatePartner(self,data):
        cpf = None
        
        if data.get('cpf')  : 
            cpf = re.sub("[^0-9]", "", data["cpf"])
        name = None

        if data.get('nome') or data.get('pnome') :
            name = ( data.get('nome') or data.get('pnome') or '')

        exist_cpf = self.env['res.partner'].search(['|',('name','=',name) , ('cpf','=',cpf)], limit = 1)
        if not exist_cpf:
            contact = self.env['res.partner'].create(
                {
                    'name' : name ,
                    'cpf' : cpf 
                }
            )
            return contact.id
        else:
            return exist_cpf.id


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    cpf = fields.Char('CPF' )
    url_origen = fields.Char('URL origem')
    producto = fields.Char('Producto')
    perfil = fields.Char('Producto')
    kolmeya_id = fields.Integer('ID kolmeya')
    kolmeya_job_id = fields.Integer('ID JOB kolmeya')
    
    teamuser_id = fields.Many2one("res.users", string="Consultor que atende" )

    is_admin = fields.Boolean(string="check field", compute='get_user')

    def get_user(self):

        if self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            self.is_admin = True
        else:
            self.is_admin = False


    def action_atribuir_venda(self):
        self.ensure_one()
        self.teamuser_id = self.env.user.id
        self.user_id = self.env.user.id

        data_hora = pytz.utc.localize(datetime.now()).astimezone(pytz.timezone(self.env.user.tz))
        data_hora = data_hora.strftime('%Y-%m-%d %H:%M:%S')

        message = "<ul class='o_Message_trackingValues'>"
        message += f"""<li><div class='o_Message_trackingValue'><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem">Consultor que atende:</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">{self.env.user.name}</div> </div></li>"""
        message += f"""<li><div class='o_Message_trackingValue'><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem">Data e hora:</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">{data_hora}</div> </div></li>"""
        message += "</ul>"
        self.message_post(body=message)

        #teams = self.env['crm.team'].search([
        #     '|', ('user_id', '=', self.env.user.id), ('member_ids', 'in', [self.env.user.id])
        #)
        #self.team_id = teams

    def action_send_api(self):
        self.ensure_one()
        env = self.env['mt.wizzard.api'].with_context(active_model=self._name, active_id=self.id)
        model_action = env.create({})
        return {
            'name': "Consulta por CPF",
            'type': 'ir.actions.act_window',
            'res_model': 'mt.wizzard.api',
            'res_id': model_action.id,
            'view_mode': 'form',
            'views': [(False,'form')],
            'target': 'new',
        }

    @api.model
    def getSmsKolmeya(self):

        url = f'https://kolmeya.com.br/api/v1/sms/replys-web'
        payload={}
        headers = {
            'Authorization': 'Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY'
        }

        # Add retry logic for connection issues
        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
                break  # Success, exit retry loop
            except requests.exceptions.ConnectionError as e:
                _logger.warning(f"Kolmeya API connection error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                else:
                    _logger.error(f"Kolmeya API connection failed after {max_retries} attempts. This may be temporary maintenance. Will retry next scheduled run.")
                    return False  # Exit gracefully, will retry on next cron run
            except requests.exceptions.Timeout as e:
                _logger.warning(f"Kolmeya API timeout (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                else:
                    _logger.error(f"Kolmeya API timeout after {max_retries} attempts. Will retry next scheduled run.")
                    return False
            except Exception as e:
                _logger.error(f"Unexpected error calling Kolmeya API: {str(e)}")
                return False

        if response.status_code == 200 :
            result_json = response.json()
            responses = result_json['data']
            #auth = self.env['mt.wizzard.api'].auth_assertiva()
            _logger.info("********respuesta  a kolmeya*********")
            _logger.info(responses)
            for response in responses :
                try:
                    _logger.info("+++++++++++++++++++++++++++++++")
                    _logger.info(response)
                    crm_kolmeya = self.search([ ('kolmeya_job_id','=', response["job"] ) ,('phone','=', response["phone"] )  ])
                    if not crm_kolmeya :
            
                        valor = response["parameters"].get("VALOR") if len(response["parameters"]) else ''
                        valor_numerico = 0  
                        if valor:
                            valor_numerico = float(re.sub('[^0-9,]', '', valor  ).replace(',', '.'))

                        exist_contact = self.env['res.partner'].search([ ('phone','=',response["phone"])], limit = 1)
                        contact_realcred = self.env['contacts.realcred.batch'].search([ '|' ,  ('telefone1','=', response["phone"]) ,  ('whatsapp1','=', response["phone"])],order='create_date DESC',limit=1)
                        contactPartner = None
                        if contact_realcred :
                            if not exist_contact:
                                _logger.info("********not exist_contact*********")
                                _logger.info(contact_realcred)
                                new_partner = self.create_partner_from_batch(contact_realcred)
                                contactPartner = new_partner.id
                            """
                            else:
                                self.write_partner_from_batch(contact_realcred,exist_contact)
                                contactPartner =  exist_contact.id
                            """
                        else:
                            if not exist_contact:
                                new_partner = self.env['res.partner'].with_user(1).create({
                                    'name': "Lead não encontrado em base de dados",
                                    'phone': response["phone"],
                                    'mobile': response["phone"],
                                })
                                contactPartner = new_partner.id
                        
                        if contactPartner :

                            message = ".."
                            job_value = response["job"]
                            if job_value:
                                campaign_info = self.env['kolmeya.campaigns'].find_campaign(job_value)
                                message = campaign_info['name']
                                campaign_id = campaign_info['campaign_id']

                            crm = self.env['crm.lead'].create(
                                {
                                'team_id' : 11,
                                'type' : 'opportunity',
                                'name' : f"NOVO LEAD - {response['phone']}", 
                                'cpf'  : contact_realcred.cpf if contact_realcred.cpf  else None,
                                'partner_id' : contactPartner , 
                                'expected_revenue' : valor_numerico,
                                'phone' : response["phone"],
                                'kolmeya_id' : response["id"],
                                'kolmeya_job_id' : response["job"]
                                }
                            )
                            _logger.info("********************************")
                            _logger.info(crm)
                            reply = response["reply"]
                            change_message = "<h5>Resposta SMS:</h5><ul class='o_Message_trackingValues'>"
                            change_message += f"""<li><div class='o_Message_trackingValue'><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem">Campanha:</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">{message}</div> </div></li>"""
                            change_message += f"""<li><div class='o_Message_trackingValue'><div class="o_Message_trackingValueFieldName o_Message_trackingValueItem">Resposta:</div> <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">{reply}</div> </div></li>"""
                            change_message += "</ul>"
                            crm.message_post(body=_(change_message))

                except  Exception as e:
                    _logger.info("++++++++++++++++++++++++++ocurrio un errror ++++++++++++++++++++++++++")
                    _logger.info(e)
        else:
            _logger.warning(f"Kolmeya API returned status code {response.status_code}. Response: {response.text}")
            return False

    def create_partner_from_batch(self,contact_batch):

        new_partner = self.env['res.partner'].with_user(1).create({
            'name': contact_batch.name,
            'phone': contact_batch.telefone1,
            'mobile': contact_batch.whatsapp1,
            'mother_name': contact_batch.nome_mae,
            'cpf': contact_batch.cpf if contact_batch.cpf  else None , 
            'cnpj_cpf': contact_batch.cpf if contact_batch.cpf  else None    , 
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
            'phone': contact_batch.telefone1,
            'mobile': contact_batch.whatsapp1,
            'mother_name': contact_batch.nome_mae,
            'cpf': contact_batch.cpf,
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

class MtWizzardApi(models.TransientModel):
    _name = 'mt.wizzard.api'
    _description = 'Consulta de datos por cpf'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res_id = self.env.context.get('active_id')
        res_model = self.env.context.get('active_model')
        if res_id and res_model:
            res.update({'res_model': res_model, 'res_id': res_id})
        return res
        
        
    res_model = fields.Char("Related Document Model", required=True)
    res_id = fields.Integer("Related Document ID", required=True)

    cpf = fields.Char('CPF' )

    def auth_assertiva(self):
        try:

            url = URL_ASSERTIVA
            payload='grant_type=client_credentials'
            headers = {
            'Authorization': 'Basic L0haUWtiK2E5Und0ckFZeWEwc0d1Z3hyejloWmZqZFIzUXJHZ2tpaERma1VnaUhpM204YVNZbWNwRVQ4eU92NWhhSHpYVHdLaVRIZWp4ckJnajFDUlE9PTpHMEgrTkh0aVZLSk94UGxRVEluUFhWbGZXMUlVVCtVNjZrdlo3dzVFZlpNVlM2K2gyeDYyVDEzTzBFMHV1ODM1eUthNEFQRTVwd28xV0FnTXl5ckdxUT09',
            'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 200 :
                result_json = response.json()
                _logger.debug(result_json)
                result_json['access_token']
                return result_json['access_token']
            else:
                _logger.info( f'Ha ocurrido un error al consultar la informacion : {response.text}')
                return False ; 

        except  Exception as e:
            _logger.info("++++++++++++++++++++++++++ocurrio un errror ++++++++++++++++++++++++++")
            _logger.info(e)
            _logger.info( f'Ha ocurrido un error al consultar la informacion : {response.text}')

            return False ; 

    def send_api(self):

        crm_lead = self.env[self.res_model].browse(self.res_id)
        

        try:
            auth = self.auth_assertiva()
            if auth :
                cpf = re.sub("[^0-9]", "", self.cpf)

                _logger.info("++++++++++++++++++++++++++ CONSULTANDO CPF ++++++++++++++++++++++++++")
                _logger.info(cpf)

                url = f'https://api.assertivasolucoes.com.br/localize/v3/cpf?cpf={cpf}&idFinalidade=1'
                payload={}
                headers = {
                    'Authorization': auth
                }
                response = requests.request("GET", url, headers=headers, data=payload)

                if response.status_code == 200 :
                      



                    result_json = response.json()
                    _logger.debug(result_json)

                    fecha_str = False
                    fecha_str = result_json['resposta']['dadosCadastrais']['dataNascimento']
                    if fecha_str :
                        fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                        fecha_str = fecha_obj.strftime('%Y-%m-%d')

                    if crm_lead.partner_id :
                        crm_lead.partner_id.write({
                                'name': result_json['resposta']['dadosCadastrais']['nome'],
                                'date_birth' :fecha_str ,  
                                'type_sex' : result_json['resposta']['dadosCadastrais']['sexo'] 
                            })
                        crm_lead.update(
                            {
                                'cpf': result_json['resposta']['dadosCadastrais']['cpf'],
                                'email_from' : None 
                            })
                    else:
                        exist_cpf = self.env['res.partner'].search([('cpf','=',cpf)])
                        if exist_cpf :
                            _logger.info("++++++++++++++++++++++++++ exist_cpf ++++++++++++++++++++++++++")
                            crm_lead.update(
                                {
                                    'partner_id' : exist_cpf.id , 
                                    'cpf': result_json['resposta']['dadosCadastrais']['cpf'],
                                    'email_from' : None 
                                })
                        else: 
                            _logger.info("++++++++++++++++++++++++++ NO exist_cpf ++++++++++++++++++++++++++")
                            contact = self.env['res.partner'].create(
                                {
                                'name' : result_json['resposta']['dadosCadastrais']['nome'] ,
                                'date_birth' :fecha_str , 
                                'type_sex' : result_json['resposta']['dadosCadastrais']['sexo'] 
                                }
                            )

                            crm_lead.update(
                                {
                                    'partner_id' : contact.id , 
                                    'cpf': result_json['resposta']['dadosCadastrais']['cpf']
                                })
                            
                            _logger.info("++++++++++++++++++++++++++ FIN de la creación y del registro ++++++++++++++++++++++++++")

                else:
                    if response.status_code == 404 :
                        _logger.debug(response.text)
                    else:
                        result_json = response.json()
                        raise ValidationError( f'Ocorreu um erro ao consultar as informações: {result_json["resposta"]}')


        except  Exception as e:
            _logger.info("++++++++++++++++++++++++++ocurrio un errror++++++++++++++++++++++++++")
            _logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++")
            _logger.info(e)  
            _logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++")

            raise ValidationError( e )
        
