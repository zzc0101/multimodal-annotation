import os


# 返回目录下的所有文件夹（用于选择标注的数据集）
def get_all_folders(directory):
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folders.append(item)
    return folders


# 统计目录下指定文件的个数
def count_json_files(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json') and os.path.isfile(os.path.join(directory, f))]
    return len(json_files)