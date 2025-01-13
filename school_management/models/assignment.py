from odoo import models, fields, api

class Assignment(models.Model):
    _name='school_management.assignment'
    _description="Assignment"
    _rec_name="title"
    
    title=fields.Char()
    course_id=fields.Many2one("school_management.course",string='Course', required=True, ondelete='cascade')
    assign_date=fields.Date(string='Assign Date')
    last_date=fields.Date(string='Due Date')

    