from allauth.account.views import LogoutView
from django.urls import path, include

from . import views
from .views import profile_view

urlpatterns = [
    path("", views.index, name="index"),
    path("welcome/", views.to_home, name="start"),
    path("home/", views.home_common, name="home-common"),
    path("pma-home/", views.home_pma, name="home-pma"),
    path("guest/", views.home_guest, name="home-guest"),
    path("accounts/logout/", LogoutView.as_view(), name="account-logout"),
    path('create-group/', views.group_create, name='group-create'),
    path('edit-group/<int:group_id>/', views.group_edit, name='group-edit'),
    path('delete-group/<int:group_id>/', views.delete_group, name='delete-group'),
    path('delete-group-pma/<int:group_id>/', views.delete_group_pma, name='delete-group-pma'),
    path('group/<int:group_id>/', views.group_page, name="group-page"),
    path('group/<int:group_id>/update_task/<int:task_id>/', views.update_task, name='update_task'),
    path('group/<int:group_id>/delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('group/<int:group_id>/delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('explore/', views.group_explore, name="group-explore"),
    path("upload-file/<int:group_id>/", views.upload_file, name="upload-file"),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete-file'),
    path('delete-file-pma/<int:file_id>/', views.delete_file_pma, name='delete-file-pma'),
    path('join-group/<int:group_id>/', views.join_group, name='join-group'),
    path('group/<int:group_id>/leave/', views.leave_group, name='leave-group'),
    path('profile/', profile_view, name='user-info'),
    path('group/<int:group_id>/join/', views.join_group, name='join-group'),
    path('group/<int:group_id>/manage-requests/', views.manage_join_requests, name='manage-requests'),
    path('group/<int:group_id>/approve-request/<int:request_id>/', views.approve_request, name='approve-request'), 
    path('group/<int:group_id>/reject-request/<int:request_id>/', views.reject_request, name='reject-request'),
    path('group/<int:group_id>/remove_member/<int:user_id>/', views.remove_member_from_group,
         name='remove_member_from_group'),

]