from odoo import http
from odoo.http import request
import datetime
import jwt
import json

class SchoolManagement(http.Controller):

    @http.route('/school_management/banner', type='json', auth='user')
    def get_banner(self):
        banner_html = """
        <div class="o_kanban_view_banner" style="background-color: #f8d7da; color: #721c24; padding: 10px; border: 1px solid #f5c6cb; border-radius: 5px; text-align: center; width: 100%; box-sizing: border-box;">
            <span style="font-weight: bold;">Important Notification:</span> School Management System Update
        </div>
        """
        return {'html': banner_html}

    @http.route('/index', auth='none')
    def index(self, **kw):
        # return "Hello, world"

        return """
            <html>
                <head>
                    <title>School Management System</title>
                </head>
                <body>
                    <h1>Welcome to School Management System</h1>
                </body>
            </html>
        """

    @http.route('/school_management/students/<int:student_id>', auth='public', website=True, csrf=False)
    def get_student(self, student_id, **kw):
        try:
            student = request.env['school_management.student'].search([('id', '=', student_id)], limit=1)

            if student:
                student_data = {
                    'id': student.id,
                    'name': student.name,
                    'age': student.age,
                    # Add more fields as needed
                }
                return json.dumps(student_data)
            else:
                return json.dumps({'error': 'Student not found'})

        except Exception as e:
            print(e)
            return json.dumps({'error': str(e)})


    @http.route('/school_management/students/<int:student_id>', auth='public', website=True, methods=['DELETE'],csrf=False)
    def delete_student(self, student_id, **kw):
        try:
            student = request.env['school_management.student'].search([('id', '=', student_id)], limit=1)
            if student:
                student.unlink()
                return request.make_response(
                    json.dumps({'message': 'Student successfully deleted'}),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'Student not found'}),
                    headers=[('Content-Type', 'application/json')]
                )

        except Exception as e:
            print(e)
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/school_management/students/update/<int:student_id>', auth='public',type='json', website=True, methods=['POST'],csrf=False)
    def update_student(self, student_id, **kw):
        try:
            student = request.env['school_management.student'].search([('id', '=', student_id)], limit=1)
            if student:
                print(kw.get('name'))
                student.sudo().write({
                    'name': kw.get("name"),
                    # 'age': student.age,
                    # 'roll_number': student.roll_number,
                    # 'standard': student.standard,
                })

                return request.make_response(
                    json.dumps({'message': 'Student successfully updated'}),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'Student not found'}),
                    headers=[('Content-Type', 'application/json')]
                )

        except Exception as e:
            print(e)
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/school_management/students', auth='public', website=True, csrf=False)
    def students(self, page=1, limit=10, **kw):
        # Ensure page and limit are integers and handle invalid input
        try:
            page = int(page)
            limit = int(limit)
            if page < 1:
                page = 1
            if limit < 1:
                limit = 10
        except ValueError:
            page = 1
            limit = 10

        # Calculate offset based on page and limit
        offset = (page - 1) * limit

        # Fetch the paginated students
        students = request.env['school_management.student'].sudo().search([], offset=offset, limit=limit)

        # Fetch the total count of students for pagination info
        total_students = request.env['school_management.student'].sudo().search_count([])

        # Prepare student data
        students_data = [{
            'id': student.id,
            'name': student.name,
            'age': student.age,
        } for student in students]

        # Include pagination metadata
        response_data = {
            'students': students_data,
            'pagination': {
                'current_page': page,
                'limit': limit,
                'total_students': total_students,
                'total_pages': (total_students + limit - 1) // limit,  # Ceiling division
            }
        }

        return request.make_response(
            json.dumps(response_data),
            headers=[('Content-Type', 'application/json')]
        )

        
    @http.route('/school_management/add_student', type='json', auth='public', methods=['POST'], csrf=False)
    def add_student(self, **kwargs):
        try:
            # Extract data from the POST request
            name = kwargs.get('name')
            roll_number = kwargs.get('roll_number')
            standard = kwargs.get('standard')
            section = kwargs.get('section')
            version = kwargs.get('version')
            admission_date = kwargs.get('admission_date')
            group = kwargs.get('group')
            gender=kwargs.get('gender')
            weight_in_kg = kwargs.get('weight_in_kg')
            school_id = kwargs.get('school_id')
            parent_id = kwargs.get('parent_id')

            print(name)

            # Validate required fields
            # if not name or not roll_number or not standard:
            #     return {
            #         'status': 'error',
            #         'message': 'Name, roll number, and standard are required fields.'
            #     }

            # Create a new student record
            student = request.env['school_management.student'].create({
                'name': name,
                'roll_number': roll_number,
                'standard': standard,
                'section': section,
                'version': version,
                'admission_date': admission_date,
                'group': group,
                'gender':gender,
                'weight_in_kg': float(weight_in_kg) if weight_in_kg else None,
                'school_id': int(school_id) if school_id else None,
                'parent_id': int(parent_id) if parent_id else None,
            })
            return {
                'status': 'success',
                'message': 'Student added successfully.',
                'student_id': student.id,
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }


    class CustomAuth(http.Controller):
        @http.route('/web/api/signin', type='json', auth="none", csrf=False, website=False, cors='*', methods=['POST'])
        def signin(self, **kw):
            print("aslkdfjlaskdfj")
            try:
                # Attempt to authenticate the user
                user_id = request.session.authenticate("odoo_17_cc_demo", request.params['login'],
                                                       request.params['password'])
                if not user_id:
                    return {'success': False, 'message': 'Authentication failed: Invalid login or password.'}
                # Create JWT token
                payload = {
                    'user_id': user_id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=240)  # Token expiration time
                }
                secret_key = 'your_secret_key'  # Replace with your actual secret key
                token = jwt.encode(payload, secret_key, algorithm='HS256')
                return {
                    'success': True,
                    'message': 'Sign in successful!',
                    'id': user_id,
                    'result': {
                        'token': token
                    }
                }
            except Exception as e:
                # In case of an error, return a message
                return {'success': False, 'message': str(e)}