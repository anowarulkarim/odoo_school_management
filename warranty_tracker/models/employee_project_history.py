from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

class EmployeeProjectHistory(models.Model):
    _name = "employee.project.history"
    _description = "Employee Project History"
    _order = "sequence, id desc"
    _rec_name = "display_name"

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", string="Department")
    project_id = fields.Many2one('project.project', string='Project', required=True)
    role = fields.Char(string="Role", required=True)
    responsibility = fields.Text(string="Responsibility")
    assigned_from = fields.Date(string="Assigned from")
    assigned_to = fields.Date(string="Assigned to")
    sequence = fields.Integer(default=1)

    @api.constrains('assigned_from_date', 'assigned_to_date')
    def compare_project_duration_date(self):
        for rec in self:
            if rec.assigned_from_date and rec.assigned_to_date and rec.assigned_from_date > rec.assigned_to_date:
                raise ValidationError(_('Assign from date should be less than to date'))

    @api.depends('employee_id', 'project_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.employee_id.name} - {rec.project_id.name}"

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            rec_names = list(filter(lambda x: x.strip(), name.split(' - ')))
            if len(rec_names) >= 2:
                domain = ['|', ('employee_id', operator, rec_names[0]), ('project_id.name', operator, rec_names[-1])]
            else:
                domain = ['|', ('employee_id', operator, name), ('project_id.name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

class InheritedProject(models.Model):
    _inherit = "project.project"

    project_members = fields.One2many(comodel_name="employee.project.history",
                                      inverse_name="project_id",
                                      string="Project Members")
    member_count = fields.Integer(compute='_compute_member_count', string='Member Count')

    @api.depends('project_members')
    def _compute_member_count(self):
        for rec in self:
            rec.member_count = len(rec.project_members)

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    employee_project_history_ids = fields.One2many(
        'employee.project.history', 'employee_id', string='Project History'
    )