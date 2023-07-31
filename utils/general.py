
def model_to_dict(model):
    """Convert SQLAlchemy model to a dictionary."""
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}

