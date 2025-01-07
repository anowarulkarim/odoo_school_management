from odoo import models, fields, api
from odoo.exceptions import UserError


class Playground(models.Model):
    _name = 'school_management.playground'
    _description = 'Playground'

    name = fields.Char()
    location = fields.Char()
    area = fields.Float()
    type = fields.Selection([('indoor', 'Indoor'), ('outdoor', 'Outdoor')], default='outdoor')


class SwimmingPool(models.Model):
    _name = 'school_management.swimming_pool'
    _description = 'Swimming Pool'

    name = fields.Char()
    location = fields.Char()
    length = fields.Float()
    width = fields.Float()
    depth = fields.Float()


class School(models.Model):
    _name = 'school_management.school'
    _description = 'School'

    name = fields.Char()
    address = fields.Text()
    contact = fields.Char()
    email = fields.Char()
    website = fields.Char()
    color = fields.Char()
    established_date = fields.Date()
    school_code = fields.Char()
    teacher_ids = fields.One2many('school_management.teacher', 'school_id', string='Teachers', ondelete='cascade')
    student_ids = fields.One2many('school_management.student', 'school_id', string='Students', ondelete='cascade')
    active = fields.Boolean(default=True)
    playground_ids = fields.Many2many('school_management.playground', string='Playgrounds')
    swimming_pool_ids = fields.Many2many('school_management.swimming_pool', 'school_id', string='Swimming Pools')

    def print_school_report(self):
        return self.env.ref('school_management.school_management_school_report_action').report_action(self)

    def print_school_student_count_report(self):
        data = {'count': len(self.student_ids)}
        return self.env.ref('school_management.school_management_school_student_count_report_action').report_action(
            self, data=data)

    def return_action_to_open_student_list(self):
        action = self.env.ref('school_management.school_management_student_action').read()[0]
        action['domain'] = [('school_id', '=', self.id)]
        action['context'] = {'default_school_id': self.id}
        action['views'] = [(self.env.ref('school_management.school_management_student_view_tree').id, 'tree')]
        return action

    # def print_school_details_report(self):
    #     students = [
    #         {'name': student.name, 'roll_number': student.roll_number, 'standard': student.standard}
    #         for student in self.student_ids
    #     ]
    #     teachers = [
    #         {'name': teacher.name, 'subject': teacher.subject}
    #         for teacher in self.teacher_ids
    #     ]
    #
    #     data = {
    #         'school_name': self.name,
    #         'school_address': self.address,
    #         'students': students,
    #         'teachers': teachers,
    #         'total_pages': 1,  # For simplicity
    #         'current_page': 1
    #     }
    #
    #     return self.env.ref('school_management.school_management_school_details_report_action').report_action(
    #         self, data=data
    #     )

    def print_school_details_report(self):
        data1 = {
            'school_name': self.name,
            'address': self.address,
            'students': sorted(
                [{'name': student.name, 'roll_number': student.roll_number, 'standard': student.standard} for student in
                 self.student_ids],
                key=lambda x: x['standard']
            ),
            'teachers': [{'name': teacher.name, 'subject': teacher.subject} for teacher in self.teacher_ids],
        }
        return self.env.ref('school_management.school_management_school_report_action').report_action(self, data=data1)

    def print_school_details_report1(self,context):
        """
        Method to print a report for the current active school
        when the form view is open.
        """
        # active_school = self.env.context.get('active_id')
        # if not active_school:
        #     raise UserError("No school selected!")
        #
        # school = self.env['school_management.school'].browse(active_school)
        # if not school:
        #     raise UserError("Invalid school!")

        # Here, you can generate the report for the school. You can replace this with your actual report logic
        # For example, generating a PDF or printing some details.
        data1 = {
            'school_name': self.name,
            'address': self.address,
            'students': sorted(
                [{'name': student.name, 'roll_number': student.roll_number, 'standard': student.standard} for student in
                 self.student_ids],
                key=lambda x: x['standard']
            ),
            'teachers': [{'name': teacher.name, 'subject': teacher.subject} for teacher in self.teacher_ids],
        }
        return self.env.ref('school_management.school_management_school_report_action').report_action(self, data=data1)