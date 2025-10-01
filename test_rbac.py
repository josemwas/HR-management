from app import create_app
from app.models.rbac import Role, Permission

app = create_app()
with app.app_context():
    print('Roles count:', Role.query.count())
    print('Permissions count:', Permission.query.count())
    
    # List some roles
    roles = Role.query.limit(5).all()
    print('Sample roles:')
    for role in roles:
        print(f'  - {role.name}: {role.description}')
    
    # List some permissions  
    permissions = Permission.query.limit(5).all()
    print('Sample permissions:')
    for perm in permissions:
        print(f'  - {perm.name} ({perm.module}): {perm.description}')