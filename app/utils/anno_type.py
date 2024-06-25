# 定义字典
attributes = {
    'filter': '问答筛选',
    'anno': '问答标注',
    'translate': '中英文对照'
}

# 访问属性值的函数
def get_attribute(key):
    return attributes.get(key)

# 更新属性值的函数
def set_attribute(key, value):
    attributes[key] = value
