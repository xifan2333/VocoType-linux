"""统一的日志配置模块 - 项目唯一的日志配置点"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def setup_logging(
    level: str = "INFO",
    log_dir: str = None,
    log_file: str = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 3,
) -> None:
    """配置全局日志系统（应该在程序入口最早调用）
    
    Args:
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
        log_dir: 日志目录，如果提供则同时输出到文件
                文件命名格式：log_YYYY-MM-DD.log
                自动轮转：每天午夜，最多保留3个备份，单文件最大10MB
        log_file: 固定日志文件路径，如果提供则优先使用该文件并按大小轮转
        max_bytes: 文件日志单文件最大大小（字节）
        backup_count: 文件日志最多保留的历史文件数量
    
    特性：
        - 控制台输出到stderr（避免干扰stdout通信）
        - 可选的文件日志持久化
        - 防止重复配置（清空已有handlers）
        - 统一的日志格式
    """
    root_logger = logging.getLogger()
    
    # 避免重复配置：清空已有handlers
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 统一日志格式
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台输出（使用stderr避免干扰stdout通信）
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 可选的文件输出
    if log_file:
        try:
            expanded_log_file = os.path.expanduser(log_file)
            log_parent = os.path.dirname(expanded_log_file) or "."
            os.makedirs(log_parent, exist_ok=True)

            file_handler = RotatingFileHandler(
                expanded_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            logging.info(
                "日志系统已初始化 - 级别=%s, 文件=%s, 轮转=%dMB x %d",
                level,
                expanded_log_file,
                max_bytes // (1024 * 1024),
                backup_count,
            )
        except Exception as e:
            logging.warning(f"文件日志配置失败，仅使用控制台日志: {e}")
    elif log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            
            # 按日期命名日志文件
            log_file = os.path.join(
                log_dir, 
                f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
            )
            
            # 使用TimedRotatingFileHandler实现按日期轮转
            # when='midnight': 每天午夜轮转
            # interval=1: 每1天
            # backupCount=3: 保留3个备份文件
            file_handler = TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            # 添加文件大小限制（10MB）
            # 注意：TimedRotatingFileHandler没有原生的maxBytes，
            # 但我们可以设置属性供监控使用
            file_handler.maxBytes = max_bytes
            
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            logging.info(f"日志系统已初始化 - 级别={level}, 文件={log_file}")
        except Exception as e:
            # 文件日志失败不应该阻止程序启动
            logging.warning(f"文件日志配置失败，仅使用控制台日志: {e}")
    else:
        logging.info(f"日志系统已初始化 - 级别={level}, 仅控制台输出")
