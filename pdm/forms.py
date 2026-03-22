from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Document, BOMItem, ChangeRequest
from django.utils import timezone


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_code', 'name', 'description', 'category', 'department',
            'specifications', 'weight', 'dimensions', 'material'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'specifications': forms.Textarea(attrs={'rows': 6}),
            'weight': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def clean_product_code(self):
        product_code = self.cleaned_data['product_code']
        # 检查产品编码是否已存在（排除当前实例）
        if self.instance and self.instance.pk:
            if Product.objects.filter(product_code=product_code).exclude(pk=self.instance.pk).exists():
                raise ValidationError('该产品编码已存在！')
        else:
            if Product.objects.filter(product_code=product_code).exists():
                raise ValidationError('该产品编码已存在！')
        return product_code


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'product', 'doc_type', 'title', 'description', 
            'file', 'version_comment'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'version_comment': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 限制产品选择：只显示用户有权限的产品
        if self.user and not self.user.is_staff:
            # 这里可以根据实际权限逻辑进行过滤
            pass
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        doc_type = cleaned_data.get('doc_type')
        version = cleaned_data.get('version', '1.0')
        
        # 检查同一产品、同一类型、同一版本的文档是否已存在
        if self.instance and self.instance.pk:
            if Document.objects.filter(
                product=product, 
                doc_type=doc_type, 
                version=version
            ).exclude(pk=self.instance.pk).exists():
                raise ValidationError('该产品、类型和版本的文档已存在！')
        else:
            if Document.objects.filter(
                product=product, 
                doc_type=doc_type, 
                version=version
            ).exists():
                raise ValidationError('该产品、类型和版本的文档已存在！')
        
        return cleaned_data
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 检查文件大小（限制为10MB）
            max_size = 10 * 1024 * 1024  # 10MB
            if file.size > max_size:
                raise ValidationError(f'文件大小不能超过10MB。当前文件大小为{file.size/1024/1024:.1f}MB。')
            
            # 检查文件类型
            allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.jpg', '.png', '.dwg', '.step', '.stp']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(f'不支持的文件类型。允许的类型：{", ".join(allowed_extensions)}')
        
        return file


class BOMItemForm(forms.ModelForm):
    class Meta:
        model = BOMItem
        fields = ['component', 'quantity', 'unit', 'position', 'remark']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'remark': forms.Textarea(attrs={'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        component = cleaned_data.get('component')
        quantity = cleaned_data.get('quantity')
        
        if component and quantity:
            # 检查数量是否为正数
            if quantity <= 0:
                raise ValidationError('数量必须大于0！')
            
            # 检查组件是否是自己（避免循环引用）
            # 这个检查需要在视图中获取product_id后进行
            # 这里只做基本检查
            
        return cleaned_data


class ChangeRequestForm(forms.ModelForm):
    class Meta:
        model = ChangeRequest
        fields = [
            'title', 'description', 'change_type', 'priority',
            'product', 'document', 'deadline'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置deadline的初始值为3天后
        if not self.instance.pk:
            self.initial['deadline'] = timezone.now() + timezone.timedelta(days=3)
    
    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise ValidationError('截止时间不能早于当前时间！')
        return deadline
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        document = cleaned_data.get('document')
        change_type = cleaned_data.get('change_type')
        
        # 根据变更类型验证关联对象
        if change_type == 'product' and not product:
            raise ValidationError('产品变更必须关联产品！')
        elif change_type == 'document' and not document:
            raise ValidationError('文档变更必须关联文档！')
        elif change_type == 'bom' and not product:
            raise ValidationError('BOM变更必须关联产品！')
        
        return cleaned_data