from sqlalchemy.orm import Session
from app.models.user import Role, UserRole

def seed_roles(db: Session):
    """Ensure that default roles exist in the database."""
    existing_roles = {role.name for role in db.query(Role).all()}
    
    roles_to_add = []
    for role in UserRole:
        if role.value not in existing_roles:
            roles_to_add.append(Role(name=role.value))

    if roles_to_add:
        db.add_all(roles_to_add)
        db.commit()
        print("✅ Roles seeded successfully!")
    else:
        print("ℹ️ Roles already exist, skipping seeding.")
