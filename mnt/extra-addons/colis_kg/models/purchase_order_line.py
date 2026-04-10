from odoo import models, fields, api
import logging

# import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    qty_kg = fields.Float(
        string="Quantity (KG)",
        store=True,
        # required=True,
        
    )
    
    def _prepare_account_move_line(self, move=False):
        vals = super()._prepare_account_move_line(move=move)

        # Copy your custom field
        vals['qty_kg'] = self.qty_kg

        return vals


    # @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    # def _compute_amount(self):
    #     for line in self:
    #         tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
    #         totals = next(iter(tax_results['totals'].values()))
    #         amount_untaxed = totals['amount_untaxed'] 
    #         amount_tax = totals['amount_tax']

    #         line.update({
    #             'price_subtotal': amount_untaxed,
    #             'price_tax': amount_tax,
    #             'price_total': amount_untaxed + amount_tax,
    #         })

    @api.depends('qty_kg', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
    #    the methode _compute_taxesis called to _compute_taxes_for_single_line iand is using the quantity field to compute the taxes, so we need to override the _compute_amount method to use the qty_kg field instead of product_qty. We will create a copy of the tax base dict and replace the quantity with qty_kg before calling the _compute_taxes method. This way, the taxes will be computed based on the quantity in kg instead of the default quantity.
        for line in self:
            # Make a copy of the tax base dict but replace quantity with qty_kg
            tax_base = line._convert_to_tax_base_line_dict()
            # logging.info("tax_base before %s: %s", line.id, tax_base)

            tax_base['quantity'] = line.qty_kg  # <-- use qty_kg here
            # logging.info("tax_base after %s: %s", line.id, tax_base)

            # Compute taxes
            tax_results = self.env['account.tax']._compute_taxes([tax_base])
            totals = next(iter(tax_results['totals'].values()))
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })




#  need to update the tax totals of the purchase order to use the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg. in purchase order form view, the tax totals are computed based on the order lines, so we need to make sure that the tax totals are computed based on the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg.
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    # @api.depends_context('lang')
    # @api.depends('order_line.taxes_id', 'order_line.price_subtotal', 'amount_total', 'amount_untaxed')
    # def _compute_tax_totals(self):
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda x: not x.display_type)
    #         order.tax_totals = self.env['account.tax']._prepare_tax_totals(
    #             [x._convert_to_tax_base_line_dict() for x in order_lines],
    #             order.currency_id or order.company_id.currency_id,
    #         )


    @api.depends_context('lang')
    @api.depends('order_line.taxes_id', 'order_line.price_subtotal', 'amount_total', 'amount_untaxed', 'order_line.qty_kg')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            tax_base_lines = []
            for line in order_lines:
                tax_base = line._convert_to_tax_base_line_dict()
                tax_base['quantity'] = line.qty_kg  # <-- override quantity here
                tax_base_lines.append(tax_base)
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                tax_base_lines,
                order.currency_id or order.company_id.currency_id,
            )


#  same ting in salle order line and sale order, we need to update the tax totals to use the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg. in sale order form view, the tax totals are computed based on the order lines, so we need to make sure that the tax totals are computed based on the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg.
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_kg = fields.Float(
        string="Quantity (KG)",
        store=True,
        # required=True,
        
    )

    # @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    # def _compute_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([
    #             line._convert_to_tax_base_line_dict()
    #         ])
    #         totals = list(tax_results['totals'].values())[0]
    #         amount_untaxed = totals['amount_untaxed']
    #         amount_tax = totals['amount_tax']

    #         line.update({
    #             'price_subtotal': amount_untaxed,
    #             'price_tax': amount_tax,
    #             'price_total': amount_untaxed + amount_tax,
    #         })

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)

        # Copy your custom field
        vals['qty_kg'] = self.qty_kg

        return vals

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'qty_kg')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line using qty_kg instead of product_uom_qty.
        """
        for line in self:
            # Get tax base dict for this line
            tax_base = line._convert_to_tax_base_line_dict()
            
            # Override quantity with qty_kg
            tax_base['quantity'] = line.qty_kg or 0.0

            # Compute taxes using the modified tax base
            tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([tax_base])
            
            # Extract totals
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            # Update line amounts
            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })



# same ting in sale order, we need to update the tax totals to use the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg. in sale order form view, the tax totals are computed based on the order lines, so we need to make sure that the tax totals are computed based on the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg.
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.depends_context('lang')
    # @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
    # def _compute_tax_totals(self):
    #     for order in self:
    #         order = order.with_company(order.company_id)
    #         order_lines = order.order_line.filtered(lambda x: not x.display_type)
    #         order.tax_totals = order.env['account.tax']._prepare_tax_totals(
    #             [x._convert_to_tax_base_line_dict() for x in order_lines],
    #             order.currency_id or order.company_id.currency_id,
    #         )
    


    @api.depends_context('lang')
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id', 'order_line.qty_kg')
    def _compute_tax_totals(self):
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.order_line.filtered(lambda x: not x.display_type)

            tax_base_lines = []
            for line in order_lines:
                vals = line._convert_to_tax_base_line_dict()
                vals['quantity'] = line.qty_kg
                tax_base_lines.append(vals)

            order.tax_totals = order.env['account.tax']._prepare_tax_totals(
                tax_base_lines,
                order.currency_id or order.company_id.currency_id,
            )




# same in account.move.line and account.move.line, we need to update the tax totals to use the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg. in invoice form view, the tax totals are computed based on the invoice lines, so we need to make sure that the tax totals are computed based on the qty_kg field instead of product_qty. We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. This way, the tax totals will be computed correctly based on the quantity in kg.
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    qty_kg = fields.Float(
        string="Quantity (KG)",
        store=True,
        # required=True,
    )

    @api.depends('qty_kg', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
                continue

            # Compute discounted unit price
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))

            # Compute subtotal using qty_kg instead of quantity
            subtotal = line.qty_kg * line_discount_price_unit

            # Compute total including taxes
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.qty_kg,  # use qty_kg here
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded']
                line.price_total = taxes_res['total_included']
            else:
                line.price_subtotal = line.price_total = subtotal

    

   

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.
        Uses qty_kg instead of quantity for tax calculations.
        """
        self.ensure_one()
        is_invoice = self.move_id.is_invoice(include_receipts=True)
        sign = -1 if self.move_id.is_inbound(include_receipts=True) else 1

        return self.env['account.tax']._convert_to_tax_base_line_dict(
            base_line=self,
            partner=self.partner_id,
            currency=self.currency_id,
            product=self.product_id,
            taxes=self.tax_ids,
            price_unit=self.price_unit if is_invoice else self.amount_currency,
            quantity=self.qty_kg if is_invoice else 1.0,  # <-- use qty_kg here
            discount=self.discount if is_invoice else 0.0,
            account=self.account_id,
            analytic_distribution=self.analytic_distribution,
            price_subtotal=sign * self.amount_currency,
            is_refund=self.is_refund,
            rate=(abs(self.amount_currency) / abs(self.balance)) if self.balance else 1.0,
        )




# same for account.move, we need to update the tax totals to use the qty_kg field instead of product_qty.
#  We will override the _compute_tax_totals method to prepare the tax totals based on the qty_kg field. 
#  This way, the tax totals will be computed correctly based on the quantity in kg. in invoice form view, 
#  the tax totals are computed based on the invoice lines, so we need to make sure that the tax totals are computed based on the qty_kg field instead of product_qty.
# class AccountMove(models.Model):
#     _inherit = 'account.move'


#     def _compute_tax_totals(self):
#         """ Computed field used for custom widget's rendering.
#             Only set on invoices.
#         """
#         for move in self:
#             if move.is_invoice(include_receipts=True):
#                 base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
#                 base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]
#                 sign = move.direction_sign
#                 if move.id:
#                     # The invoice is stored so we can add the early payment discount lines directly to reduce the
#                     # tax amount without touching the untaxed amount.
#                     base_line_values_list += [
#                         {
#                             **line._convert_to_tax_base_line_dict(),
#                             'handle_price_include': False,
#                             'quantity': 1.0,
#                             'price_unit': sign * line.amount_currency,
#                         }
#                         for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
#                     ]

#                 kwargs = {
#                     'base_lines': base_line_values_list,
#                     'currency': move.currency_id or move.journal_id.currency_id or move.company_id.currency_id,
#                 }

#                 if move.id:
#                     kwargs['tax_lines'] = [
#                         line._convert_to_tax_line_dict()
#                         for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
#                     ]
#                 else:
#                     # In case the invoice isn't yet stored, the early payment discount lines are not there. Then,
#                     # we need to simulate them.
#                     epd_aggregated_values = {}
#                     for base_line in base_lines:
#                         if not base_line.epd_needed:
#                             continue
#                         for grouping_dict, values in base_line.epd_needed.items():
#                             epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
#                             epd_values['price_subtotal'] += values['price_subtotal']

#                     for grouping_dict, values in epd_aggregated_values.items():
#                         taxes = None
#                         if grouping_dict.get('tax_ids'):
#                             taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

#                         kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
#                             None,
#                             partner=move.partner_id,
#                             currency=move.currency_id,
#                             taxes=taxes,
#                             price_unit=values['price_subtotal'],
#                             quantity=1.0,
#                             account=self.env['account.account'].browse(grouping_dict['account_id']),
#                             analytic_distribution=values.get('analytic_distribution'),
#                             price_subtotal=values['price_subtotal'],
#                             is_refund=move.move_type in ('out_refund', 'in_refund'),
#                             handle_price_include=False,
#                             extra_context={'_extra_grouping_key_': 'epd'},
#                         ))
#                 kwargs['is_company_currency_requested'] = move.currency_id != move.company_id.currency_id
#                 move.tax_totals = self.env['account.tax']._prepare_tax_totals(**kwargs)
#                 if move.invoice_cash_rounding_id:
#                     rounding_amount = move.invoice_cash_rounding_id.compute_difference(move.currency_id, move.tax_totals['amount_total'])
#                     totals = move.tax_totals
#                     totals['display_rounding'] = True
#                     if rounding_amount:
#                         if move.invoice_cash_rounding_id.strategy == 'add_invoice_line':
#                             totals['rounding_amount'] = rounding_amount
#                             totals['formatted_rounding_amount'] = formatLang(self.env, totals['rounding_amount'], currency_obj=move.currency_id)
#                         elif move.invoice_cash_rounding_id.strategy == 'biggest_tax':
#                             if totals['subtotals_order']:
#                                 max_tax_group = max((
#                                     tax_group
#                                     for tax_groups in totals['groups_by_subtotal'].values()
#                                     for tax_group in tax_groups
#                                 ), key=lambda tax_group: tax_group['tax_group_amount'])
#                                 max_tax_group['tax_group_amount'] += rounding_amount
#                                 max_tax_group['formatted_tax_group_amount'] = formatLang(self.env, max_tax_group['tax_group_amount'], currency_obj=move.currency_id)
#                         totals['amount_total'] += rounding_amount
#                         totals['formatted_amount_total'] = formatLang(self.env, totals['amount_total'], currency_obj=move.currency_id)
#             else:
#                 # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
#                 move.tax_totals = None



# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     def _get_name_invoice_report(self):
#         self.ensure_one()
#         logging.info("Getting custom invoice report for move %s", self.id)
#         return 'colis_kg.custom_invoice_report'






# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = 'sale.advance.payment.inv'

#     def create_invoices(self):
#         for wizard in self:
#             logging.info("===== SALE ORDER IDS =====")
#             logging.info("IDs: %s", wizard.sale_order_ids.ids)
#             logging.info("Names: %s", wizard.sale_order_ids.mapped('name'))

#         return super().create_invoices()