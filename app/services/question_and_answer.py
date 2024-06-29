from app.utils import file_util, img_file, data_parse, anno_type
from config import config
import os, json, datetime
from app.services import operator_record

# 计算出问答筛选的所有文件
def query_data():
    """
    查询问答筛选的所有文件，并统计标注和修改文件的数量。
    """
    list = []
    root_folders = config.QA_ANNOTATION_FILE_PATH
    anno_folders = config.QA_ANNOTATION_SAVE_PATH
    modify_folders = config.QA_ANNOTATION_MODIFICATION_FILE_PATH
    folders = file_util.get_all_folders(root_folders)
    
    for name in folders:
        data = {}
        data['name'] = name
        anno_path = os.path.join(anno_folders, name, config.ERROR_FILE)
        modify_path = os.path.join(modify_folders, name)
        data['anno'] = 0
        data['modify'] = 0
        data['isMerge'] = False
        
        if os.path.exists(anno_path):
            data['anno'] = file_util.count_json_files(anno_path, config.ANNOTATION_SUF)
        
        if data['anno'] == 0:
            continue
        
        if os.path.exists(modify_path):
            data['modify'] = file_util.count_json_files(modify_path, config.ANNOTATION_SUF)
        
        # 查询操作记录
        record_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
        load_data = operator_record.query_entry(record_data, name, anno_type.get_attribute('anno'))
        
        if load_data is not None:
            data['isMerge'] = load_data['isMerge']
        
        list.append(data)
    
    return list


# 根据文件名称查询当前文件的对应下标
def get_current_index(dataset: str, file_name: str):
    """
    根据文件名称查询当前文件的对应下标。
    """
    source_root_folders = os.path.join(config.QA_ANNOTATION_SAVE_PATH, dataset, config.ERROR_FILE)
    
    if not os.path.exists(source_root_folders):
        return 0
    
    return file_util.get_file_index(source_root_folders, file_name)


# 页面数据响应
def get_anno_data(dataset: str, current_index: int):
    """
    获取标注数据，并返回页面响应数据。
    """
    response_data = {}
    source_root_folders = os.path.join(config.QA_ANNOTATION_SAVE_PATH, dataset, config.ERROR_FILE)
    save_root_folders = os.path.join(config.QA_ANNOTATION_MODIFICATION_FILE_PATH, dataset)
    data_count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    response_data['total'] = data_count
    
    if current_index < 0 or current_index >= data_count:
        raise Exception('数据获取异常！')
    
    data_json = file_util.get_sorted_json_content(source_root_folders, current_index)
    data = {}
    
    # 提取源文件的问题和回答
    try:
        extracted_values = data_parse.extract_values(data_json, 'value')
        for i, value in enumerate(extracted_values):
            if i == 0:
                data['questionValue'] = value
            else:
                data['sourceValue'] = value
                data['answerValue'] = value
    except Exception as e:
        raise Exception(f'数据解析失败 {e}！')
    
    data['image'] = img_file.set_image_url(data_json['image'])
    
    # 提取文件名，不包含路径
    file_name_with_ext = data_json['image'].split('/')[-1]
    file_name = file_name_with_ext.rsplit('.', 1)[0]
    
    # 读取已保存的文件
    if file_util.file_exists_in_directory(save_root_folders, file_name + config.ANNOTATION_SUF):
        data['saveFlag'] = True
        with open(os.path.join(save_root_folders, file_name + config.ANNOTATION_SUF), 'r', encoding='utf-8') as file:
            data_json = json.load(file)
        
        # 提取已保存的数据
        try:
            extracted_values = data_parse.extract_values(data_json, 'value')
            for i, value in enumerate(extracted_values):
                if i == 1:
                    data['answerValue'] = value
        except Exception as e:
            raise Exception(f'数据解析失败 {e}！')
    else:
        data['saveFlag'] = False
    
    data['fileName'] = file_name
    response_data['currentIndex'] = current_index
    response_data['data'] = data
    
    return response_data


# 合并标注数据
def merge_data(datasetName: str):
    """
    合并标注数据到指定目录，并更新操作记录。
    """
    response_data = {
        'code': 200,
        'message': '合并成功！'
    }
    
    source_folder = os.path.join(config.QA_ANNOTATION_MODIFICATION_FILE_PATH, datasetName)
    if not os.path.exists(source_folder):
        response_data['code'] = 500
        response_data['message'] = '合并失败，同步数据集不存在！'
        return response_data
    
    merge_folder = os.path.join(config.QA_MERGE_FILE_PATH, datasetName)
    if not os.path.exists(merge_folder):
        os.makedirs(merge_folder)
    
    file_util.copy_files(source_folder=source_folder, destination_folder=merge_folder)
    
    # 保存操作记录
    load_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    query_data = operator_record.query_entry(load_data, str(datasetName), anno_type.get_attribute('anno'))
    
    if query_data is None:
        response_data['code'] = 500
        response_data['message'] = '合并失败，请先标注！'
        return response_data
    else:
        operator_record.update_entry(load_data, datasetName, anno_type.get_attribute('anno'), isMerge=True)
    
    operator_record.save_json(config.OPERATION_RECORD_PATH, load_data)
    
    return response_data


# 页面数据保存
def save_anno_data(data_json):
    """
    保存标注数据，并更新操作记录。
    """
    source_root_folders = os.path.join(config.QA_ANNOTATION_SAVE_PATH, str(data_json['datasetName']), config.ERROR_FILE)
    save_folders = os.path.join(config.QA_ANNOTATION_MODIFICATION_FILE_PATH, str(data_json['datasetName']))
    
    file_path = f"{data_json['fileName']}{config.ANNOTATION_SUF}"

    exists_flag = False
    
    # 通过文件名称查找对应的文件（校验）
    if not file_util.file_exists_in_directory(source_root_folders, data_json['fileName'] + config.ANNOTATION_SUF):
        raise Exception('文件不存在！')
    
    # 写入到文件夹中，同时存在错误文件内容的修改
    with open(os.path.join(source_root_folders, data_json['fileName'] + config.ANNOTATION_SUF), 'r', encoding='utf-8') as file:
        content = json.load(file)
    
    # 修改第二个 conversation 中的 value
    if "conversations" in content and len(content["conversations"]) > 1:
        content["conversations"][1]["value"] = data_json['answerValue']
        
    # 将修改后的数据保存回文件
    if not os.path.exists(save_folders):
        os.makedirs(save_folders)
    
    for path in [save_folders]:
        if file_util.file_exists_in_directory(path, file_path):
            exists_flag = True
            os.remove(os.path.join(path, file_path))

    with open(os.path.join(save_folders, data_json['fileName'] + config.ANNOTATION_SUF), 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)
    
    count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    saveCount = file_util.count_json_files(save_folders, config.ANNOTATION_SUF)
    
    # 保存操作记录
    load_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    query_data = operator_record.query_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('anno'))
    date_data = {}
    if not query_data:
        date_data[today_str] = 1
        operator_record.add_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('anno'), 
                                  preview=data_json['fileName'] + config.ANNOTATION_SUF, count=count, saveCount=saveCount, isMerge=False, date=date_data)
    else:
        date_data = query_data.get('date', {})
        if exists_flag is False:
            date_data[today_str] = date_data.get(today_str, 0) + 1
    operator_record.update_entry(load_data, str(data_json['datasetName']), 
                                anno_type.get_attribute('anno'), 
                                preview=data_json['fileName'] + config.ANNOTATION_SUF, 
                                count=count, saveCount=saveCount, isMerge=False, date=date_data)
    operator_record.save_json(config.OPERATION_RECORD_PATH, load_data)
