# 测试目录说明

本目录包含PyFTP服务器项目的所有测试文件。

## 测试文件列表

1. [test_refactor.py](file:///D:/project/pyFTP-server/tests/test_refactor.py) - 原始重构测试
2. [test_optimizations.py](file:///D:/project/pyFTP-server/tests/test_optimizations.py) - 优化功能测试
3. [test_log_optimizations.py](file:///D:/project/pyFTP-server/tests/test_log_optimizations.py) - 日志显示优化测试

## 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_refactor.py

# 运行测试并显示详细信息
python -m pytest -v
```