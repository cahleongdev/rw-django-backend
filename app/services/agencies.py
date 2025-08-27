from app.models import School


def get_schools_by_agency(agency_id):
    try:
        # Query the School model to get all schools with matching agency_id
        schools = School.objects.filter(agency_id=agency_id)

        # Return just the IDs if you only need the IDs
        school_ids = schools.values_list("id", flat=True)

        return list(school_ids)
    except Exception as e:
        # Log the error and return empty list
        print(f"Error fetching schools for agency {agency_id}: {str(e)}")
        return []
