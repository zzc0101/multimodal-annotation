import cv2
from config import config

# 设置图片大小
def resize_image(image_path: str, target_width: int, target_height: int) -> bytes:
    # 读取图像
    image = cv2.imread(image_path)
    
    # 调整图像大小到1080p
    resized_image = cv2.resize(image, (target_width, target_height))
    
    # 将图像转换为字节流
    _, img_encoded = cv2.imencode('.jpg', resized_image)
    return img_encoded.tobytes()


# 设置图片请求路径
def set_image_url(image_name: str):
    return "http://" + config.Server_Host + ":" + str(config.Server_Port) + "/image/" + image_name