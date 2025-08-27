from rest_framework import serializers

from app.models.board_members import BoardMember
from app.serializers.schools import SchoolNameSerializer

class BoardMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardMember
        fields = [
            'id',
            'first_name',
            'last_name',
        ]

class BoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardMember
        fields = [
            'id',
            'first_name',
            'last_name',
            'start_term',
            'end_term',
        ]


class BoardMemberDetailSerializer(serializers.ModelSerializer):   
    class Meta:
        model = BoardMember
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'title',
            'start_term',
            'end_term',
            'custom_fields',
            'schools',
        ]
        read_only_fields = ["id"]
