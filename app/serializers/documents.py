from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from app.models.documents import Document
from app.models.schools import School
from app.models.users import User


class DocumentSerializer(serializers.ModelSerializer):
    parent_type = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "file_url",
            "name",
            "type",
            "year",
            "expiration_date",
            "created_at",
            "parent_type",
            "parent_id",
        ]
        read_only_fields = ["id", "created_at"]

    def get_parent_type(self, obj):
        return obj.parent_type.model

    def create(self, validated_data):
        # Get the content type and object ID from the request data
        request_data = self.context.get("request").data
        parent_type_name = request_data.get("parent_type")
        parent_id = request_data.get("parent_id")

        # Get the content type
        if parent_type_name == "school":
            parent_type = ContentType.objects.get_for_model(School)
        elif parent_type_name == "user":
            parent_type = ContentType.objects.get_for_model(User)
        elif parent_type_name == "board":
            parent_type = ContentType.objects.get_for_model(School)
            validated_data["year"] = "Board Documents"
        else:
            raise serializers.ValidationError(
                f"Invalid content type: {parent_type_name}"
            )

        # Add content type to validated data
        validated_data["parent_type"] = parent_type
        validated_data["parent_id"] = parent_id

        return super().create(validated_data)


class DocumentWithRelatedSerializer(DocumentSerializer):
    related_object = serializers.SerializerMethodField()

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ["related_object"]

    def get_related_object(self, obj):
        if obj.parent_type.model == "school":
            from app.serializers.schools import SchoolNameSerializer

            return SchoolNameSerializer(obj.parent_object).data
        elif obj.parent_type.model == "user":
            from app.serializers.users import UserNameSerializer

            return UserNameSerializer(obj.parent_object).data
        return None
