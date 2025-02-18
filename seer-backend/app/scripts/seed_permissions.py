from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import Role, Permission

def seed_roles_and_permissions():
    db: Session = SessionLocal()
    try:
        # Define default roles
        default_roles = [
            {"name": "ADMIN", "permissions": ["MANAGE_USERS", "MANAGE_ROLES", "MANAGE_PERMISSIONS"]},
            {"name": "USER", "permissions": ["VIEW_CONTENT"]},
        ]

        # Ensure permissions exist first
        for role in default_roles:
            for permission_name in role["permissions"]:
                permission = db.query(Permission).filter(Permission.name == permission_name).first()
                if not permission:
                    new_permission = Permission(name=permission_name)
                    db.add(new_permission)
        db.commit()

        # Ensure roles exist and link permissions
        for role in default_roles:
            role_obj = db.query(Role).filter(Role.name == role["name"]).first()
            if not role_obj:
                role_obj = Role(name=role["name"])
                db.add(role_obj)
                db.commit()
                db.refresh(role_obj)

            # Assign permissions to role
            for permission_name in role["permissions"]:
                permission = db.query(Permission).filter(Permission.name == permission_name).first()
                if permission and permission not in role_obj.permissions:
                    role_obj.permissions.append(permission)
        
        db.commit()
        print("✅ Roles and permissions seeded successfully!")
    except Exception as e:
        print(f"❌ Error seeding roles and permissions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles_and_permissions()
