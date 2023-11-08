from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('student/', views.StudentNotification.as_view(), name='student_notifications'),
    path('adviser/', views.AdviserNotification.as_view(), name='adviser_notifications'),
    path('ktto/', views.KTTONotification.as_view(), name='ktto_notifications'),
    path('rdco/', views.RDCONotification.as_view(), name='rdco_notifications'),
    path('tbi/', views.TBINotification.as_view(), name='tbi_notifications'),
    path('itso/', views.ITSONotification.as_view(), name='itso_notifications'), 
]
