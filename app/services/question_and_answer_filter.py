from app.utils import file_util, img_file, data_parse, anno_type
from config import config
import os, json, datetime
from app.services import operator_record

# 计算出问答筛选的所有文件
def query_data():
    """
    查询问答筛选的所有文件，并返回包含每个文件信息的列表。
    """
    list = []
    root_folders = config.QA_ANNOTATION_FILE_PATH
    result_folders = config.QA_ANNOTATION_SAVE_PATH
    folders = file_util.get_all_folders(root_folders)
    
    for name in folders:
        data = {
            'name': name,
            'isSync': False,
            'count': file_util.count_json_files(os.path.join(root_folders, name), config.ANNOTATION_SUF),
            'correct': file_util.count_json_files(os.path.join(result_folders, name, config.CORRECT_FILE), config.ANNOTATION_SUF),
            'error': file_util.count_json_files(os.path.join(result_folders, name, config.ERROR_FILE), config.ANNOTATION_SUF)
        }
        
        save_path = os.path.join(result_folders, name)
        correct_path = os.path.join(save_path, config.CORRECT_FILE)
        error_path = os.path.join(save_path, config.ERROR_FILE)
        
        # 创建文件夹
        file_util.create_folder(save_path)
        file_util.create_folder(correct_path)
        file_util.create_folder(error_path)
        
        # 查询操作记录
        record_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
        load_data = operator_record.query_entry(record_data, name, anno_type.get_attribute('filter'))
        if load_data:
            data['isSync'] = load_data.get('isSync', False)
        
        list.append(data)
    
    return list


# 根据文件名称查询当前文件的对应下标
def get_current_index(dataset: str, file_name: str) -> int:
    """
    获取文件名称在数据集中的下标。
    """
    source_root_folders = os.path.join(config.QA_ANNOTATION_FILE_PATH, dataset)

    if not os.path.exists(source_root_folders):
        return 0

    return file_util.get_file_index(source_root_folders, file_name)


# 同步标注数据
def sync_data(datasetName: str) -> dict:
    """
    同步标注数据。
    """
    response_data = {
        'code': 200,
        'message': '同步成功！'
    }
    
    source_error_folder = os.path.join(config.QA_ANNOTATION_SAVE_PATH, datasetName, config.ERROR_FILE)
    source_correct_folder = os.path.join(config.QA_ANNOTATION_SAVE_PATH, datasetName, config.CORRECT_FILE)
    
    if not os.path.exists(source_error_folder) or not os.path.exists(source_correct_folder):
        response_data.update({'code': 500, 'message': '同步失败，同步数据集不存在！'})
        return response_data
    
    load_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    query_data = operator_record.query_entry(load_data, datasetName, anno_type.get_attribute('filter'))
    
    if not query_data:
        response_data.update({'code': 500, 'message': '同步失败，请先标注！'})
        return response_data
    
    operator_record.update_entry(load_data, datasetName, anno_type.get_attribute('filter'), isSync=True)
    operator_record.save_json(config.OPERATION_RECORD_PATH, load_data)
    
    target_merge = os.path.join(config.QA_MERGE_FILE_PATH, datasetName)
    file_util.copy_files(source_folder=source_correct_folder, destination_folder=target_merge)
    
    return response_data


# 页面数据响应
def get_anno_data(dataset: str, current_index: int) -> dict:
    """
    获取当前索引的标注数据。
    """
    response_data = {}
    source_root_folders = os.path.join(config.QA_ANNOTATION_FILE_PATH, dataset)
    save_root_folders = os.path.join(config.QA_ANNOTATION_SAVE_PATH, dataset)
    correct_path = os.path.join(save_root_folders, config.CORRECT_FILE)
    error_path = os.path.join(save_root_folders, config.ERROR_FILE)
    
    data_count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    response_data['total'] = data_count
    
    if current_index < 0 or current_index >= data_count:
        raise ValueError('数据获取异常！')
    
    data_json = file_util.get_sorted_json_content(source_root_folders, current_index)
    data = {
        'image': img_file.set_image_url(data_json['image']),
        'correctFlag': True,
        'fileName': os.path.splitext(os.path.basename(data_json['image']))[0]
    }
    
    if file_util.file_exists_in_directory(correct_path, f"{data['fileName']}{config.ANNOTATION_SUF}"):
        data['saveFlag'] = True
        data['correctFlag'] = True
        with open(os.path.join(correct_path, f"{data['fileName']}{config.ANNOTATION_SUF}"), 'r', encoding='utf-8') as file:
            data_json = json.load(file)
    elif file_util.file_exists_in_directory(error_path, f"{data['fileName']}{config.ANNOTATION_SUF}"):
        data['saveFlag'] = True
        data['correctFlag'] = False
        with open(os.path.join(error_path, f"{data['fileName']}{config.ANNOTATION_SUF}"), 'r', encoding='utf-8') as file:
            data_json = json.load(file)
    else:
        data['saveFlag'] = False
    
    try:
        extracted_values = data_parse.extract_values(data_json, 'value')
        data['questionValue'] = extracted_values[0] if extracted_values else ""
        data['answerValue'] = extracted_values[1] if len(extracted_values) > 1 else ""
    except Exception as e:
        raise ValueError(f'数据解析失败: {e}！')
    
    response_data.update({
        'currentIndex': current_index,
        'data': data
    })
    return response_data


# 页面数据保存
def save_anno_data(data_json: dict):
    """
    保存标注数据。
    """
    source_root_folders = os.path.join(config.QA_ANNOTATION_FILE_PATH, data_json['datasetName'])
    root_folders = os.path.join(config.QA_ANNOTATION_SAVE_PATH, data_json['datasetName'])
    correct_path = os.path.join(root_folders, config.CORRECT_FILE)
    error_path = os.path.join(root_folders, config.ERROR_FILE)

    file_path = f"{data_json['fileName']}{config.ANNOTATION_SUF}"
    
    exists_flag = False

    # 校验文件是否存在
    if not file_util.file_exists_in_directory(source_root_folders, file_path):
        raise FileNotFoundError('文件不存在！')

    # 如果文件存在于正确或错误文件夹中，先删除旧文件
    for path in [correct_path, error_path]:
        if file_util.file_exists_in_directory(path, file_path):
            exists_flag = True
            os.remove(os.path.join(path, file_path))

    if data_json['correctFlag']:
        # 将文件保存在正确的文件夹中
        file_util.copy_specific_file(source_root_folders, correct_path, file_path)
    else:
        with open(os.path.join(source_root_folders, file_path), 'r', encoding='utf-8') as file:
            content = json.load(file)

        if "conversations" in content and len(content["conversations"]) > 1:
            content["conversations"][1]["value"] = data_json['answerValue']
        
        # 保存修改后的数据
        with open(os.path.join(error_path, file_path), 'w', encoding='utf-8') as file:
            json.dump(content, file, ensure_ascii=False, indent=4)
    
    # 统计文件数量
    count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    correctCount = file_util.count_json_files(correct_path, config.ANNOTATION_SUF)
    errorCount = file_util.count_json_files(error_path, config.ANNOTATION_SUF)
    
    # 保存操作记录
    load_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    query_data = operator_record.query_entry(load_data, data_json['datasetName'], anno_type.get_attribute('filter'))
    date_data = {}
    if not query_data:
        date_data[today_str] = 1
        operator_record.add_entry(load_data, data_json['datasetName'], anno_type.get_attribute('filter'), 
                                  preview=file_path, count=count, correctCount=correctCount, errorCount=errorCount, isSync=False, date=date_data)
    else:
        date_data = query_data.get('date', {})
        if exists_flag is False:
            date_data[today_str] = date_data.get(today_str, 0) + 1
        operator_record.update_entry(load_data, data_json['datasetName'], anno_type.get_attribute('filter'), 
                                     preview=file_path, count=count, correctCount=correctCount, errorCount=errorCount, isSync=False, date=date_data)
    operator_record.save_json(config.OPERATION_RECORD_PATH, load_data)
