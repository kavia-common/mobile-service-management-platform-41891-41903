from marshmallow import Schema, fields
from marshmallow.validate import OneOf, Length, Range


class ServiceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=2, max=255))
    category = fields.Str(required=True, validate=Length(min=2, max=100))
    description = fields.Str(required=True)
    price_cents = fields.Int(required=True, validate=Range(min=0))
    duration_minutes = fields.Int(required=True, validate=Range(min=5))
    is_active = fields.Int(required=True, validate=OneOf([0, 1]))


class ServiceCreateSchema(Schema):
    name = fields.Str(required=True, validate=Length(min=2, max=255))
    category = fields.Str(required=True, validate=Length(min=2, max=100))
    description = fields.Str(required=True)
    price_cents = fields.Int(required=True, validate=Range(min=0))
    duration_minutes = fields.Int(required=True, validate=Range(min=5))


class UserPublicSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    full_name = fields.Str(required=True)
    role = fields.Str(required=True)


class SignupSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.Str(required=True, validate=Length(min=2, max=255))
    password = fields.Str(required=True, validate=Length(min=6, max=256))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=Length(min=1, max=256))


class AuthTokenSchema(Schema):
    access_token = fields.Str(required=True)
    token_type = fields.Str(required=True)
    user = fields.Nested(UserPublicSchema, required=True)


class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    service_id = fields.Int(required=True)
    status = fields.Str(required=True)
    notes = fields.Str(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    service = fields.Nested(ServiceSchema, dump_only=True)
    user = fields.Nested(UserPublicSchema, dump_only=True)


class OrderCreateSchema(Schema):
    service_id = fields.Int(required=True)
    notes = fields.Str(required=False, load_default="")


class OrderUpdateSchema(Schema):
    status = fields.Str(required=True, validate=OneOf(["requested", "scheduled", "in_progress", "completed", "cancelled"]))
    notes = fields.Str(required=False)
