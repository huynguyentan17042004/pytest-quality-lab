from __future__ import annotations

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


def validate_schema(instance, schema: dict) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        path = ".".join(str(item) for item in error.absolute_path) or "$"
        raise ValidationError(f"schema mismatch at {path}: {error.message}")
