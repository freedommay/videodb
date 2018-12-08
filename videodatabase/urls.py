from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('home/', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('show/<int:video_id>/', views.detail, name='detail'),
    path('analysis/', views.analysis_video, name='analysis'),
    path("delete/<int:clip_id>", views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('container/<int:container_id>/', views.search_container, name='search_container'),
    path('scenes/<int:scenes_id>/', views.search_scenes, name='search_scenes'),
    path('category/<int:category_id>', views.search_category, name='search_category'),
    path('autoEdit/', views.auto_edit, name="autoEdit"),
    path('save_clip/', views.save_clip, name='save_clip'),
    path('contact/', views.contact, name='contact'),
    path('setting/', views.setting, name="setting"),
    path("download/", views.download, name="download"),
    path("download_video/", views.download_video, name="download_video"),
]
