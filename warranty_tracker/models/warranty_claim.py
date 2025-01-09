from email.policy import default
from random import randint
from xml.etree.ElementInclude import default_loader

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from odoo.release import description
from odoo.tools.populate import compute


class WarrantyClaim(models.Model):
    _name = 'warranty.claim'
    _description = 'Warranty Claim'
    _inherit = ['mail.thread','mail.activity.mixin']

    product_id = fields.Many2one('warranty.product', string="Product", required=True)
    claim_date = fields.Date(string="Claim Date", default=fields.Date.today(), tracking=True)
    description = fields.Text(string="Description of Issue",)
    show_button = fields.Boolean(
        string="Show Button",
        compute="_compute_show_button",
        store=False,
        default=True
    )
    print(show_button)
    @api.model
    def _compute_show_button(self):
        for record in self:
            user = self.env.user
            # manager_group = self.env.ref('warranty_tracker.group_warranty_tracker_manager')
            # Button will be visible if the user belongs to the manager group
            record.show_button = self.env.user.has_group('warranty_tracker.group_warranty_tracker_manager')





    # _rec_name = "display_name"
    # display_name=fields.Char(
    #     compute="_compute_display_name"
    # )
    # def _compute_display_name(self):
    #     for record in self:
    #         record.display_name=f"{record.product_id.name} {record.description}"
    status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string="Claim Status",
        default='pending',

        tracking=True
    )
    resolution_date = fields.Date(string="Resolution Date")

    color = fields.Integer(default=lambda self:randint(0,11))
    #
    # @api.model
    # def name_create(self, name):
    #     record = self.create({'name': name,
    #                           'color': randint(0, 11)})
    #     return record.id, record.display_name
    #
    # @api.constrains('color')
    # def _check_color(self):
    #     for rec in self:
    #         if rec.color < 0 or rec.color > 12:
    #             raise exceptions.ValidationError("Color has to be a integer between 0 and 12")
    def action_approve(self):
        for record in self:
            record.status = 'approved'

    def action_reject(self):
        for record in self:
            record.status = 'rejected'

    def action_cancel(self):
        for record in self:
            record.status = 'pending'

    # @api.constrains('product_id', 'claim_date')
    # def _check_claim_date(self):
    #     for record in self:
    #         if record.claim_date < record.product_id.purchase_date:
    #             raise ValidationError("Claim Date cannot be earlier than the Product's Purchase Date.")
