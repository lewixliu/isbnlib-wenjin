# isbnlib-wenjin
isbnlib-wenjin是一个isbnlib Python 插件，用于从国家图书馆的文津搜索（http://find.nlc.cn/）查找图书信息。

## 要求
需要安装如下Python模块，均可用pip从PyPI (https://pypi.org/)获取。
* isbnlib (version >= 3.9.1)
* beautifulsoup4 (version >= 4.7.1)


## 安装

#### 使用setup.py安装

命令如下
```shell
git clone https://github.com/lewixliu/isbnlib-wenjin
cd isbnlib-wenjin/
python setup.py check -s
python setup.py sdist bdist_wheel
```

## 使用
安装之后可以通过下面的Python示例代码来获取图书信息：

```python
import isbnlib

isbnlib.meta(isbn='9787111334620', service='wenjin')
```

## License
(c) 2024 Lewix -- Code available under LGPL v3 license
