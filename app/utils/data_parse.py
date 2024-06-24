
def extract_values(data, key):
    values = []
    
    def _extract_values(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    values.append(v)
                elif isinstance(v, (dict, list)):
                    _extract_values(v)
        elif isinstance(obj, list):
            for item in obj:
                _extract_values(item)
    
    _extract_values(data)
    return values

