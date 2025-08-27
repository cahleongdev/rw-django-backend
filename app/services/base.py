from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from app.utils.pagination import CustomPagination


def process_serializer(
    serializer_class,
    data,
    success_status=status.HTTP_201_CREATED,
    original_object=None,
    **kwargs
):
    if original_object is None:
        serializer = serializer_class(data=data, partial=True)
    else:
        serializer = serializer_class(original_object, data=data, partial=True)

    if serializer.is_valid():
        serializer.save(**kwargs)
        return Response(serializer.data, status=success_status)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def filterObjects(filter_fields, object_class):
    query = Q()
    for field, value in filter_fields.items():
        if value is not None:
            query &= Q(**{field: value})
    return object_class.objects.filter(query)


def get_paginated_filtered_data(
    req, model, serializer_class, filter_kwargs, page_size=10
):
    queryset = model.objects.filter(**filter_kwargs)
    paginator = CustomPagination()
    paginator.page_size = page_size
    paginated_queryset = paginator.paginate_queryset(queryset, req)
    serializer = serializer_class(paginated_queryset, many=True)
    return paginator.get_paginated_response(serializer.data)

def get_filtered_data(model, serializer_class, filter_kwargs):
    queryset = model.objects.filter(**filter_kwargs)
    serializer = serializer_class(queryset, many=True)
    return serializer.data
