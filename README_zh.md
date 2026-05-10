# isbnlib-wenjin

isbnlib-wenjin 是一个非官方的 [isbnlib](https://github.com/xlcnd/isbnlib) 插件，用于从国家图书馆的[文津搜索](http://find.nlc.cn/)查找图书元数据。

## 依赖

- Python 3.7+
- [isbnlib2](https://pypi.org/project/isbnlib2/) >= 3.11.0（isbnlib 的 fork，兼容新版 setuptools）
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) >= 4.7.1

## 安装

#### 从 GitHub 安装

```bash
pip install git+https://github.com/lewixliu/isbnlib-wenjin.git
```

#### 本地开发安装

```bash
git clone https://github.com/lewixliu/isbnlib-wenjin
cd isbnlib-wenjin
pip install -e .
```

## 使用

安装后，isbnlib 中新增元数据查询服务 `wenjin`：

```python
import isbnlib

meta = isbnlib.meta('9787111334620', service='wenjin')
print(meta)
# {
#   'ISBN-13': '9787111334620',
#   'Title': '三元合金相图手册',
#   'Authors': ['张启运', '庄鸿寿'],
#   'Publisher': '机械工业出版社',
#   'Year': '2011',
#   'Language': 'zh'
# }
```

## 运行测试

```bash
# 仅运行单元测试（不需要网络）
pytest -m "not network" -v

# 运行全部测试（包含网络集成测试）
pytest -v

# 带覆盖率报告
pytest --cov=isbnlib_wenjin -m "not network"
```

## 已知限制

- **语言字段**固定为 `zh`（中文）。若需要检测实际语言，需要额外请求图书详情页。
- **HTML 解析**：解析器依赖文津当前的页面结构，若页面改版则需要更新解析器。
- **仅使用第一条结果**：当一个 ISBN 返回多条结果时，只使用第一条。

## License

(c) 2024 Lewix — 代码采用 [LGPL v3](LICENSE-LGPL.txt) 协议
