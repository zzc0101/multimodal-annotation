from app.utils import file_util
from config import config

# 计算出问答筛选的所有文件
def query_data():
    list = []
    root_folders = config.QA_ANNOTATION_FILE_PATH
    result_folders = config.QA_ANNOTATION_SAVE_PATH
    folders = file_util.get_all_folders(root_folders)
    for name in folders:
        data = {}
        data['name'] = name
        save_path = result_folders + '/' + name
        correct_path = result_folders + '/' + name + '/' + config.CORRECT_FILE
        error_path = result_folders + '/' + name + '/' + config.ERROR_FILE
        # 问价不存在则创建文件
        file_util.create_folder(save_path)
        file_util.create_folder(correct_path)
        file_util.create_folder(error_path)
        # 统计文件数量
        data['count'] = file_util.count_json_files(root_folders + '/' + name, config.ANNOTATION_SUF)
        data['correct'] = file_util.count_json_files(correct_path, config.ANNOTATION_SUF)
        data['error'] = file_util.count_json_files(error_path, config.ANNOTATION_SUF)
        list.append(data)
    return list





