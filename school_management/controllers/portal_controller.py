from odoo.addons.portal.controllers.portal import CustomerPortal, pager as p
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class MySchoolPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(MySchoolPortal, self)._prepare_home_portal_values(counters)
        values['school_count'] = request.env['school_management.school'].search_count([])
        print("values: ", values)
        return values

    @http.route(['/my/school', '/my/school/page/<int:page>'], type='http', auth='user', website=True)
    def my_school_list(self, page=1, sortby=None, search=None, search_in='all', groupby="none", **kw):
        # add sort by feature
        if not search_in:
            search_in = 'name'

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'established_date': {'label': _('Establish Date'), 'order': 'established_date'},
        }
        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'name': {'label': _('Name'), 'input': 'name', 'domain': [('name', 'ilike', search)]}
        }
        search_domain = search_list[search_in]['domain']
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not groupby or groupby == 'none':
            groupby = 'school_type'
        groupby_list = {
            'location': {'label': _('Location'), 'input': 'location'},
            'school_type': {'label': _('School Type'), 'input': 'school_type'},
        }
        group_by_school = groupby_list.get(groupby, {})
        if groupby in ('location', 'school_type'):
            group_by_school.get('input')
        else:
            group_by_school = ''
        print("group_by_school: ", group_by_school)

        school_count = request.env['school_management.school'].search_count([])
        pager = portal_pager(url='/my/school',
                             total=school_count,
                             page=page, step=5,
                             scope=5,
                             url_args={'sortby': sortby, 'search_in': search_in, 'search': search,
                                       'groupby': groupby})
        schools = request.env['school_management.school'].search(search_domain, limit=5, offset=pager['offset'],
                                                                 order=order)
        if groupby_list[groupby]['input']:
            school_group_list = [{group_by_school['input']: i, 'schools': list(j)} for i, j in groupbyelem(schools, itemgetter(group_by_school['input']))]
        else:
            school_group_list = [{'schools': schools}]
        print("school_group_list: ", school_group_list)
        print("school_group_list: type ", type(school_group_list))
        print("school: type ", type(schools))
        return request.render('school_management.school_list_view_template', {
            'group_schools': school_group_list,
            'page_name': 'my_school',
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'default_url': '/my/school',
            'groupby': groupby,
            'searchbar_groupby': groupby_list,
        })


    @http.route(['/my/school/create'], type='http', auth='user',  methods=['POST', 'GET'], website=True)
    def create_school(self, **kw):
        print(kw)
        countries = request.env['res.country'].search([])
        if request.httprequest.method == 'POST':
            keys = ['name', 'country_id', 'email', 'website', 'address', 'contact', 'image']
            vals = {key: kw.get(key) for key in keys if kw.get(key)}
            new_school_id = request.env['school_management.school'].create(vals)
            if new_school_id:
                return request.render('school_management.create_school_success_form')
        return request.render('school_management.create_school_form',
                                  {'page_name': 'create_school',
                                   'countries': countries})

    @http.route(['/my/student/create'], type='http', auth='user', methods=['POST', 'GET'], website=True)
    def create_student(self, **kw):
        print(kw)  # For debugging purposes
        schools = request.env['school_management.school'].sudo().search([])
        parents = request.env['school_management.parent'].sudo().search([])

        # Handle POST request
        if request.httprequest.method == 'POST':
            # Extract and validate the input data
            keys = ['name', 'roll_number', 'standard', 'section', 'school_id', 'email', 'admission_date', 'parent_id',
                    'image']
            vals = {key: kw.get(key) for key in keys if kw.get(key)}

            if vals.get('school_id'):
                vals['school_id'] = int(vals['school_id'])
            if vals.get('parent_id'):
                vals['parent_id'] = int(vals['parent_id'])

            new_student_id = request.env['school_management.student'].create(vals)

            if new_student_id:
                return request.render('school_management.create_student_success_form')

        # Handle GET request or invalid POST
        return request.render('school_management.create_student_form', {
            'page_name': 'create_student',
            'schools': schools,
            'parents': parents,
        })

        schools = request.env['school_management.school'].sudo().search([])
        parents = request.env['school_management.parent'].sudo().search([])
        return request.render('school_management.create_student_form', {
            'schools': schools,
            'parents': parents,
        })


    @http.route(['/my/school/<int:school_id>'], type='http', auth='user', website=True)
    def my_school_detail(self, school_id, **kw):
        # school_id = request.env['school_management.school'].search([('id', '=', school_id)])
        # return None
        school_ids = request.env['school_management.school'].search([]).ids
        school_index = school_ids.index(school_id)
        school_count = len(school_ids)
        prev_school_id = school_ids[school_index - 1] if school_index > 0 else False
        next_school_id = school_ids[school_index + 1] if school_index < school_count - 1 else False
        school = request.env['school_management.school'].search([('id', '=', school_id)])
        total = len(school.student_ids)
        return request.render('school_management.school_details_view_portal', {'school': school,
                                                                               'page_name': 'school_details',
                                                                               'prev_record': f'/my/school/{prev_school_id}' if prev_school_id else False,
                                                                               'next_record': f'/my/school/{next_school_id}' if next_school_id else False,
                                                                               'total': total})

    @http.route(['/my/school/print/<model("school_management.school"):school_id>'], type='http', auth='user',
                website=True)
    def report(self, school_id, **kw):
        return self._show_report(model=school_id, report_type='pdf',
                                 report_ref='school_management.school_management_school_report_action', download=True)

    

    @http.route(['/my/school/student/<int:school_id>', '/my/school/student/<int:school_id>/page/<int:page>'],
                type='http', auth='user', website=True)
    def school_student_list(self, school_id, page=1, sortby=None, search=None, search_in='all', **kw):
        # Fetch the school object
        school = request.env['school_management.school'].browse(school_id)
        if not school.exists():
            return request.not_found()

        # Search and sort options
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'roll_number': {'label': _('Roll Number'), 'order': 'roll_number'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        search_list = {
            'all': {
                'label': _('All'),
                'input': 'all',
                'domain': [('id', 'in', school.student_ids.ids)],  # Restrict to enrolled students
            },
            'name': {
                'label': _('Name'),
                'input': 'name',
                'domain': [('id', 'in', school.student_ids.ids), ('name', 'ilike', search)],
            },
            'roll_number': {
                'label': _('Roll Number'),
                'input': 'roll_number',
                'domain': [('id', 'in', school.student_ids.ids), ('roll_number', 'ilike', search)],
            },
        }

        # Determine search domain
        search_domain = search_list.get(search_in, search_list['all'])['domain']

        # Determine sorting order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Fetch the total count of students
        total_students = request.env['school_management.student'].search_count(search_domain)

        # Pagination logic
        pager = portal_pager(
            url='/my/school/student/%s' % school_id,
            total=total_students,
            page=page,
            step=5,  # Number of students per page
            scope=5,  # Number of pages to display
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
        )

        # Fetch students for the current page
        students = request.env['school_management.student'].search(search_domain, limit=5, offset=pager['offset'],
                                                                   order=order)

        return request.render('school_management.school_student_view', {
            'students': students,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_list': search_list,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
            'school': school,
        })



    @http.route(['/my/student/edit/<int:student_id>'], type='http' , auth='user',methods=['POST', 'GET'],website=True)
    def edit_student(self,student_id,**kw):
        
        if request.httprequest.method == 'POST':
            # Get the submitted data from the form
            print(kw)
            name = kw.get('name')
            email = kw.get('email')
            section = kw.get('section')
            version = kw.get('version')
            admission_date = kw.get('admission_date')
            group = kw.get('group')
            weight_in_kg = kw.get('weight_in_kg')
            weight_in_pounds = kw.get('weight_in_pounds')

            # Fetch the student record to be updated
            student = request.env['school_management.student'].sudo().browse(student_id)
            print(student)
            if student.exists():
                # Update the student's record with the new values
                student.write({
                    'name': name,
                    'email': email,
                    'section': section,
                    'version': version,
                    'admission_date': admission_date,
                    'group': group,
                    'weight_in_kg': float(weight_in_kg) if weight_in_kg else 0.0,
                    'weight_in_pounds': float(weight_in_pounds) if weight_in_pounds else 0.0,
                })
                return None

            # If student doesn't exist, you can return an error page or message
            return request.render('school_management.student_edit_template', {
                'error': 'Student not found',
                'student': student,
            })

        # Handling GET request to render the edit form
        student = request.env['school_management.student'].sudo().browse(student_id)
        if student.exists():
            return request.render('school_management.student_edit_template', {
                'student': student,
            })
        return request.render('school_management.student_edit_template', {
            'error': 'Student not found',
        })