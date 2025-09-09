{
    'name': 'Base Course Extend',
    'version': '1.0',
    'summary': 'Add session scheduling to courses',
    'depends': ['base_course'],  # ← tetap refer ke base_course
    'data': [
        'views/course_subject_view.xml',
    ],
    'installable': True,
}