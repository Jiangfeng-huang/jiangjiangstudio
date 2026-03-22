from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
import os

from .models import (
    Product, Document, BOMItem, ChangeRequest, 
    Notification, Department, ProductCategory, DocumentType
)
from .forms import (
    ProductForm, DocumentForm, BOMItemForm, 
    ChangeRequestForm
)


def health_check(request):
    """健康检查端点"""
    return HttpResponse("PDM系统运行正常！服务器时间: " + timezone.now().strftime("%Y-%m-%d %H:%M:%S"))


def public_home(request):
    """公开首页（无需登录）"""
    return render(request, 'pdm/public_home.html')


def test_access(request):
    """测试访问页面"""
    context = {
        'current_time': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return render(request, 'pdm/test_access.html', context)


@login_required
def index(request):
    """首页仪表板"""
    # 统计信息
    stats = {
        'total_products': Product.objects.count(),
        'total_documents': Document.objects.count(),
        'pending_changes': ChangeRequest.objects.filter(status__in=['draft', 'submitted', 'reviewing']).count(),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    
    # 最近的产品
    recent_products = Product.objects.order_by('-created_at')[:5]
    
    # 最近的文档
    recent_documents = Document.objects.order_by('-created_at')[:5]
    
    # 待处理的变更
    pending_changes = ChangeRequest.objects.filter(
        Q(status='submitted') | Q(status='reviewing')
    ).order_by('-requested_at')[:5]
    
    context = {
        'stats': stats,
        'recent_products': recent_products,
        'recent_documents': recent_documents,
        'pending_changes': pending_changes,
    }
    return render(request, 'pdm/index.html', context)


class ProductListView(LoginRequiredMixin, ListView):
    """产品列表"""
    model = Product
    template_name = 'pdm/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.all()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(product_code__icontains=search) |
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('-created_at')


class ProductDetailView(LoginRequiredMixin, DetailView):
    """产品详情"""
    model = Product
    template_name = 'pdm/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, CreateView):
    """创建产品"""
    model = Product
    form_class = ProductForm
    template_name = 'pdm/product_form.html'
    success_url = reverse_lazy('pdm:product_list')


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """更新产品"""
    model = Product
    form_class = ProductForm
    template_name = 'pdm/product_form.html'
    
    def get_success_url(self):
        return reverse_lazy('pdm:product_detail', kwargs={'pk': self.object.pk})


class DocumentListView(LoginRequiredMixin, ListView):
    """文档列表"""
    model = Document
    template_name = 'pdm/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Document.objects.all()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('-created_at')


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """文档详情"""
    model = Document
    template_name = 'pdm/document_detail.html'
    context_object_name = 'document'


class DocumentCreateView(LoginRequiredMixin, CreateView):
    """创建文档"""
    model = Document
    form_class = DocumentForm
    template_name = 'pdm/document_form.html'
    success_url = reverse_lazy('pdm:document_list')


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    """更新文档"""
    model = Document
    form_class = DocumentForm
    template_name = 'pdm/document_form.html'
    
    def get_success_url(self):
        return reverse_lazy('pdm:document_detail', kwargs={'pk': self.object.pk})


@login_required
def document_download(request, pk):
    """下载文档"""
    document = get_object_or_404(Document, pk=pk)
    response = FileResponse(document.file.open('rb'))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
    return response


class BOMListView(LoginRequiredMixin, ListView):
    """BOM列表"""
    model = BOMItem
    template_name = 'pdm/bom_list.html'
    context_object_name = 'bom_items'
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return BOMItem.objects.filter(product_id=product_id)


class BOMCreateView(LoginRequiredMixin, CreateView):
    """添加BOM项"""
    model = BOMItem
    form_class = BOMItemForm
    template_name = 'pdm/bom_form.html'
    
    def get_success_url(self):
        product_id = self.kwargs['product_id']
        return reverse_lazy('pdm:bom_list', kwargs={'product_id': product_id})


class ChangeRequestListView(LoginRequiredMixin, ListView):
    """变更请求列表"""
    model = ChangeRequest
    template_name = 'pdm/change_list.html'
    context_object_name = 'changes'
    paginate_by = 20
    
    def get_queryset(self):
        return ChangeRequest.objects.all().order_by('-requested_at')


class ChangeRequestDetailView(LoginRequiredMixin, DetailView):
    """变更请求详情"""
    model = ChangeRequest
    template_name = 'pdm/change_detail.html'
    context_object_name = 'change'


class ChangeRequestCreateView(LoginRequiredMixin, CreateView):
    """创建变更请求"""
    model = ChangeRequest
    form_class = ChangeRequestForm
    template_name = 'pdm/change_form.html'
    success_url = reverse_lazy('pdm:change_list')


class NotificationListView(LoginRequiredMixin, ListView):
    """通知列表"""
    model = Notification
    template_name = 'pdm/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


@login_required
def mark_notification_read(request, pk):
    """标记通知为已读"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('pdm:notification_list')


@login_required
def mark_all_notifications_read(request):
    """标记所有通知为已读"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('pdm:notification_list')


@login_required
def product_report(request):
    """产品报表"""
    status_stats = Product.objects.values('status').annotate(count=Count('id')).order_by('status')
    category_stats = Product.objects.values('category__name').annotate(count=Count('id')).order_by('category__name')
    recent_products = Product.objects.order_by('-created_at')[:10]
    
    context = {
        'status_stats': status_stats,
        'category_stats': category_stats,
        'recent_products': recent_products,
    }
    return render(request, 'pdm/reports/product_report.html', context)


@login_required
def document_report(request):
    """文档报表"""
    type_stats = Document.objects.values('doc_type__name').annotate(count=Count('id')).order_by('doc_type__name')
    status_stats = Document.objects.values('status').annotate(count=Count('id')).order_by('status')
    recent_documents = Document.objects.order_by('-created_at')[:10]
    
    context = {
        'type_stats': type_stats,
        'status_stats': status_stats,
        'recent_documents': recent_documents,
    }
    return render(request, 'pdm/reports/document_report.html', context)