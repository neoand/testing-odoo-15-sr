from odoo import _, api, fields, models

class SaleOrderLineInherint(models.Model):

    _inherit = 'sale.order.line'

    product_bank = fields.Char(
        string="Banco",
        compute='_compute_product_bank',
        store=True, readonly=True,  precompute=True)
    

    product_promotora = fields.Char(
        string="Promotora",
        compute='_compute_product_promotora',
        store=True, readonly=True, precompute=True)
    
    
    #rc_recurring_plan = fields.Char( string="Prazo", compute='_compute_rc_recurring_plan')
    
    rc_recurring_prazo = fields.Many2one('crm.recurring.plan', tracking=True , string="Prazo")

    monthly_amount = fields.Monetary(string="Valor da Parcela", tracking=True , currency_field='currency_id')

    liquido = fields.Monetary(string="Liquido", tracking=True , currency_field='currency_id')

    ade = fields.Char(string="ADE",tracking=True )


    @api.depends('product_id','price_unit')
    def _compute_rc_recurring_plan(self):
        for line in self:
            if line.order_id: 
                line.rc_recurring_plan = line.order_id.opportunity_id.recurring_plan.name
                line.monthly_amount = line.order_id.opportunity_id.monthly_amount
                line.price_unit = line.order_id.opportunity_id.expected_revenue
            else:
                line.rc_recurring_plan = ""



    @api.depends('product_id')
    def _compute_price_unit(self):
        for option in self:
            if not option.product_id or not option.order_id.pricelist_id:
                continue
            # To compute the price_unit a so line is created in cache
            values = option._get_values_to_add_to_order()
            new_sol = self.env['sale.order.line'].new(values)
            new_sol._compute_price_unit()
            option.price_unit = new_sol.price_unit


    @api.depends( 'product_id')
    def _compute_product_bank(self):
        for line in self:
            if not line.product_id:
                continue
            line.product_bank = line.product_id.bank.name


    @api.depends( 'product_id')
    def _compute_product_promotora(self):
        for line in self:
            if not line.product_id:
                continue
            line.product_promotora = line.product_id.promotora.name