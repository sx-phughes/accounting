from django.urls import path
from pages import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "connectToQuickbooks",
        views.connectToQuickbooks,
        name="connectToQuickbooks",
    ),
    path(
        r"^(?i)signInWithIntuit/?$",
        views.signInWithIntuit,
        name="signInWithIntuit",
    ),
    path(r"^(?i)getAppNow/?$", views.getAppNow, name="getAppNow"),
    path(
        r"^(?i)authCodeHandler/?$",
        views.authCodeHandler,
        name="authCodeHandler",
    ),
    path(r"^(?i)disconnect/?$", views.disconnect, name="disconnect"),
    path(r"^(?i)apiCall/?$", views.apiCall, name="apiCall"),
    path(r"^(?i)connected/?$", views.connected, name="connected"),
    path(
        r"^(?i)refreshTokenCall/?$",
        views.refreshTokenCall,
        name="refreshTokenCall",
    ),
]
