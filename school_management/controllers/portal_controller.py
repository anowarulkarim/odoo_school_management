from odoo.addons.portal.controllers.portal import CustomerPortal, pager as p
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _


class MySchoolPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(MySchoolPortal, self)._prepare_home_portal_values(counters)
        values['school_count'] = request.env['school_management.school'].search_count([])
        print("values: ", values)
        return values

    @http.route(['/my/school', '/my/school/page/<int:page>'], type='http', auth='user', website=True)
    def my_school_list(self, page=1, sortby=None, search=None, search_in='all', **kw):
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
        school_count = request.env['school_management.school'].search_count([])
        pager = portal_pager(url='/my/school',
                             total=school_count,
                             page=page, step=5,
                             scope=5,
                             url_args={'sortby': sortby, 'search_in': search_in, 'search': search})
        schools = request.env['school_management.school'].search(search_domain, limit=5, offset=pager['offset'],
                                                                 order=order)
        return request.render('school_management.school_list_view_template', {
            'schools': schools,
            'page_name': 'my_school',
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
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

    # @http.route(['/my/school/student/<int:school_id>', '/my/school/student/<int:school_id>/page/<int:page>'],
    #             type='http', auth='user', website=True)
    # def school_student_list(self, school_id, page=1, sortby=None, search=None, search_in='all', **kw):
    #     # School object
    #     school = request.env['school_management.school'].search([('id', '=', school_id)])
    #     if not school.exists():
    #         return request.not_found()
    #
    #     # Add search options
    #     searchbar_sortings = {
    #         'date': {'label': _('Newest'), 'order': 'create_date desc'},
    #         'roll_number': {'label': _('Roll Number'), 'order': 'roll_number'},
    #         'name': {'label': _('Name'), 'order': 'name'},
    #     }
    #     search_list = {
    #         'all': {'label': _('All'), 'input': 'all', 'domain': [('id', '=', school_id)]},
    #         'name': {'label': _('Name'), 'input': 'name', 'domain': [('name', 'ilike', search)]},
    #         'roll_number': {'label': _('Roll Number'), 'input': 'roll_number',
    #                         'domain': [('roll_number', 'ilike', search)]}
    #     }
    #
    #     search_domain = search_list.get(search_in, {'domain': []})['domain']
    #
    #     if not sortby:
    #         sortby = 'date'
    #     order = searchbar_sortings.get(sortby, {}).get('order', 'create_date desc')
    #
    #     # Pagination
    #     student_count = len(school.student_ids)
    #     pager = portal_pager(
    #         url=f'/my/school/student/{school_id}',
    #         total=student_count,
    #         page=page,
    #         step=5,
    #         scope=5,
    #         url_args={'sortby': sortby, 'search_in': search_in, 'search': search}
    #     )
    #
    #     # Fetching student data
    #     students = school.student_ids.search(search_domain, limit=5, offset=pager['offset'], order=order)
    #
    #     return request.render('school_management.school_student_view', {
    #         'students': students,
    #         'school': school,
    #         'page_name': 'school_student_list',
    #         'pager': pager,
    #         'sortby': sortby,
    #         'searchbar_sortings': searchbar_sortings,
    #         'searchbar_inputs': search_list,
    #         'search_in': search_in,
    #         'search': search,
    #     })

    # @http.route(['/my/school/student/<int:school_id>'], type='http', auth='user', website=True)
    # def school_student_list(self, school_id, page=1, sortby=None, search=None, search_in='all', **kw):
    #     # Fetch the school object
    #     school = request.env['school_management.school'].browse(school_id)
    #     if not school.exists():
    #         return request.not_found()
    #
    #     # Search and sort options
    #     searchbar_sortings = {
    #         'date': {'label': _('Newest'), 'order': 'create_date desc'},
    #         'roll_number': {'label': _('Roll Number'), 'order': 'roll_number'},
    #         'name': {'label': _('Name'), 'order': 'name'},
    #     }
    #
    #     search_list = {
    #         'all': {
    #             'label': _('All'),
    #             'input': 'all',
    #             'domain': [('id', 'in', school.student_ids.ids)],  # Restrict to enrolled students
    #         },
    #         'name': {
    #             'label': _('Name'),
    #             'input': 'name',
    #             'domain': [('id', 'in', school.student_ids.ids), ('name', 'ilike', search)],
    #         },
    #         'roll_number': {
    #             'label': _('Roll Number'),
    #             'input': 'roll_number',
    #             'domain': [('id', 'in', school.student_ids.ids), ('roll_number', 'ilike', search)],
    #         },
    #     }
    #
    #     # Determine search domain
    #     search_domain = search_list.get(search_in, search_list['all'])['domain']
    #
    #     # Determine sorting order
    #     order = searchbar_sortings.get(sortby, searchbar_sortings['date'])['order']
    #
    #     # Fetch students based on domain and order
    #     students = request.env['school_management.student'].search(search_domain, order=order)
    #
    #     # Pagination logic
    #     total_students = len(students)
    #     pager = portal_pager(
    #         url='/my/school/student/%s' % school_id,
    #         total=total_students,
    #         page=page,
    #         step=5,  # Number of students per page
    #         scope=5,  # Number of pages to display
    #         url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
    #     )
    #
    #     # Slice students for the current page
    #     students = students[(page - 1) * 5:page * 5]
    #
    #     return request.render('school_management.school_student_view', {
    #         'students': students,
    #         'pager': pager,
    #         'searchbar_sortings': searchbar_sortings,
    #         'search_list': search_list,
    #         'sortby': sortby,
    #         'search_in': search_in,
    #         'search': search,
    #         'school': school,
    #     })

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