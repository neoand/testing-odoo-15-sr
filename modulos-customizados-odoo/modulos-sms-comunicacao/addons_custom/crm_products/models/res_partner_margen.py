from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import re
import requests
import logging
_logger = logging.getLogger(__name__)

class ResMargen(models.Model):

    _inherit = 'res.partner'
    margem_disponivel = fields.Char(string="Margem Disponivel")
    margem_disponivel_cartao = fields.Char(string="Margem Disponivel Cartao")
    margem_disponivel_rcc = fields.Char(string="Margem Disponivel Rcc")
    especie_beneficio = fields.Char(string="Especie Beneficio")
    situacao_beneficio = fields.Char(string="Situacao Beneficio")
    numero_matricula = fields.Char(string="Numero Matricula")
    data_despacho_beneficio = fields.Char(string="Data Despacho Beneficio")
    data_despacho_beneficio_desbloqueo = fields.Char(string="Data de Desbloqueio")
    procurador = fields.Char(string="Procurador")
    representante = fields.Char(string="cpfRepresentanteLegal")

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced') ] , string="Estado Civil")
    
    state_solicitud = fields.Many2one(
        comodel_name="res.country.state",
        string="Estado de Solicitação do Benefício",
        domain=[("country_id.code", "=", "BR")],
            )
    mother_name = fields.Char(string="Nome da Mãe")
    father_name = fields.Char(string="Nome do Pai")
     
    nacionalidade = fields.Many2one(string="Nacionalidade", comodel_name="res.city")
    naturalidade = fields.Many2one(string="Naturalidade", comodel_name="res.city")
    data_emissao = fields.Date(string="Data Emissão RG")
    orgao_expedidor = fields.Char(string="Órgão Expedidor")
    matricula_1 = fields.Char(string="Matrícula 1")
    matricula_2 = fields.Char(string="Matrícula 2")
    senha_1 = fields.Char(string="Senha 1")
    senha_2 = fields.Char(string="Senha 2")

    reception_type = fields.Selection([
        ('C/C', 'C/C'),
        ('C/P', 'C/P'),
        ('O/P', 'O/P') ] , string="Tipo de Recebimento")
    
    agency_regis = fields.Char(string="Agência e dígito")
    account_regis = fields.Char(string="N. da conta e digito")
    bank_id = fields.Many2one(
        comodel_name="res.bank" , string="Banco" 
    ) 

    campaign_id = fields.Many2one(comodel_name='utm.campaign', string="Campaign")
    medium_id = fields.Many2one(comodel_name='utm.medium', string="Medium")
    source_id = fields.Many2one(comodel_name='utm.source', string="Source")

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_margem_disponivel = fields.Char(string="Margem Disponivel" ,  related='partner_id.margem_disponivel', readonly=True)
    partner_margem_disponivel_cartao = fields.Char(string="Margem Disponivel Cartao",related='partner_id.margem_disponivel_cartao', readonly=True)
    partner_margem_disponivel_rcc = fields.Char(string="Margem Disponivel Rcc",related='partner_id.margem_disponivel_rcc', readonly=True)
    partner_especie_beneficio = fields.Char(string="Especie Beneficio",related='partner_id.especie_beneficio', readonly=True)
    partner_situacao_beneficio = fields.Char(string="Situacao Beneficio",related='partner_id.situacao_beneficio', readonly=True)
    partner_numero_matricula = fields.Char(string="Numero Matricula",related='partner_id.numero_matricula', readonly=True)
    partner_data_despacho_beneficio = fields.Char(string="Data Despacho Beneficio",related='partner_id.data_despacho_beneficio', readonly=True)
    partner_data_despacho_beneficio_desbloqueo = fields.Char(string="Data de Desbloqueio",related='partner_id.data_despacho_beneficio_desbloqueo', readonly=True)
    partner_procurador = fields.Char(string="Procurador",related='partner_id.procurador', readonly=True)
    partner_representante = fields.Char(string="cpfRepresentanteLegal",related='partner_id.representante', readonly=True)
    

    partner_marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced') ] , string="Estado Civil" ,related='partner_id.marital' )
    partner_state_solicitud = fields.Many2one(
        comodel_name="res.country.state",
        string="Estado de Solicitação do Benefício",
        domain=[("country_id.code", "=", "BR")],related='partner_id.state_solicitud'
            )
    partner_mother_name = fields.Char(string="Nome da Mãe" ,related='partner_id.mother_name' )
    partner_father_name = fields.Char(string="Nome do Pai" ,related='partner_id.father_name')
    partner_nacionalidade = fields.Many2one(string="Nacionalidade", comodel_name="res.city" ,related='partner_id.nacionalidade')
    partner_naturalidade = fields.Many2one(string="Naturalidade", comodel_name="res.city" ,related='partner_id.naturalidade')
    partner_data_emissao = fields.Date(string="Data Emissão RG",related='partner_id.data_emissao')
    partner_orgao_expedidor = fields.Char(string="Órgão Expedidor",related='partner_id.orgao_expedidor')
    partner_matricula_1 = fields.Char(string="Matrícula 1",related='partner_id.matricula_1')
    partner_matricula_2 = fields.Char(string="Matrícula 2",related='partner_id.matricula_2')
    partner_senha_1 = fields.Char(string="Senha 1",related='partner_id.senha_1')
    partner_senha_2 = fields.Char(string="Senha 2",related='partner_id.senha_2')
    partner_reception_type = fields.Selection([
        ('C/C', 'C/C'),
        ('C/P', 'C/P'),
        ('O/P', 'O/P') ] , string="Tipo de Recebimento" ,related='partner_id.reception_type')
    partner_agency_regis = fields.Char(string="Agência e dígito" ,related='partner_id.agency_regis')
    partner_account_regis = fields.Char(string="N. da conta e digito" ,related='partner_id.account_regis')
    partner_bank_account = fields.Many2one(
        comodel_name="res.bank", string="Banco" ,related='partner_id.bank_id')

    monthly_amount = fields.Monetary(string="Valor da Parcela", currency_field='company_currency')

    date_lead_closed = fields.Date(string="Data de fechamento do lead" )

    def action_search_margem(self):
        self.ensure_one()
        env = self.env['mt.wizzard.apimargem'].with_context(active_model=self._name, active_id=self.id)
        model_action = env.create({})
        return {
            'name': "Consultar margem",
            'type': 'ir.actions.act_window',
            'res_model': 'mt.wizzard.apimargem',
            'res_id': model_action.id,
            'view_mode': 'form',
            'views': [(False,'form')],
            'target': 'new',
        }


    def search(self, args, offset=0, limit=None, order=None, count=False):

        if self.env.user.has_group('sales_team.group_sale_manager'):
            args += [(1,'=',1)]
        elif self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            args += ['|',('team_id', '=',self.env.user.team_id.id),( 'team_id.user_id', '=', self.env.user.id)] 
        elif self.env.user.has_group('sales_team.group_sale_salesman'):
            args += ['|',('user_id','=',self.env.user.id),('user_id','=',False)]


        return super(CrmLead, self).search(args, offset=offset, limit=limit, order=order, count=count)

class MtWizzardApiMargem(models.TransientModel):
    _name = 'mt.wizzard.apimargem'
    _description = 'Consulta de Margem'

    res_model = fields.Char("Related Document Model", required=True)
    res_id = fields.Integer("Related Document ID", required=True)

    cpf = fields.Char('CPF' )
    nb = fields.Char('NB' )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res_id = self.env.context.get('active_id')
        res_model = self.env.context.get('active_model')
        if res_id and res_model:
            res.update({'res_model': res_model, 'res_id': res_id})
        return res
        

    def search_margem(self):

        crm_lead = self.env[self.res_model].browse(self.res_id)
        
        try:

            cpf = re.sub("[^0-9]", "", self.cpf)
            nb = re.sub("[^0-9]", "", self.nb)
            _logger.info("++++++++++++++++++++++++++ CONSULTANDO CPF ++++++++++++++++++++++++++")
            _logger.info(cpf)
            url = f'https://in100.novapowerhub.com.br/api/consulta/3/pre?token=ca31e368-4c49-4ae3-ba8a-e29098f43d03&cpf={cpf}&nb={nb}'
            payload={}
            headers = {
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200 :
                    
                result_json = response.json()
                _logger.debug(result_json)

                fecha_str = False
                fecha_str = result_json['dataDespachoBeneficio']
                #if fecha_str :
                #    fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                #    fecha_str = fecha_obj.strftime('%Y-%m-%d')

                if crm_lead.partner_id :
                    crm_lead.partner_id.write({
                            'margem_disponivel': result_json['margemDisponivel'],
                            'margem_disponivel_cartao' :fecha_str ,  
                            'margem_disponivel_rcc' : result_json['margemDisponivelRcc'],
                            'especie_beneficio' : result_json['especieBeneficio'],
                            'situacao_beneficio' : result_json['situacaoBeneficio'],
                            'numero_matricula' : result_json['numeroMatricula'],
                            'data_despacho_beneficio' : result_json['dataDespachoBeneficio'],
                            'data_despacho_beneficio_desbloqueo' : result_json['dataDespachoBeneficio'],
                            'procurador' : result_json['possuiProcurador'],
                            'representante' : result_json['cpfRepresentanteLegal']


                        })
                else:
                    exist_cpf = self.env['res.partner'].search([('cpf','=',cpf)])
                    if exist_cpf :
                        _logger.info("++++++++++++++++++++++++++ exist_cpf ++++++++++++++++++++++++++")
                        crm_lead.update(
                            {
                            'margem_disponivel': result_json['margemDisponivel'],
                            'margem_disponivel_cartao' :fecha_str ,  
                            'margem_disponivel_rcc' : result_json['margemDisponivelRcc'],
                            'especie_beneficio' : result_json['especieBeneficio'],
                            'situacao_beneficio' : result_json['situacaoBeneficio'],
                            'numero_matricula' : result_json['numeroMatricula'],
                            'data_despacho_beneficio' : result_json['dataDespachoBeneficio'],
                            'data_despacho_beneficio_desbloqueo' : result_json['dataDespachoBeneficio'],
                            'procurador' : result_json['possuiProcurador'],
                            'representante' : result_json['cpfRepresentanteLegal']
                            
                            })
                    else: 
                        raise ValidationError( f'No existe contacto')
            else:
                raise ValidationError( f'Ocorreu um erro ao consultar as informações')



        except  Exception as e:

            raise ValidationError( e )
        