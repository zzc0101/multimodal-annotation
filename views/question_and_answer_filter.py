from utils.file_util import count_json_files, get_all_folders
from config import config

# 计算出问答的所有文件
def query_data():
    list = []
    folders = get_all_folders(config.data_path)
    for i in folders:
        data = {}
        data['name'] = folders[i]
        data['count'] = count_json_files(config.data_path + folders[i], config.ANNOTATION_SUF)
        data['correct'] = count_json_files(config.data_path + folders[i], config)
        data['error'] = count_json_files(config.data_path + folders[i], config.ERROR_SUF)
        list.append(data)
    return list


