from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http

class MySchoolPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(MySchoolPortal, self)._prepare_home_portal_values(counters)
        values['school_count'] = request.env['school_management.school'].search_count([])
        print("values: ", values)
        return values

    @http.route(['/my/school'], type='http', auth='user', website=True)
    def my_school(self, **kw):
        schools = request.env['school_management.school'].search([])
        return request.render('school_management.school_list_view_template', {
            'schools': schools,
            'page_name': 'my_school',
        }) 

    @http.route(['/my/school/<int:school_id>'], type='http', auth='user', website=True)
    def my_school_detail(self, school_id, **kw):
        # school_id = request.env['school_management.school'].search([('id', '=', school_id)])
            # return None
        school = request.env['school_management.school'].search([('id', '=', school_id)])
        total=len(school.student_ids)
        return request.render('school_management.school_details_view_portal', {'school': school,
                                                                               'page_name': 'school_details',
                                                                               'total':total})

    @http.route(['/my/school/student/<int:school_id>'], type='http', auth='user', website=True)
    def school_student_list(self,school_id,**kw):
        print("here")
        school = request.env['school_management.school'].search([('id', '=', school_id)])
        print(school)
        if not school.exists():
            return request.not_found()

        students = school.student_ids
        print(students)
        return request.render('school_management.school_student_view',{
            'students':students,
            'page_name':'school_student_list',
        })