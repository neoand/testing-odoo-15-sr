# -*- coding: utf-8 -*-
from urllib.parse import urljoin
import requests
from email.policy import default
from this import d
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError, Warning
import logging
import calendar
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import time
import babel
from odoo.tools import float_compare, float_is_zero
from odoo.models import BaseModel
from babel.dates import format_date
from json import dumps
from dateutil.relativedelta import relativedelta
import ast
import json
_logger = logging.getLogger(__name__)
from time import sleep
URL_LIMIT = "https://api.lemit.com.br/api/v1/consulta/pessoa/"


class ContactsRealcred(models.Model):
    _name = 'contacts.realcred.batch'

    _order = 'id desc'
    _description = "Contatos RC"

    updated_limit = fields.Boolean( string='Atualizado', default=False , tracking=True)
    name = fields.Char(string='Nome', tracking=True)
    cpf = fields.Char(string='CPF', tracking=True)
    telefone1 = fields.Char(string='Telefone 1', tracking=True)
    whatsapp1 = fields.Char(string='Whatsapp 1', tracking=True)
    type_sex = fields.Selection(
        [('Masculino', 'Masculino'), ('Feminino', 'Feminino'), ], string='Sexo')
    date_birth = fields.Date(string='Data de Nascimento')
    age = fields.Integer(readonly=True, compute="_compute_age",
                         string='Edad', store="True")
    especie = fields.Char(string='Espécie')
    nb = fields.Char(string='Matricula')
    vl_bruto_atrasados = fields.Char(string='Vl Bruto Atrasados')
    salario = fields.Char(string='Salario')
    data_ddb = fields.Date(string='Data do despacho do beneficio')
    uf = fields.Char(string='UF', tracking=True)
    campaing_id = fields.Many2one(comodel_name='contacts.realcred.campaign', string='Campaña')

    nome_mae = fields.Char(string='Nome Mae', tracking=True)
    falecido = fields.Boolean(string='Falecido', tracking=True ,default=False)
    situacao_cpf = fields.Char(string='situacao cpf', tracking=True)
    renda = fields.Char(string='renda', tracking=True)
    ocupacao = fields.Char(string='ocupacao', tracking=True)
    vi_rmi = fields.Monetary(string='VI RMI', tracking=True)
    currency_id = fields.Many2one(comodel_name='res.currency', string='currency')

    margemDisponivel  = fields.Char(string='margemDisponivel', tracking=True)
    margemDisponivelCartao = fields.Char(string='margemDisponivelCartao', tracking=True)
    valorLimiteCartao  = fields.Char(string='valorLimiteCartao', tracking=True)
    elegivelEmprestimo = fields.Boolean(string='elegivelEmprestimo' ,default=False)
    margemDisponivelRcc  = fields.Char(string='margemDisponivelRcc', tracking=True)
    valorLimiteRcc  = fields.Char(string='valorLimiteRcc', tracking=True)
    cpf_id = fields.Many2one('res.partner', 'Cpfs')

    @api.depends("date_birth")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.date_birth:
                age = relativedelta(fields.Date.today(),
                                    record.date_birth).years
            record.age = age

    @api.model
    def create_campaing(self):
        if len(self) > 1:
            campaign = self[0].env['contacts.realcred.campaign'].create({
                'name_campaign': 'Nova campanha',
                'state_update_info': 'draft',
                'contacts_realcred_campaign_ids': self
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'contacts.realcred.campaign',
                'res_id': campaign.id,
                'view_mode': 'form',
                'target': 'current',

            }


class ContactsRealcredCampaign(models.Model):
    _name = 'contacts.realcred.campaign'

    _rec_name = "name_campaign"
    _order = 'id desc'
    _description = "Contatos RC Campaign"

    state_update_info = fields.Selection(string='State', selection=[('draft', 'Rascunho'), (
        'process', 'En Proceso de Atualização'), ('updated', 'Informacion atualizada')], default='draft', track_visibility='always')
    state_sms = fields.Selection(string='State', selection=[('draft', 'Rascunho'), (
        'process', 'Enviando'), ('finished', 'Enviado')], default='draft', track_visibility='always')
    name_campaign = fields.Char(string='Nome da Campanha', tracking=True)
    contacts_realcred_campaign_ids = fields.One2many(
        'contacts.realcred.batch', 'campaing_id', string='Cotacto', tracking=True, )
    # webhook_sms
    message = fields.Text(string='Mensaje')

    def action_send_campaign(self) :
        self.state_sms = 'process'

    @api.model
    def check_data_kolmeya_send(self):
        all = self.env['contacts.realcred.campaign'].search([('state_sms', '=' ,'process')])
        for rec in all:

            lines = []
            count = 0
            for contact in rec.contacts_realcred_campaign_ids:
                if contact.telefone1 and contact.updated_limit and contact.falecido == False :
                    # Replace name
                    message_name = rec.message.replace('|NOME|', contact.name.strip())

                    # Replace CPF
                    message_cpf = message_name.replace('|CPF|', str(contact.cpf))
                    # Replace VI_RM
                    full_message = message_cpf.replace('|VI_RM|', str(contact.vi_rmi))

                    lines.append({
                        'phone': contact.telefone1.strip(),
                        'message': full_message.strip(),
                        'reference': count
                    })

                    count +=1

            data = {
                'reference': rec.name_campaign,
                'messages': lines
            }
            rec.state_sms = 'finished'
            _logger.debug('++++++++++++++++++++++++')
            _logger.debug( data)
            _logger.debug( count)
            _logger.debug('++++++++++++++++++++++++')


    def send_info_limit(self):

        self.state_update_info = 'process'
        for contact in self.contacts_realcred_campaign_ids:
            payload = {}
            headers = {
                'Authorization': 'Bearer atoBgWaA24foyyeSaIXwhWST74uJWuQhOF8Lp6kV'
            }

            url = urljoin(URL_LIMIT, contact.cpf)
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            if response.status_code == 200 :
                result_json = response.json()
                _logger.debug(result_json['pessoa'])
                contact.update(
                    {
                        'nome_mae': result_json['pessoa']['nome_mae'],
                        'falecido': result_json['pessoa']['falecido'],
                        'situacao_cpf': result_json['pessoa']['situacao_cpf'],
                        'renda': result_json['pessoa']['renda'],
                        'ocupacao': result_json['pessoa']['ocupacao'],
                        'updated_limit' : True
                    }
                )
                #sleep(1)
            else:
                if response.status_code == 404 :
                    _logger.debug(response.text)
                else:
                    raise ValidationError( f'Ha ocurrido un error al consultar la informacion a LIMIT: {response.text}')

        #self.state_update_info = 'updated'


    @api.model
    def check_data_limit_send(self):
        all = self.env['contacts.realcred.campaign'].search([('state_update_info', '=' ,'process')])
        for ele in all:

            for contact in ele.contacts_realcred_campaign_ids:
                payload = {}
                headers = {}
                url = f"https://in100.novapowerhub.com.br/api/consulta/3/pre?token=ca31e368-4c49-4ae3-ba8a-e29098f43d03&nb={contact.nb}&cpf={contact.cpf}"
                response = requests.request(
                    "GET", url, headers=headers, data=payload)
                if response.status_code == 200 :
                    result_json = response.json()
                    _logger.debug(result_json)
                    contact.update(
                        {
                            'margemDisponivel': result_json['margemDisponivel'],
                            'margemDisponivelCartao': result_json['margemDisponivelCartao'],
                            'valorLimiteCartao': result_json['valorLimiteCartao'],
                            'elegivelEmprestimo': result_json['elegivelEmprestimo'],
                            'margemDisponivelRcc': result_json['margemDisponivelRcc'],
                            'valorLimiteRcc': result_json['valorLimiteRcc'],
                            'updated_limit' : True
                        }
                    )

                    #sleep(1)
                else:
                    if response.status_code == 404 :
                        _logger.debug(response.text)
                    else:
                        _logger.debug( f'Ha ocurrido un error al consultar la informacion a LIMIT: {response.text}')

            ele.state_update_info = 'updated'

    @api.model
    def check_data_limit_send_LIMIT(self):
        all = self.env['contacts.realcred.campaign'].search([('state_update_info', '=' ,'process')])
        for ele in all:

            for contact in ele.contacts_realcred_campaign_ids:
                payload = {}
                headers = {
                    'Authorization': 'Bearer atoBgWaA24foyyeSaIXwhWST74uJWuQhOF8Lp6kV'
                }

                url = urljoin(URL_LIMIT, contact.cpf)
                response = requests.request(
                    "GET", url, headers=headers, data=payload)
                if response.status_code == 200 :
                    result_json = response.json()
                    _logger.debug(result_json['pessoa'])
                    contact.update(
                        {
                            'nome_mae': result_json['pessoa']['nome_mae'],
                            'falecido': result_json['pessoa']['falecido'],
                            'situacao_cpf': result_json['pessoa']['situacao_cpf'],
                            'renda': result_json['pessoa']['renda'],
                            'ocupacao': result_json['pessoa']['ocupacao'],
                            'updated_limit' : True
                        }
                    )
                    #sleep(1)
                else:
                    if response.status_code == 404 :
                        _logger.debug(response.text)
                    else:
                        raise ValidationError( f'Ha ocurrido un error al consultar la informacion a LIMIT: {response.text}')

            ele.state_update_info = 'updated'

    def button_show_lines(self):

        self.state_update_info = 'process'


    def button_view_detail(self):

        result = self.env['ir.actions.act_window']._for_xml_id('contacts_realcred.action_view_contacts_realcred')
        objs = self.contacts_realcred_campaign_ids.mapped('id')
        ids = []
        for order in objs:
            ids.append(order)
        # # Remvove the context since the action basically display RFQ and not PO.
        #result['context'] = {'search_default_group_department_id': 1, 'search_default_group_payment_type':1}
        result['domain'] = [('id','in',ids)]
        return result


class ContactsRealcredCampaignList(models.Model):
    _name = 'contacts.realcred.campaign.list'

    _order = 'id desc'
    _description = "Contatos RC list"

    state = fields.Selection(string='State', selection=[('draft', 'Rascunho'), (
        'process', 'Em Processo'), ('paid', 'Pago')], default='draft', track_visibility='always')
    contacts_realcred_campaign_id = fields.Many2one(
        'contacts.realcred.campaign', string='Campana')
    contacts_realcred_id = fields.Many2one(
        'contacts.realcred.batch', string='Contato')


class WizardContactsRealcred(models.TransientModel):
    _name = 'contacts.realcred.wizard'
    _inherit = 'contacts.realcred.campaign'

    def save_view_report(self):
        """
        'type_search':self.type_search,
        'start_date':self.start_date,
        'week':self.week,
        'week_extra':self.week_extra,
        'end_date':self.end_date,
        'type_search_cierre':self.type_search_cierre,
        'cancel_start_date':self.cancel_start_date,
        'cancel_end_date':self.cancel_end_date ,
        """

        view_id = self.env['contacts.realcred.campaign'].create({

            'name_campaign': self.name_campaign,
        })

        order_ids = self.env['contacts.realcred.batch'].search([
        ], order='create_date asc'
        )
        if order_ids:
            self.create_toview_orders(order_ids, view_id)

        return {
            'name': 'Previsiones',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'contacts.realcred.campaign',
            'view_id': False,
            'type': 'ir.actions.act_window',
            # 'target': 'new',
            'context': {
            },
        }

    def create_toview_orders(self, order_ids, view_id):

        for order in order_ids:

            ctx = {
                'contacts_realcred_campaign_id': view_id.id,
                'contacts_realcred_id': order.id
            }

        self.env['contacts.realcred.campaign.list'].create(ctx)


class ResPartnerInherint(models.Model):

    _inherit = 'res.partner'
#    beneficios_ids =  fields.One2many('contacts.realcred.batch', 'cpf_id', 'Beneficios',compute="_get_cpfs")
    
    @api.model
    def _get_cpfs(self):
        for row in self:
            related_recordset = self.env["contacts.realcred.batch"].search([("cpf", "=",row.cnpj_cpf)])
            row.beneficios_ids = related_recordset
