from rest_framework import serializers

from app.models.agencies import Agency


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
            "id",
            "title",
            "admin_privileges",
            "school_privileges",
            "access_school",
            "home_url",
            "logo_url",
            "street_address",
            "city",
            "state",
            "county",
            "zipcode",            
            "authorize_type",
            "jurisdiction",
            "calendar_year",
            "years_operation",
            "number_of_schools",
            "number_of_impacted_students",
            "domain",
            "annual_budget",
            "custom_fields",
            "agency_entity_fields",
            "school_entity_fields",
            "network_entity_fields",
            "board_member_fields",
            "agency_user_fields",
            "school_user_fields",
        ]


class AgencySchoolPrivilegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = [
            "school_privileges",
        ]
