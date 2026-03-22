from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Department, ProductCategory, Product, 
    DocumentType, Document, BOMItem, 
    ChangeRequest, Notification
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager', 'parent', 'created_at')
    list_filter = ('parent',)
    search_fields = ('code', 'name', 'description')
    raw_id_fields = ('manager', 'parent')
    ordering = ('code',)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'created_at')
    list_filter = ('parent',)
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'category', 'department', 'status', 'version', 'created_at')
    list_filter = ('status', 'category', 'department')
    search_fields = ('product_code', 'name', 'description', 'specifications')
    raw_id_fields = ('created_by', 'updated_by', 'approved_by', 'category', 'department')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('product_code', 'name', 'description', 'category', 'department', 'status', 'version')
        }),
        ('技术参数', {
            'fields': ('specifications', 'weight', 'dimensions', 'material'),
            'classes': ('collapse',)
        }),
        ('管理信息', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at', 'approved_by', 'approved_at')
        }),
    )
    ordering = ('-created_at',)


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'doc_type', 'version', 'status', 'file_size_display', 'created_at')
    list_filter = ('status', 'doc_type', 'product')
    search_fields = ('title', 'description', 'product__product_code', 'product__name')
    raw_id_fields = ('product', 'doc_type', 'created_by', 'updated_by', 'previous_version')
    readonly_fields = ('file_size', 'file_type', 'created_at', 'updated_at')
    
    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = '文件大小'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('product', 'doc_type', 'title', 'description', 'version', 'status')
        }),
        ('文件信息', {
            'fields': ('file', 'file_size', 'file_type')
        }),
        ('版本控制', {
            'fields': ('previous_version', 'version_comment'),
            'classes': ('collapse',)
        }),
        ('管理信息', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at')
        }),
    )
    ordering = ('-created_at',)


@admin.register(BOMItem)
class BOMItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'component', 'quantity', 'unit', 'position', 'created_at')
    list_filter = ('unit', 'product')
    search_fields = ('product__product_code', 'product__name', 'component__product_code', 'component__name')
    raw_id_fields = ('product', 'component')
    ordering = ('product', 'position')


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('request_code', 'title', 'change_type', 'priority', 'status', 'requester', 'requested_at')
    list_filter = ('status', 'change_type', 'priority')
    search_fields = ('request_code', 'title', 'description')
    raw_id_fields = ('product', 'document', 'requester', 'reviewer', 'approver')
    readonly_fields = ('requested_at', 'reviewed_at', 'approved_at', 'implemented_at')
    
    fieldsets = (
        ('变更信息', {
            'fields': ('request_code', 'title', 'description', 'change_type', 'priority', 'status')
        }),
        ('关联对象', {
            'fields': ('product', 'document'),
            'classes': ('collapse',)
        }),
        ('审批流程', {
            'fields': ('requester', 'reviewer', 'approver', 'deadline')
        }),
        ('时间信息', {
            'fields': ('requested_at', 'reviewed_at', 'approved_at', 'implemented_at'),
            'classes': ('collapse',)
        }),
        ('结果信息', {
            'fields': ('review_comment', 'implementation_details'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-requested_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'title', 'message')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "标记为已读"
    
    actions = [mark_as_read]
    ordering = ('-created_at',)