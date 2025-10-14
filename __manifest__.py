{
    'name': 'Laptop Management',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Manajemen Peminjaman Laptop untuk Siswa',
    'description': """
Modul untuk mengelola data siswa, jurusan, kelas, dan peminjaman laptop.
""",
    'author': 'Project PKL',
    'depends': ['base'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/major_view.xml',
        'views/class_room_view.xml',
        'views/student_view.xml',
        'views/laptop_loan_view.xml',
        'views/teacher_view.xml',
        'views/menuitem.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
