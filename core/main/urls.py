from django.urls import path

from CarPricePredictionWeb.core.main.views import index, predict

urlpatterns = [
    path("", index, name="index"),
    path("predict/", predict, name="predict"),
]
