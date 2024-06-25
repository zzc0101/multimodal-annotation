import os, json
import shutil


# 返回目录下的所有文件夹（用于选择标注的数据集）
def get_all_folders(directory):
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folders.append(item)
    # 返回一个排序后的新列表
    return sorted(folders)


# 统计目录下指定文件类型的个数
def count_json_files(directory, file_type):
    json_files = [f for f in os.listdir(directory) if f.endswith(file_type) and os.path.isfile(os.path.join(directory, f))]
    return len(json_files)


# 判断文件夹是否存在，不存在则创建
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


# 获取指定文件内容
def get_sorted_json_content(folder_path, index):
    # 列出文件夹中的所有文件
    files = os.listdir(folder_path)
    # 过滤出所有的 JSON 文件，并进行排序
    json_files = sorted([f for f in files if f.endswith('.json')])
    # 检查下标是否有效
    if index < 0 or index >= len(json_files):
        raise IndexError("Index out of range.")
    # 获取指定下标的 JSON 文件路径
    json_file_path = os.path.join(folder_path, json_files[index])
    # 读取 JSON 文件内容
    with open(json_file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content


# 判断指定目录中是否存在特定文件名（不含后缀）的文件
def file_exists_in_directory(directory, filename):
    # 遍历目录中的所有文件
    for file in os.listdir(directory):
        # 检查文件名是否匹配
        if file == filename:
            return True
    return False

# 获取指定目录中特定文件名的文件的索引
def get_file_index(directory, target_file):
    # 获取文件夹中的所有文件并排序
    files = sorted(os.listdir(directory))
    
    # 查找目标文件的下标
    if target_file in files:
        index = files.index(target_file)
        return index
    else:
        return 0

# 复制指定文件
def copy_specific_file(source_directory, destination_directory, file_name):
    # 构建源文件的完整路径
    source_file = os.path.join(source_directory, file_name)
    
    # 检查源文件是否存在
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"文件 '{source_file}' 不存在于源文件夹中。")

    # 如果目标文件夹不存在，则创建
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # 构建目标文件的完整路径
    destination_file = os.path.join(destination_directory, file_name)

    # 复制文件
    shutil.copy2(source_file, destination_file)