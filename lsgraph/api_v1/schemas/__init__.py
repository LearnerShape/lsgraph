from marshmallow import Schema, fields


class SkillSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    description = fields.String()


class OrganizationSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    root_skill = fields.Nested(SkillSchema(only=("id",)), dump_only=True)
    level_map = fields.Mapping(
        fields.String,
        fields.Float,
        missing={
            "No knowledge": 0.0,
            "Beginner": 1.0,
            "Intermediate": 2.0,
            "Advanced": 3.0,
            "Expert": 4.0,
        },
    )
