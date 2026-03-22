from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class Department(models.Model):
    """部门管理"""
    code = models.CharField('部门代码', max_length=20, unique=True)
    name = models.CharField('部门名称', max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='上级部门')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='部门经理')
    description = models.TextField('部门描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProductCategory(models.Model):
    """产品分类"""
    code = models.CharField('分类代码', max_length=20, unique=True)
    name = models.CharField('分类名称', max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='上级分类')
    description = models.TextField('分类描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类管理'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(models.Model):
    """产品管理"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('review', '审核中'),
        ('approved', '已批准'),
        ('released', '已发布'),
        ('obsolete', '已废弃'),
    ]

    product_code = models.CharField('产品编码', max_length=50, unique=True)
    name = models.CharField('产品名称', max_length=200)
    description = models.TextField('产品描述')
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, verbose_name='产品分类')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='负责部门')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.CharField('版本', max_length=20, default='1.0')
    
    # 技术参数
    specifications = models.TextField('技术规格', blank=True)
    weight = models.DecimalField('重量(kg)', max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField('尺寸', max_length=100, blank=True)
    material = models.CharField('材质', max_length=100, blank=True)
    
    # 管理信息
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_products', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_products', verbose_name='更新人')
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_products', verbose_name='批准人')
    approved_at = models.DateTimeField('批准时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品管理'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_code']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.product_code} - {self.name} v{self.version}"


class DocumentType(models.Model):
    """文档类型"""
    name = models.CharField('文档类型', max_length=100, unique=True)
    code = models.CharField('类型代码', max_length=20, unique=True)
    description = models.TextField('类型描述', blank=True)
    template_path = models.CharField('模板路径', max_length=200, blank=True)
    
    class Meta:
        verbose_name = '文档类型'
        verbose_name_plural = '文档类型管理'
        ordering = ['code']

    def __str__(self):
        return self.name


def document_upload_path(instance, filename):
    """文档上传路径"""
    product_code = instance.product.product_code
    doc_type = instance.doc_type.code
    version = instance.version
    return f'documents/{product_code}/{doc_type}/v{version}/{filename}'


class Document(models.Model):
    """文档管理"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('review', '审核中'),
        ('approved', '已批准'),
        ('released', '已发布'),
        ('obsolete', '已废弃'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents', verbose_name='关联产品')
    doc_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT, verbose_name='文档类型')
    title = models.CharField('文档标题', max_length=200)
    description = models.TextField('文档描述', blank=True)
    version = models.CharField('版本', max_length=20, default='1.0')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 文件信息
    file = models.FileField('文档文件', upload_to=document_upload_path)
    file_size = models.BigIntegerField('文件大小', default=0)
    file_type = models.CharField('文件类型', max_length=50, blank=True)
    
    # 版本控制
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='上一版本')
    version_comment = models.TextField('版本说明', blank=True)
    
    # 管理信息
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_documents', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_documents', verbose_name='更新人')
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '文档'
        verbose_name_plural = '文档管理'
        ordering = ['-created_at']
        unique_together = ['product', 'doc_type', 'version']
        indexes = [
            models.Index(fields=['product', 'doc_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.product.product_code} - {self.title} v{self.version}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1].lower()
        super().save(*args, **kwargs)


class BOMItem(models.Model):
    """BOM物料清单项"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_items', verbose_name='产品')
    component = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='used_in_boms', verbose_name='组件')
    quantity = models.DecimalField('数量', max_digits=10, decimal_places=2, default=1)
    unit = models.CharField('单位', max_length=20, default='个')
    position = models.CharField('位置/编号', max_length=50, blank=True)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'BOM项'
        verbose_name_plural = 'BOM物料清单'
        unique_together = ['product', 'component']
        ordering = ['position']

    def __str__(self):
        return f"{self.product.product_code} <- {self.component.product_code} x{self.quantity}"


class ChangeRequest(models.Model):
    """变更请求"""
    TYPE_CHOICES = [
        ('product', '产品变更'),
        ('document', '文档变更'),
        ('bom', 'BOM变更'),
        ('other', '其他变更'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('reviewing', '审核中'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('implemented', '已实施'),
    ]

    request_code = models.CharField('变更单号', max_length=50, unique=True)
    title = models.CharField('变更标题', max_length=200)
    description = models.TextField('变更描述')
    change_type = models.CharField('变更类型', max_length=20, choices=TYPE_CHOICES)
    priority = models.IntegerField('优先级', choices=[(1, '低'), (2, '中'), (3, '高'), (4, '紧急')], default=2)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 关联对象
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name='关联产品')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True, verbose_name='关联文档')
    
    # 审批流程
    requester = models.ForeignKey(User, on_delete=models.PROTECT, related_name='submitted_changes', verbose_name='申请人')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewing_changes', verbose_name='审核人')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_changes', verbose_name='批准人')
    
    # 时间信息
    requested_at = models.DateTimeField('申请时间', auto_now_add=True)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    approved_at = models.DateTimeField('批准时间', null=True, blank=True)
    implemented_at = models.DateTimeField('实施时间', null=True, blank=True)
    deadline = models.DateTimeField('要求完成时间', null=True, blank=True)
    
    # 结果
    review_comment = models.TextField('审核意见', blank=True)
    implementation_details = models.TextField('实施详情', blank=True)
    
    class Meta:
        verbose_name = '变更请求'
        verbose_name_plural = '变更请求管理'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['request_code']),
            models.Index(fields=['status']),
            models.Index(fields=['change_type']),
        ]

    def __str__(self):
        return f"{self.request_code} - {self.title}"


class Notification(models.Model):
    """系统通知"""
    TYPE_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('success', '成功'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收用户')
    title = models.CharField('通知标题', max_length=200)
    message = models.TextField('通知内容')
    notification_type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField('已读', default=False)
    related_object_type = models.CharField('关联对象类型', max_length=50, blank=True)
    related_object_id = models.IntegerField('关联对象ID', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '系统通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"