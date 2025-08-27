from django.urls import path

from app.views.rubrics import RubricAPI, RubricPKAPI
from app.views.rubrics_score import RubricScoreAPI, RubricScorePKAPI

urlpatterns = [
    path("", RubricAPI.as_view(), name="rubric-list-create"),
    path("<str:pk>/", RubricPKAPI.as_view(), name="rubric-detail"),
    path("scores/<str:rubric_pk>/", RubricScoreAPI.as_view(), name="rubric-score-list"),
    path(
        "score_detail/<str:pk>/", RubricScorePKAPI.as_view(), name="rubric-score-detail"
    ),
]
