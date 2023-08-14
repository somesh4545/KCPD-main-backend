from pydantic import BaseModel

def model_to_dict(model):
    """Convert SQLAlchemy model to a dictionary."""
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}

def _convert(obj):
    if isinstance(obj, dict):
        return {k: _convert(v) for k, v in obj.items()}
    elif isinstance(obj, (list, set)):
        return [_convert(item) for item in obj]
    elif isinstance(obj, BaseModel):
        return model_to_dict(obj)
    else:
        return obj

def enhanced_model_to_dict(model):
    """Convert SQLAlchemy model to a dictionary, with support for nested dictionaries."""
    data = model_to_dict(model)
    return _convert(data)
