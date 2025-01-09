from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Result(models.Model):
    _name = 'school_management.result'
    _description = 'Result'
    _inherits = {'school_management.student': 'student_id'}

    student_id = fields.Many2one('school_management.student', string='Student', required=True, ondelete='cascade')
    course_id = fields.Many2one('school_management.course', string='Course', required=True)
    grade = fields.Selection([('a+', 'A+'), ('a', 'A'), ('a-', 'A-'), ('b+', 'B+'), ('b', 'B'), ('b-', 'B-'),])
    marks = fields.Float()
    result_date = fields.Date(string='Result Date')

    # @api.model
    # def create(self, vals):
    #     """
    #     Override create to check if total marks exceed 500.
    #     """
    #     # Calculate the total marks including the new result
    #     student_id = vals.get('student_id')
    #     new_marks = vals.get('marks', 0)
    #
    #     # Search for existing results
    #     student_results = self.search([('student_id', '=', student_id)])
    #     total_marks = sum(result.marks for result in student_results) + new_marks
    #
    #     # Raise an error if the total exceeds 500
    #     if total_marks >= 500:
    #         raise ValidationError(
    #             f"Total marks for student ID {student_id} exceed 500! Current total (including this record): {total_marks}")
    #
    #     # Create the record
    #     return super(Result, self).create(vals)
    #
    # def write(self, vals):
    #     """
    #     Override write to check if total marks exceed 500.
    #     """
    #     for record in self:
    #         # Calculate the new marks based on the updates
    #         new_marks = vals.get('marks', record.marks)
    #
    #         # Search for other results excluding the current record
    #         student_results = self.search([('student_id', '=', record.student_id.id), ('id', '!=', record.id)])
    #         total_marks = sum(result.marks for result in student_results) + new_marks
    #
    #         # Raise an error if the total exceeds 500
    #         if total_marks >= 500:
    #             raise ValidationError(
    #                 f"Total marks for student ID {record.student_id.id} exceed 500! Current total (including this update): {total_marks}")
    #
    #     # Write the updates
    #     return super(Result, self).write(vals)

    @api.onchange('marks','student_id')
    def _onchange_marks(self):
        # print(self.student_id.id)
        # domain = [('student_id', '=', self.student_id.id)]
        student = self.env['school_management.student'].search([('id', 'ilike', self.student_id.id)], limit=1)
        print(student.name)
        # print(self.id)
        for result in self:
            result_list = [result.marks for result in result.student_id.result_ids]
            # print(result_list)
            total_marks = sum(result_list)-result_list[-1]
            # print(total_marks,len(result_list))
            max_marks = (len(result_list)) * 100
            if total_marks > max_marks:
                raise ValidationError(
                    f"Total marks for all subjects must not exceed {max_marks} for student {result.student_id.name}")

        if self.student_id:

            if self.marks > 150:

                raise ValidationError(
                    f"marks cant be more then 150")

    # def create(self, vals):
    #     if vals.get('marks') and vals['marks'] > 150:
    #         raise ValidationError('Marks cannot be more than 150!')
    #     return super(Result, self).create(vals)
    #
    # def write(self, vals):
    #     if 'marks' in vals and vals['marks'] > 150:
    #         raise ValidationError('Marks cannot be more than 150!')
    #     return super(Result, self).write(vals)

