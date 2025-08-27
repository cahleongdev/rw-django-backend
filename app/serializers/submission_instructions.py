from rest_framework import serializers

from app.models.submission_instructions import SubmissionInstruction


class SubmissionInstructionSerializer(serializers.ModelSerializer):
    questions = serializers.JSONField()

    class Meta:
        model = SubmissionInstruction
        fields = [
            "id",
            "type",
            "auto_accept",
            "allow_submission",
            "questions",
            "accepted_files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_questions(self, value):
        """
        Validate the questions JSON structure
        """

        if not isinstance(value, list):
            raise serializers.ValidationError("Questions must be a JSON object")

        if len(value) > 10:
            raise serializers.ValidationError("Questions must be less than 10")

        for index, question in enumerate(value):
            if not isinstance(question, dict):
                raise serializers.ValidationError("Each question must be an object")

            if (
                question.get("type") == "multiple_choice"
                or question.get("type") == "single_choice"
            ):
                if not question.get("options"):
                    raise serializers.ValidationError(
                        f"Question {index + 1} options are required"
                    )

                if len(question.get("options")) < 2:
                    raise serializers.ValidationError(
                        f"Question {index + 1} options must be at least 2"
                    )

                if len(question.get("options")) > 10:
                    raise serializers.ValidationError(
                        f"Question {index + 1} options must be less than 10"
                    )

        return value

    # def validate_accepted_files(self, value):
    #     """
    #     Validate the accepted_files JSON structure
    #     Example valid structure:
    #     [
    #         {
    #             "type": "pdf",
    #             "max_size": 10,  # in MB
    #             "required": true
    #         },
    #         {
    #             "type": "image",
    #             "formats": ["jpg", "png"],
    #             "max_size": 5,
    #             "required": false
    #         }
    #     ]
    #     """
    #     if not isinstance(value, list):
    #         raise serializers.ValidationError("Accepted files must be a list")

    #     for file_type in value:
    #         if not isinstance(file_type, dict):
    #             raise serializers.ValidationError("Each file type must be an object")

    #         required_fields = ['type', 'max_size', 'required']
    #         for field in required_fields:
    #             if field not in file_type:
    #                 raise serializers.ValidationError(f"Missing required field: {field}")

    #         if not isinstance(file_type['max_size'], (int, float)):
    #             raise serializers.ValidationError("max_size must be a number")

    #         if not isinstance(file_type['required'], bool):
    #             raise serializers.ValidationError("required must be a boolean")

    #     return value
