"""
PDM系统 - Django Admin配置
将Django管理后台标题改为PDM系统
"""

from django.contrib import admin

# 修改admin站点标题
admin.site.site_header = "PDM系统管理后台"
admin.site.site_title = "PDM系统"
admin.site.index_title = "PDM系统管理"