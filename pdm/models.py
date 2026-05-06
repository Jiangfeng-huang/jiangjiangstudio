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
        ('active', '在售'),
        ('inactive', '下架'),
        ('replaced', '已被替换新品'),
        ('not_for_sale', '不在售'),
        ('accessory', '配件'),
        ('discontinued', '停售'),
        ('coming_soon', '新品待上架'),
        ('not_released', '未上市'),
        ('clearance', '在售（清货）'),
    ]

    product_code = models.CharField('产品编码', max_length=50, unique=True)
    name = models.CharField('产品名称', max_length=200)
    description = models.TextField('产品描述')
    image = models.BinaryField('产品图片', null=True, blank=True)
    image_content_type = models.CharField('图片类型', max_length=100, null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, verbose_name='产品分类')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='负责部门')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.CharField('版本', max_length=20, default='1.0')
    
    # 技术参数
    
    
    # 产品汇总表字段
    chinese_category = models.CharField('通用名(中文)', max_length=200, blank=True)
    english_category = models.CharField('通用名(英文)', max_length=200, blank=True)
    brand = models.CharField('品牌', max_length=100, blank=True)
    model = models.CharField('产品型号', max_length=100, blank=True)
    supplier_model = models.CharField('工厂型号', max_length=100, blank=True)
    color = models.CharField('颜色', max_length=50, blank=True)
    battery_info = models.CharField('电池信息', max_length=200, blank=True)
    special_note = models.TextField('特殊说明', blank=True)
    short_name = models.CharField('短名称（英文）', max_length=100, blank=True)
    product_owner = models.CharField('产品负责人', max_length=100, blank=True)
    amazon_category = models.CharField('亚马逊类目', max_length=200, blank=True)
    product_size = models.CharField('单个产品尺寸', max_length=100, blank=True)
    package_size = models.CharField('单个产品的包装尺寸', max_length=100, blank=True, default='')
    product_weight = models.DecimalField('单个产品重量g', max_digits=10, decimal_places=2, null=True, blank=True)
    package_weight = models.DecimalField('单个产品含包装的重量g', max_digits=10, decimal_places=2, null=True, blank=True)
    carton_qty = models.IntegerField('满箱数量', null=True, blank=True)
    carton_dimension = models.CharField('满箱材积', max_length=100, blank=True, default='')
    carton_weight = models.DecimalField('满箱毛重(KG)', max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_period = models.IntegerField('保修期(月)', null=True, blank=True)
    file_link = models.CharField('文件链接', max_length=500, blank=True, default='')
    certification_file = models.CharField('认证文件', max_length=500, blank=True, default='')
    lead_time = models.IntegerField('交货期(天)', null=True, blank=True)
    operation = models.CharField('运营', max_length=100, blank=True, default='')
    platform_store = models.CharField('平台店铺', max_length=200, blank=True, default='')
    establishment_date = models.DateField('链接建立日期', null=True, blank=True)
    asin = models.CharField('ASIN', max_length=50, blank=True, default='')
    amazon_fnsku = models.CharField('Amazon FNSKU', max_length=50, blank=True, default='')
    amazon_sku = models.CharField('Amazon SKU', max_length=100, blank=True, default='')
    multiple_asin = models.CharField('Amazon-多个链接涉及ASIN', max_length=500, blank=True, default='')
    mrp = models.DecimalField('MRP', max_digits=10, decimal_places=2, null=True, blank=True)
    flipkart_sku = models.CharField('Flipkart（SKU ID）', max_length=100, blank=True, default='')
    flipkart_fsn = models.CharField('Flipkart（FSN ID）', max_length=100, blank=True, default='')
    flipkart_listing = models.CharField('Flipkart Listing ID', max_length=100, blank=True, default='')
    product_description = models.TextField('货描', blank=True, default='')
    remark = models.TextField('备注', blank=True, default='')
    ean_code = models.CharField('EAN码', max_length=20, blank=True, default='')
    
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
            models.Index(fields=['asin']),
            models.Index(fields=['ean_code']),
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


class Word(models.Model):
    """单词模型"""
    english = models.CharField('英文单词', max_length=200, unique=True)
    phonetic = models.CharField('音标', max_length=100, blank=True, default='')
    part_of_speech = models.CharField('词性', max_length=50, blank=True, default='')
    chinese = models.CharField('中文翻译', max_length=500)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '单词'
        verbose_name_plural = '单词管理'
        ordering = ['english']
    
    def __str__(self):
        return f"{self.english} - {self.chinese}"


class WrongWord(models.Model):
    """错误单词记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wrong_words', verbose_name='用户')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='wrong_records', verbose_name='单词')
    wrong_count = models.IntegerField('错误次数', default=1)
    last_wrong_at = models.DateTimeField('最后错误时间', auto_now=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '错误单词'
        verbose_name_plural = '错误单词记录'
        unique_together = ['user', 'word']
        ordering = ['-last_wrong_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.word.english}"


class WordProgress(models.Model):
    """单词学习进度"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_progress', verbose_name='用户')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='progress_records', verbose_name='单词')
    mastered = models.BooleanField('已掌握', default=False)
    reviewed_count = models.IntegerField('复习次数', default=0)
    last_reviewed_at = models.DateTimeField('最后复习时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '单词进度'
        verbose_name_plural = '单词学习进度'
        unique_together = ['user', 'word']
    
    def __str__(self):
        return f"{self.user.username} - {self.word.english} ({'已掌握' if self.mastered else '未掌握'})"