from app.utils import file_util, img_file, data_parse, anno_type
from config import config
import os, json
from app.services import operator_record

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


# 根据文件名称查询当前文件的对应下标
def get_current_index(dataset: str, file_name: str):
    source_root_folders = config.QA_ANNOTATION_FILE_PATH + '/' + dataset
    return file_util.get_file_index(source_root_folders, file_name)
    

# 页面数据响应
def get_anno_data(dataset: str, current_index: int):
    response_data = {}
    source_root_folders = config.QA_ANNOTATION_FILE_PATH + '/' + dataset
    save_root_folders = config.QA_ANNOTATION_SAVE_PATH + '/' + dataset
    correct_path = save_root_folders + '/' + config.CORRECT_FILE
    error_path = save_root_folders + '/' + config.ERROR_FILE
    data_count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    response_data['total'] = data_count
    if current_index < 0 and current_index >= data_count:
        raise BaseException('数据获取异常！')
    data_json = file_util.get_sorted_json_content(source_root_folders, current_index)
    data = {}
    data['image'] = img_file.set_image_url(data_json['image'])
    data_json['image'].startswith('/')
    # 提取文件名，不包含路径
    file_name_with_ext = data_json['image'].split('/')[-1]
    # 分离文件名和扩展名
    file_name = file_name_with_ext.rsplit('.', 1)[0]
    data['correctFlag'] = True
    if file_util.file_exists_in_directory(correct_path, file_name + config.ANNOTATION_SUF):
        data['saveFlag'] = True
        data['correctFlag'] = True
        with open(correct_path + '/' + file_name + config.ANNOTATION_SUF, 'r', encoding='utf-8') as file:
            data_json = json.load(file)
    elif file_util.file_exists_in_directory(error_path, file_name + config.ANNOTATION_SUF):
        data['saveFlag'] = True
        data['correctFlag'] = False
        with open(error_path + '/' + file_name + config.ANNOTATION_SUF, 'r', encoding='utf-8') as file:
            data_json = json.load(file)
    else:
        data['saveFlag'] = False
    data['fileName'] = file_name
    try:
        extracted_values = data_parse.extract_values(data_json, 'value')
        for i, value in enumerate(extracted_values):
            if i == 0:
                data['questionValue'] = value
            else:
                data['answerValue'] = value
    except Exception as e:
        raise BaseException(f'数据解析失败 {e}！')
    response_data['currentIndex'] = current_index
    response_data['data'] = data
    return response_data


# 页面数据保存
def save_anno_data(data_json):
    source_root_folders = config.QA_ANNOTATION_FILE_PATH + '/' + str(data_json['datasetName'])
    root_folders = config.QA_ANNOTATION_SAVE_PATH + '/' + str(data_json['datasetName'])
    correct_path = root_folders + '/' + config.CORRECT_FILE
    error_path = root_folders + '/' + config.ERROR_FILE

    # 通过文件名称查找对应的文件并删除
    if not file_util.file_exists_in_directory(source_root_folders, data_json['fileName']+config.ANNOTATION_SUF):
        raise BaseException('文件不存在！')

    if file_util.file_exists_in_directory(correct_path, data_json['fileName']+config.ANNOTATION_SUF):
        os.remove(correct_path+'/'+data_json['fileName']+config.ANNOTATION_SUF)
    
    if file_util.file_exists_in_directory(error_path, data_json['fileName']+config.ANNOTATION_SUF):
        os.remove(error_path+'/'+data_json['fileName']+config.ANNOTATION_SUF)

    # 写入到文件夹中，同时存在错误文件内容的修改
    if data_json['correctFlag']:
        # 将文件保存在正确的文件夹中
        file_util.copy_specific_file(source_root_folders, correct_path, data_json['fileName']+config.ANNOTATION_SUF)
    else:
        with open(source_root_folders + '/' + data_json['fileName']+config.ANNOTATION_SUF, 'r', encoding='utf-8') as file:
            content = json.load(file)

        # 修改第二个 conversation 中的 value
        if "conversations" in content and len(content["conversations"]) > 1:
            content["conversations"][1]["value"] = data_json['answerValue']
        
        # 将修改后的数据保存回文件
        with open(error_path + '/' + data_json['fileName']+config.ANNOTATION_SUF, 'w', encoding='utf-8') as file:
            json.dump(content, file, ensure_ascii=False, indent=4)
    
    count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    correctCount = file_util.count_json_files(correct_path, config.ANNOTATION_SUF)
    errorCount = file_util.count_json_files(error_path, config.ANNOTATION_SUF)
    # 保存操作记录
    load_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    if load_data is None:
        operator_record.add_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('filter'), preview=data_json['fileName']+config.ANNOTATION_SUF, count=count, correctCount=correctCount, errorCount=errorCount)
    else:
        query_data = operator_record.query_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('filter'))
        if query_data is None:
            operator_record.add_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('filter'), preview=data_json['fileName']+config.ANNOTATION_SUF, count=count, correctCount=correctCount, errorCount=errorCount)
        else:
            operator_record.update_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('filter'), preview=data_json['fileName']+config.ANNOTATION_SUF, count=count, correctCount=correctCount, errorCount=errorCount)
    operator_record.save_json(config.OPERATION_RECORD_PATH, load_data)
