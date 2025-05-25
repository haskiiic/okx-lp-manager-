#!/usr/bin/env python3
"""
配置测试脚本
"""

import sys
import os

# 清除Python缓存
import importlib
import app.config
importlib.reload(app.config)

from app.config import settings

print("🔧 配置测试")
print("=" * 50)
print(f"数据库URL: {settings.database_url}")
print(f"OKX API Key: {settings.okx_api_key}")
print(f"默认费率: {settings.default_fee_tier}")

# 测试数据库连接
if settings.database_url.startswith("mysql"):
    print("✅ 配置使用MySQL数据库")
else:
    print("❌ 配置仍在使用PostgreSQL")

print("=" * 50) 