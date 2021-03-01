# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    commission_percent = fields.Float(string='Commission(%)', compute='get_commission_percent')
    commission_amount = fields.Float(string='Commission Amount', compute='get_commission_amount')

    @api.depends('product_id', 'move_id.partner_id')
    def get_commission_percent(self):
        sale_order = self.env['sale.order'].search([('name', '=', self.move_id.invoice_origin)], limit=1)
        self.commission_percent = 0
        for child in sale_order.partner_id.child_ids:
            if child.type == 'delivery' and child.commission_id:
                self.commission_percent = child.commission_id.percentage
                break
            if not child.type == 'delivery' and child.type == 'invoice' and child.commission_id:
                self.commission_percent = child.commission_id.percentage
        if not sale_order.partner_id.child_ids:
            self.commission_percent = self.move_id.partner_id.commission_id.percentage

    @api.depends('product_id', 'price_subtotal', 'move_id.partner_id')
    def get_commission_amount(self):
        for rec in self:
            rec.commission_amount = 0
            if rec.commission_percent:
                rec.commission_amount = (rec.price_subtotal / 100) * rec.commission_percent
