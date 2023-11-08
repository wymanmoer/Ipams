from django.conf.urls.static import static
from django.urls import path

from ipams import settings
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='records-index'),
    path('record/publishedRecords', views.PublishedRecords.as_view(), name='records-publish'),
    path('dashboard', views.Dashboard.as_view(), name='records-dashboard'),
    path('dashboard/manage/documents', views.ViewManageDocuments.as_view(), name='dashboard-manage-documents'),
    path('dashboard/manage/documents/record/<int:record_id>', views.ViewManageDocumentsRecord.as_view(), name='dashboard-manage-documents-record'),
    path('dashboard/manage/records', views.ViewManageRecords.as_view(), name='dashboard-manage-records'),
    path('dashboard/logs', views.LogsView.as_view(), name='dashboard-logs'),
    path('dashboard/manage/records/<int:record_id>', views.DashboardManageRecord.as_view(), name='dashboard-manage-record'),
    path('dashboard/manage/accounts', views.DashboardManageAccounts.as_view(), name='dashboard-manage-accounts'),
    path('dashboard/logs/record/<int:record_id>', views.DashboardLogsRecordView.as_view(), name='dashboard-logs-record'),
    path('record/<int:record_id>', views.ViewRecord.as_view(), name='records-view'),
    path('record/myrecords/<int:record_id>', views.MyRecordView.as_view(), name='records-myrecords-view'),
    

    #Upload Controller
    path('record/uploads/getUploadDocument/', views.UploadController.as_view(), name='get-upload-document'),
    path('record/uploads/createComment/', views.UploadController.as_view(), name='create-comment'),

    #View Record
    path('record/recordFile/<int:record_id>', views.ViewRecordFile.as_view(), name='view-record-file'),

    #Evaluation
    path('record/evaluation/<int:record_id>', views.EvaluationView.as_view(), name='records-evaluation-view'),
    path('record/evaluation/removeRecord/', views.EvaluationController.as_view(), name='remove-record'),
    path('record/evaluation/evaluateRecord/', views.EvaluationController.as_view(), name='evaluate-record'),




    path('record/approved/<int:record_id>', views.ApprovedRecordView.as_view(), name='records-approved-view'),
    path('record/declined/<int:record_id>', views.DeclinedRecordView.as_view(), name='records-declined-view'),

    #Add records URLs
    path('add/', views.AddRecordView.as_view(), name='records-add'),
    path('add/getUserList/', views.AddRecordController.as_view(), name='get-user-list'),
    path('add/getAdviserList/', views.AddRecordController.as_view(), name='get-adviser-list'),
    path('add/createRecord/', views.AddRecordController.as_view(), name='create-record'),
    path('add/createThesis/', views.AddResearchController.as_view(), name='create-thesis'),

    path('add/research/<int:research_record_id>', views.AddResearch.as_view(), name='records-add-research'),
    path('edit/<int:record_id>', views.Edit.as_view(), name='records-edit'),
    path('uploadexcel/', views.ParseExcel.as_view(), name='records-upload'),
    path('downloadformat/', views.download_format, name='records-download-format'),
    path('download/abstract/<int:record_id>', views.download_abstract, name='records-download-abstract'),
    path('download/document/<int:record_upload_id>', views.download_document, name='records-download-document'),

    #My record URLS
    path('records/user/', views.MyRecordsView.as_view(), name='records-myrecords'),
    path('records/user/getMyRecordsList/', views.MyRecordsController.as_view(), name='get-myrecords-list'),
    path('records/user/getComment/', views.MyRecordsController.as_view(), name='get-comments'),

    path('records/pending/', views.PendingRecordsView.as_view(), name='records-pending'),
    path('records/approved/', views.ApprovedRecordsView.as_view(), name='records-approved'),
    path('records/declined/', views.DeclinedRecordsView.as_view(), name='records-declined'),

    path('lockout', views.LockoutPage.as_view(), name='lockout-page'),
    path('dashboard/reset/accounts', views.LockedAccountsView.as_view(), name='reset-accounts'),
    path('delete/requests', views.get_all_delete_requests, name="all-delete-requests"),
    path('record/pending/delete/request/<int:record_id>', views.PendingDeleteRecordsView.as_view(), name='pending-delete-view'),
    path('download/requests', views.get_all_download_requests, name="all-download-requests"),
    path('approved/download/request', views.approved_download_requests, name="download-request"),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
