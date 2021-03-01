# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        customer_ref = ''
        for line in order.order_line:
            for customer in line.product_id.customer_ids:
                if customer.product_code:
                    customer_ref = customer.product_code
                    break
            self.env['sale.commission.reports'].create({
                'date': order.date_order,
                'invoice_id': order.id,
                'partner_id': order.partner_id.id,
                'customer_reference': customer_ref,
                'invoice_value': order.amount_total,
                'merchandise_value': order.amount_untaxed,
                'commission_amount': line.commission_amount,
                'commission_percent': line.commission_percent,
                'product_id': line.product_id.id,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'commision_id': line.commision_id.id
            })

        res = super(SaleAdvancePaymentInv, self).create_invoices()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commission_percent = fields.Float(string='Commission(%)', compute='get_commission_percent')
    commision_id = fields.Many2one('sale.commision', string='Commission Code', compute='get_commission_percent')

    commission_amount = fields.Float(string='Commission Amount', compute='get_commission_amount')

    @api.depends('product_id', 'order_id.partner_id')
    def get_commission_percent(self):

        for rec in self:
            rec.commission_percent = 0
            for child in rec.order_id.partner_id.child_ids:
                if child.type == 'delivery' and child.commission_id:
                    rec.commission_percent = child.commission_id.percentage
                    rec.commision_id = child.commission_id.id
                    break
                if not child.type == 'delivery' and child.type == 'invoice' and child.commission_id:
                    rec.commission_percent = child.commission_id.percentage
                    rec.commision_id = child.commission_id.id

        if not rec.order_id.partner_id.child_ids:
            rec.commission_percent = rec.order_id.partner_id.commission_id.percentage
            rec.commision_id = rec.order_id.partner_id.commission_id.id

    @api.depends('product_id', 'price_subtotal', 'order_id.partner_id')
    def get_commission_amount(self):
        for rec in self:
            rec.commission_amount = 0
            if rec.commission_percent:
                rec.commission_amount = (rec.price_subtotal / 100) * rec.commission_percent


class SalesCommission(models.Model):
    _name = 'sale.commision'
    _rec_name = 'code'
    code = fields.Char(string='Code')
    percentage = fields.Float(string='Percentage')
