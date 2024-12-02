from app import app
from models import db, Category

# Ensure app context is available
with app.app_context():
    # List of categories to add
    categories = [
        "Plumbing",
        "Electrical",
        "Cleaning",
        "Carpentry",
        "Painting",
        "Gardening"
    ]

    # Add categories to the database
    for category_name in categories:
        # Check if category already exists to avoid duplication
        if not Category.query.filter_by(name=category_name).first():
            category = Category(name=category_name)
            db.session.add(category)
    
    db.session.commit()
    print("Categories added successfully!")
