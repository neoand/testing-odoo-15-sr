from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class SaleOrderInherint(models.Model):

    _inherit = 'sale.order'

    ade = fields.Char(string="ADE")

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
        comodel_name="res.bank" ,string="Banco" ,related='partner_id.bank_id')
    
    liquido_total = fields.Monetary(string="Liquido Total", currency_field='currency_id' , tracking=True , compute='_compute_liquido_total' )
    monthly_amount_total = fields.Monetary(string="Valor da Parcela Total", currency_field='currency_id' , tracking=True , compute='_compute_monthly_amount_total' )
    """
    state = fields.Selection([
        ('draft', 'Análise'),
        ('sent', 'Cotação Enviada'),
        ('sale', 'Averbada'),
        ('done', 'Trancado'),
        ('cancel', 'Cancelado'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    """
    state = fields.Selection(
        selection_add=[
        ('draft', 'Análise'),
        ('sent', 'Cotação Enviada'),
        ('sale', 'Averbada'),
        ('done', 'Trancado'),
        ('cancel', 'Cancelado'),
        ],
        string='Estatus',
        tracking=False,
        )



    mt_state = fields.Selection([
        ('draft', 'Análise'),
        ('cancel', 'Cancelado'),
        ('sale', 'Averbado'),
        ('pago_pelo_banco', 'Pago pelo banco'),
        ('estornado', 'Estornado'),
    ], string='Estatus',index=True, copy=False, default='draft', tracking=True)
    
    crm_lead_id = fields.Integer(string="Lead ID", compute='_compute_lead_id')
    cotacoe_id = fields.Integer(string="Cotacoe ID", compute='_compute_cotacoe_id')

    operator_id = fields.Many2one(
        'res.users', string='Operador',
        default=False,
        domain="[('share', '=', False)]",
        check_company=True, index=True, tracking=True)
    

    date_order = fields.Datetime(tracking=True)
    validity_date = fields.Date(string="DATA DE DESBLOQUEIO",tracking=True)
    
    def _compute_lead_id(self):
        for rec in self:
            rec.crm_lead_id = rec.opportunity_id.id

    def _compute_cotacoe_id(self):
        for rec in self:
            rec.cotacoe_id = rec.id

    def action_confirm_rc(self):
        for rec in self:
            rec.mt_state = 'sale'
            rec.state = 'sale'

    @api.depends('state')
    def _compute_mt_state(self):
        for rec in self:
            if rec.state in ('open','to approve'):
                rec.mt_state = 'draft'
            elif rec.state in ('done' , 'sale','sent'):
                rec.mt_state = 'sale'
            else:
                rec.mt_state = rec.state


    @api.depends('order_line.liquido')
    def _compute_liquido_total(self):
        for order in self:
            order_lines = order.order_line
            total = 0.0
            for orl in order_lines :
                total += orl.liquido
            order.liquido_total = total

    @api.depends('order_line.monthly_amount')
    def _compute_monthly_amount_total(self):
        for order in self:
            order_lines = order.order_line
            total = 0.0
            for orl in order_lines :
                total += orl.monthly_amount
            order.monthly_amount_total = total

    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None,  args=None):
        args = args or []
        if self._context.get('search_default_custom_ade'):
            ades = []
            _logger.debug(domain)
            _logger.debug(args)
            for condition in domain:
                if 'ade' in condition:
                    field_name, cond , values = condition
                    ades = values.split(',')
                    domain = [('ade', 'in', ades)]
                    return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
    

class SaleOrderNotesWizard(models.TransientModel):
    _name = 'sale.order.notes.wizard'
    _description = 'Adicionar notas em massa'
    ade_ids = fields.Many2many('sale.order', string="ADE")
    note = fields.Char('Notas' )
        
    def add_notes(self):
        note = self.note 
        orders = self.env['sale.order'].search([('id', 'in', self.ade_ids.ids)])
        for order in orders:
            order.message_post(message_type='comment', body=note)
