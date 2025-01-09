from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaintenanceRecord(models.Model):
    _name = 'maintenance.record'
    _description = 'Maintenance Record'

    product_id = fields.Many2one('warranty.product', string="Product", required=True)
    service_center_id = fields.Many2one('service.center', string="Service Center")
    maintenance_date = fields.Date(string="Maintenance Date", default=fields.Date.today(), required=True)
    description = fields.Text(string="Maintenance Description", required=True)
    cost = fields.Monetary(string="Cost", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    @api.model
    def create(self, vals):
        product = self.env['warranty.product'].browse(vals['product_id'])
        if product.is_expired:
            raise ValidationError("Cannot perform maintenance on expired warranty products.")
        return super(MaintenanceRecord, self).create(vals)
