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
    path('searches/', views.search_by_es, name='search_by_es'),
    path('container/<int:container_id>/', views.search_container, name='search_container'),
    path('scene/<int:scene_id>/', views.search_scene, name='search_scene'),
    path('category/<int:category_id>', views.search_category, name='search_category'),
    path('style/<int:style_id>', views.search_style, name='search_style'),
    path('add_container/', views.add_container, name='add_container'),
    path('add_scene/', views.add_scene, name='add_scene'),
    path('add_product_category/', views.add_product_category, name='add_product_category'),
    path('add_style/', views.add_style, name='add_style'),
    path('autoEdit/', views.auto_edit, name="autoEdit"),
    path('save_clip/', views.save_clip, name='save_clip'),
    path('contact/', views.contact, name='contact'),
    path('setting/', views.setting, name="setting"),
    path("download/", views.download, name="download"),
    path("download_video/", views.download_video, name="download_video"),
]
