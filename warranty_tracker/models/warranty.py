from email.policy import default
from random import randint

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError, UserError
from datetime import date


class WarrantyProduct(models.Model):
    _name = 'warranty.product'
    _description = 'Product Warranty'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Product Name")
    serial_number = fields.Char(string="Serial Number", tracking=True)
    purchase_date = fields.Date(string="Purchase Date", )
    warranty_start_date = fields.Date(string="Warranty Start Date",
                                      compute='_compute_warranty_start_date',)
    warranty_end_date = fields.Date(string="Warranty End Date", tracking=True)
    selling_price = fields.Monetary(string="Selling Price",currency_field="product_currency_id")
    discount_price = fields.Monetary(
        compute='_compute_discount_price',
        currency_field="product_currency_id",
        # store=True
    )
    offer = fields.Boolean(string="Offer")

    paid_option = fields.Selection(
        selection=[
            ("c", "cash"),
            ("o", "online")
        ],
        string="Payment Method",
    )

    is_expired = fields.Boolean(
        string="Is Expired",
        compute="_compute_is_expired",
        store=True,
        help="Indicates if the warranty has expired."
    )

    days_to_expiry = fields.Integer(
        string="Days to Expiry",
        compute="_compute_days_to_expiry",
        help="Number of days left until the warranty expires. Negative for expired warranties."
    )

    warranty_duration = fields.Integer(
        string="Warranty Duration (Days)",
        compute="_compute_warranty_duration",
        help="The total duration of the warranty in days."
    )

    warranty_claim_ids = fields.One2many(
        comodel_name='warranty.claim',
        inverse_name='product_id',
        string='Warranty Claims',
    )

    claim_descriptions = fields.Text(
        string='Claim Descriptions',
        compute='_compute_claim_descriptions',
        store=True,
    )


    @api.depends('warranty_claim_ids.description')
    def _compute_claim_descriptions(self):
        for record in self:
            descriptions = record.warranty_claim_ids.mapped('description')
            record.claim_descriptions = "\n".join(descriptions) if descriptions else 'No claims available.'

    @api.depends('warranty_end_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = bool(record.warranty_end_date) and record.warranty_end_date < today

    @api.depends('warranty_end_date')
    def _compute_days_to_expiry(self):
        today = date.today()
        for record in self:
            record.days_to_expiry = (record.warranty_end_date - today).days if record.warranty_end_date else 0

    @api.depends('warranty_start_date', 'warranty_end_date')
    def _compute_warranty_duration(self):
        for record in self:
            if record.warranty_start_date and record.warranty_end_date:
                record.warranty_duration = (record.warranty_end_date - record.warranty_start_date).days
            else:
                record.warranty_duration = 0


    @api.onchange('offer')
    def _onchange_offer(self):
        if self.offer:
            self.paid_option = 'o'

    @api.constrains('offer', 'paid_option')
    def _check_offer_paid_option(self):
        for record in self:
            if record.offer and record.paid_option != 'o':
                raise ValidationError(
                    "When 'Offer' is enabled, the payment method must be 'Online'."
                )

    # @api.constrains('warranty_start_date', 'warranty_end_date')
    # def _check_warranty_dates(self):
    #     for record in self:
    #         if record.warranty_start_date and record.warranty_end_date:
    #             if record.warranty_end_date < record.warranty_start_date:
    #                 raise ValidationError(
    #                     "Warranty End Date cannot be earlier than Warranty Start Date."
    #                 )

    @api.constrains('serial_number')
    def _check_serial_number(self):
        for record in self:
            found = self.search_count([('id', '!=', record.id), ('serial_number', '=ilike', record.serial_number)],limit=1 )
            if found:
                raise ValidationError(
                    "Same product already used."
                )

    @api.depends('selling_price')
    def _compute_discount_price(self):
        for record in self:
            record.discount_price = record.selling_price - (record.selling_price * (10 / 100))


    @api.depends('purchase_date')
    def _compute_warranty_start_date(self):
        for records in self:
            records.warranty_start_date=records.purchase_date

    # @api.ondelete(at_uninstall=False)
    # def _check_warranty_end_date(self):
    #     for record in self:
    #         if record.warranty_end_date and record.warranty_end_date > date.today():
    #             raise ValidationError(
    #                 "Cannot delete a record with a Warranty End Date past than today's date."
    #             )

    # def unlink(self):
    #     for record in self:
    #         if record.warranty_end_date and record.warranty_end_date > date.today():
    #             raise ValidationError(
    #                 "Cannot delete a record with a Warranty End Date past than today's date."
    #             )
    #     return super().unlink()

    # @api.model
    # def write(self, vals):
    #     if 'warranty_end_date' in vals or 'purchase_date' in vals:
    #         raise UserError("You cannot change any date")
    #
    #     return super(WarrantyProduct, self).write(vals)

    product_currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', tracking=True,
        help="this is the currency",
        default=lambda self:self._get_default_currency())

    def _get_default_currency(self):
        return self.env.company.currency_id