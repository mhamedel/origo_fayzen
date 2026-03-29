from odoo import api, models, fields


class ResCompany(models.Model):
    
    _inherit = 'res.company'
    
    #----------------------------------------------------------
    # Fields
    #----------------------------------------------------------
    
    favicon = fields.Binary(
        string="Company Favicon", 
        attachment=True
    )
    
    background_image = fields.Binary(
        string='Apps Menu Background Image',
        attachment=True
    )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the sale order line,
        adding 100 to the untaxed amount.
        """
        for line in self:
            tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([
                line._convert_to_tax_base_line_dict()
            ])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed'] + 100  # your extra 100
            amount_tax = totals['amount_tax']

            line.price_subtotal = amount_untaxed
            line.price_tax = amount_tax
            line.price_total = amount_untaxed + amount_tax

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total')
#     def _compute_amounts(self):
#         """Compute the total amounts of the SO."""
#         for order in self:
#             order = order.with_company(order.company_id)
#             order_lines = order.order_line.filtered(lambda x: not x.display_type)

#             if order.company_id.tax_calculation_rounding_method == 'round_globally':
#                 tax_results = order.env['account.tax']._compute_taxes([
#                     line._convert_to_tax_base_line_dict()
#                     for line in order_lines
#                 ])
#                 totals = tax_results['totals']
#                 amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
#                 amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
#             else:
#                 amount_untaxed = sum(order_lines.mapped('price_subtotal'))
#                 amount_tax = sum(order_lines.mapped('price_tax'))

#             order.amount_untaxed = amount_untaxed
#             order.amount_tax = amount_tax
            # order.amount_total = order.amount_untaxed + order.amount_tax