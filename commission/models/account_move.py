# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    commission_percent = fields.Float(string='Commission(%)', compute='get_commission_percent')
    commission_amount = fields.Float(string='Commission Amount', compute='get_commission_amount')

    @api.depends('product_id', 'move_id.partner_id')
    def get_commission_percent(self):
        for rec in self:
            sale_order = rec.env['sale.order'].search([('name', '=', rec.move_id.invoice_origin)], limit=1)
            commission_obj = None
            if sale_order:
                if sale_order.partner_shipping_id.commission_id:
                    commission_obj = sale_order.partner_shipping_id.commission_id
                elif sale_order.partner_invoice_id.commission_id:
                    commission_obj = sale_order.partner_invoice_id.commission_id
                else:
                    commission_obj = sale_order.partner_id.commission_id
                    
                if commission_obj:
                    rec.commission_percent = commission_obj.percentage
                else:
                    rec.commission_percent = 0

    @api.depends('product_id', 'price_subtotal', 'move_id.partner_id')
    def get_commission_amount(self):
        for rec in self:
            rec.commission_amount = 0
            if rec.commission_percent:
                rec.commission_amount = (rec.price_subtotal / 100) * rec.commission_percent


class AccountMove(models.Model):
    _inherit = "account.move"

    merchandising_amount = fields.Monetary(string='Merchandising Amount', store=True, readonly=True, tracking=True,
        compute='_compute_merchandising_amount')

    @api.depends('line_ids.commission_amount')
    def _compute_merchandising_amount(self):
        total = 0.0
        for move in self:
            for line in move.invoice_line_ids:
                print("line.commission_amount")
                print(line.commission_amount)
                total += line.commission_amount
            move.merchandising_amount = total
