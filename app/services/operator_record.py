import json
import os

def load_json(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)  # 创建一个空的 JSON 数组
        return []
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def query_entry(json_data, dataset, entry_type):
    for entry in json_data:
        if entry['dataset'] == dataset and entry['type'] == entry_type:
            return entry
    return None

def update_entry(json_data, dataset, entry_type, **kwargs):
    entry = query_entry(json_data, dataset, entry_type)
    if entry:
        for key, value in kwargs.items():
            if key in entry:
                entry[key] = value
    return entry

def add_entry(json_data, dataset, entry_type, preview, **kwargs):
    if query_entry(json_data, dataset, entry_type) is None:
        new_entry = {
            "dataset": dataset,
            "type": entry_type,
            "preview": preview
        }
        new_entry.update(kwargs)
        json_data.append(new_entry)
        return new_entry
    else:
        return None