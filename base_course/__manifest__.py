{
    "name": "Base Course",
    "summary": """Base Course Module""",
    "description": """Base Course Module""",
    "author": "SMK AS",
    "maintainers": ["{Habil}"],
    "website": "",
    "category": "Customizations",
    "version": "17.0.1.0.1",
    "depends": ['base'],
    "data": [
        "security/ir.model.access.csv",
        "views\course_subject_view.xml",
        "views\course_order_view.xml",
        "views\menuitems.xml",

    ],
    # 'post_init_hook': 'post_init_hook',
    "application": False,
    "installable": True,
    "auto_install": False,
    "external_dependencies": {"python": []},
}