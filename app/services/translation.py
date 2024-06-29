from app.utils import file_util, img_file, data_parse, anno_type
from config import config
import os, json, shutil
from app.services import operator_record


# 计算出问答筛选的所有文件
def query_data():
    list = []
    # 待翻译中文路径，暂时为：./test/source/translate/Chinese
    root_folders = os.path.join(config.TRANSLATE_ANNOTATION_FILE_PATH, config.CHINESE_FOLDER)
    # 翻译标注后中文文件保存的路径，暂时为：./test/result/translate/Chinese
    result_folders = os.path.join(config.TRANSLATE_ANNOTATION_SAVE_PATH, config.CHINESE_FOLDER)
    # 获取倒排的中文路径的文件夹名称
    folders = file_util.get_all_folders(root_folders)
    for name in folders:
        # 保存路径（防止未创建而读取失败）
        save_path = os.path.join(result_folders, name)
        os.makedirs(save_path, exist_ok=True)

        # 封装返回数据
        data = {}
        data['name'] = name
        data['count'] = file_util.count_json_files(os.path.join(root_folders, name), config.ANNOTATION_SUF)
        data['saveCount'] = file_util.count_json_files(save_path, config.ANNOTATION_SUF)
        list.append(data)
    return list


# 根据文件名称查询当前文件的对应下标
def get_current_index(dataset: str, file_name: str):
    source_root_folders = os.path.join(config.TRANSLATE_ANNOTATION_FILE_PATH, config.CHINESE_FOLDER, dataset)
    return file_util.get_file_index(source_root_folders, file_name)


# 同步标注数据
# def sync_data(datasetName: str):
#     source_error_folder = config.TRANSLATE_ANNOTATION_SAVE_PATH + '/' + datasetName + '/' + config.ERROR_FILE
#     if not os.path.exists(source_error_folder):
#         return False
#     source_correct_folder = config.TRANSLATE_ANNOTATION_SAVE_PATH + '/' + datasetName + '/' + config.CORRECT_FILE
#     if not os.path.exists(source_correct_folder):
#         return False
#     target_merge = config.QA_MERGE_FILE_PATH + '/' + datasetName
#     target_anno = config.QA_ANNOTATION_ERROR_FILE_PATH + '/' + datasetName
#     file_util.copy_files(source_folder=source_correct_folder, destination_folder=target_merge)
#     file_util.copy_files(source_folder=source_error_folder, destination_folder=target_anno)
#     return True


# 页面数据响应
def get_anno_data(dataset: str, current_index: int):
    response_data = {}
    # 中英文的源文件夹和保存文件夹
    source_root_folders = os.path.join(config.TRANSLATE_ANNOTATION_FILE_PATH, config.CHINESE_FOLDER, dataset)
    source_root_folders_en = os.path.join(config.TRANSLATE_ANNOTATION_FILE_PATH, config.ENGLISH_FOLDER, dataset)
    save_root_folders = os.path.join(config.TRANSLATE_ANNOTATION_SAVE_PATH, config.CHINESE_FOLDER, dataset)
    save_root_folders_en = os.path.join(config.TRANSLATE_ANNOTATION_SAVE_PATH, config.ENGLISH_FOLDER, dataset)

    # 总数（以中文为准）
    data_count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    response_data['total'] = data_count

    # 校验index
    if current_index < 0 and current_index >= data_count:
        raise BaseException('数据获取异常！')

    # 中英文的json信息
    data_json = file_util.get_sorted_json_content(source_root_folders, current_index)
    data_json_en = file_util.get_sorted_json_content(source_root_folders_en, current_index)

    # 返回结果
    data = {}
    data['image'] = img_file.set_image_url(data_json['image'])
    data_json['image'].startswith('/')
    # 提取文件名，不包含路径
    file_name_with_ext = data_json['image'].split('/')[-1]
    # 分离文件名和扩展名
    file_name = file_name_with_ext.rsplit('.', 1)[0]
    if file_util.file_exists_in_directory(save_root_folders, file_name + config.ANNOTATION_SUF) \
            and file_util.file_exists_in_directory(save_root_folders_en, file_name + config.ANNOTATION_SUF):

        data['saveFlag'] = True
        with open(os.path.join(save_root_folders, file_name + config.ANNOTATION_SUF), 'r', encoding='utf-8') as file:
            data_json = json.load(file)
        with open(os.path.join(save_root_folders_en, file_name + config.ANNOTATION_SUF), 'r', encoding='utf-8') as file:
            data_json_en = json.load(file)
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

        extracted_values_en = data_parse.extract_values(data_json_en, 'value')
        for i, value in enumerate(extracted_values_en):
            if i == 0:
                data['questionValueEn'] = value
            else:
                data['answerValueEn'] = value
    except Exception as e:
        raise BaseException(f'数据解析失败 {e}！')
    response_data['currentIndex'] = current_index
    response_data['data'] = data
    return response_data


# 页面数据保存
def save_anno_data(data_json):
    # 中英文根目录
    source_root_folders = os.path.join(config.TRANSLATE_ANNOTATION_FILE_PATH, config.CHINESE_FOLDER, str(data_json['datasetName']))
    source_root_folders_en = os.path.join(config.TRANSLATE_ANNOTATION_FILE_PATH, config.ENGLISH_FOLDER,
                                       str(data_json['datasetName']))
    # 中英文保存目录
    root_folders = os.path.join(config.TRANSLATE_ANNOTATION_SAVE_PATH, config.CHINESE_FOLDER, str(data_json['datasetName']))
    root_folders_en = os.path.join(config.TRANSLATE_ANNOTATION_SAVE_PATH, config.ENGLISH_FOLDER,
                                str(data_json['datasetName']))
    os.makedirs(root_folders, exist_ok=True)
    os.makedirs(root_folders_en, exist_ok=True)

    # 取出源文件的中英文内容
    with open(os.path.join(source_root_folders, data_json['fileName'] + config.ANNOTATION_SUF), 'r',
              encoding='utf-8') as file:
        content = json.load(file)
    with open(os.path.join(source_root_folders_en, data_json['fileName'] + config.ANNOTATION_SUF), 'r',
              encoding='utf-8') as file:
        content_en = json.load(file)

    # 修改中英文第二个 conversation 中的 value
    if "conversations" in content and len(content["conversations"]) > 1:
        content["conversations"][1]["value"] = data_json['answerValue']
    if "conversations" in content_en and len(content["conversations"]) > 1:
        content_en["conversations"][1]["value"] = data_json['answerValueEn']

    # 将修改后的数据保存回文件
    with open(os.path.join(root_folders, data_json['fileName'] + config.ANNOTATION_SUF), 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)
    with open(os.path.join(root_folders_en, data_json['fileName'] + config.ANNOTATION_SUF), 'w',
              encoding='utf-8') as file:
        json.dump(content_en, file, ensure_ascii=False, indent=4)

    # 总数
    count = file_util.count_json_files(source_root_folders, config.ANNOTATION_SUF)
    # correctCount = file_util.count_json_files(correct_path, config.ANNOTATION_SUF)
    # 完成数
    saveCount = file_util.count_json_files(root_folders, config.ANNOTATION_SUF)
    # 保存操作记录
    load_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    if load_data is None:
        operator_record.add_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('translate'),
                                  preview=data_json['fileName'] + config.ANNOTATION_SUF, count=count,
                                  saveCount=saveCount)
    else:
        query_data = operator_record.query_entry(load_data, str(data_json['datasetName']),
                                                 anno_type.get_attribute('translate'))
        if query_data is None:
            operator_record.add_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('translate'),
                                      preview=data_json['fileName'] + config.ANNOTATION_SUF, count=count,
                                      saveCount=saveCount)
        else:
            operator_record.update_entry(load_data, str(data_json['datasetName']), anno_type.get_attribute('translate'),
                                      preview=data_json['fileName'] + config.ANNOTATION_SUF, count=count,
                                      saveCount=saveCount)
    operator_record.save_json(config.OPERATION_RECORD_PATH, load_data)
