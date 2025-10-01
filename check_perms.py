from app import create_app
from app.models.rbac import Permission

app = create_app()
with app.app_context():
    # Get role-related permissions
    perms = Permission.query.filter(Permission.name.like('%role%')).all()
    print('Role-related permissions:')
    for p in perms:
        print(f'  - {p.name}')
    
    # Get admin permissions
    admin_perms = Permission.query.filter(Permission.module == 'admin').all()
    print('\nAdmin permissions:')
    for p in admin_perms:
        print(f'  - {p.name}')
        
    # Get all permission names
    all_perms = Permission.query.all()
    print('\nAll permission names:')
    for p in all_perms:
        print(f'  - {p.name} ({p.module})')