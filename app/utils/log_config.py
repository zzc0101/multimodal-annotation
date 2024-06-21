import logging
from logging.config import dictConfig

# 日志配置字典
log_config = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': './logs/logfile.log',
            'maxBytes': 1024 * 1024 * 5,
            'mode': 'a',
            'backupCount': 10,
            'encoding': 'utf8'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO'
    }
}

# 获取日志记录器
def get_logger():
    # 应用日志配置
    dictConfig(log_config)
    return logging.getLogger()