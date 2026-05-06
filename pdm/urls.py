from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'pdm'

urlpatterns = [
    # 健康检查（无需登录）
    path('health/', views.health_check, name='health_check'),
    path('public/', views.public_home, name='public_home'),
    path('test/', views.test_access, name='test_access'),
    path('simple/', views.simple_test, name='simple_test'),
    path('manual/', views.user_manual, name='user_manual'),
    path('portal/', views.access_portal, name='access_portal'),
    
    # 首页
    path('', views.index, name='index'),
    
    # 认证相关
    path('login/', auth_views.LoginView.as_view(template_name='pdm/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(http_method_names=['get', 'post', 'options'], template_name='pdm/login.html'), name='logout'),
    
    # 产品管理
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/export/', views.product_export, name='product_export'),
    path('products/import/', views.product_import, name='product_import'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    
    # 文档管理
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('documents/create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/update/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),
    
    # BOM管理
    path('products/<int:product_id>/bom/', views.BOMListView.as_view(), name='bom_list'),
    path('products/<int:product_id>/bom/add/', views.BOMCreateView.as_view(), name='bom_create'),
    
    # 变更管理
    path('changes/', views.ChangeRequestListView.as_view(), name='change_list'),
    path('changes/<int:pk>/', views.ChangeRequestDetailView.as_view(), name='change_detail'),
    path('changes/create/', views.ChangeRequestCreateView.as_view(), name='change_create'),
    
    # 通知管理
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # 报表
    path('reports/products/', views.product_report, name='product_report'),
    path('reports/documents/', views.document_report, name='document_report'),
    
    # 背单词功能
    path('words/', views.word_list, name='word_list'),
    path('words/import/', views.word_import, name='word_import'),
    path('words/import/docx/', views.word_import_docx, name='word_import_docx'),
    path('words/practice/', views.word_practice, name='word_practice'),
    path('words/check/', views.word_check, name='word_check'),
    path('words/wrong/', views.wrong_word_list, name='wrong_word_list'),
    path('words/wrong/<int:wrong_word_id>/clear/', views.clear_wrong_word, name='clear_wrong_word'),
]