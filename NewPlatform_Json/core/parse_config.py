import linecache
import re

from core.format_file import Format_File
from log.log import logger


class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)  # 初始化父类
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


class Parse(Format_File):
    """
    解析文本
    """

    def __init__(self, ost):
        super(Parse, self).__init__(ost)

    def get_info(self):
        for line in self.lines:
            wav_name, text = line.rstrip('\n').split('\t')  # 获取文件名，文本内容
            try:
                SPK, *_, suf = re.split('[^a-zA-Z0-9]+', wav_name)  # 获取SPK
            except ValueError:
                message = '文件名不符合格式，未能解析出SPK'  # 文件名中没有下划线等符号     eg：SPK00010002
                logger.critical(message)
                raise CustomError(message) from None
            else:
                if suf in wav_name:  # 文本格式为 SPK001_00123 加 .wav
                    wav_name = re.sub('.wav', '', wav_name)
                yield SPK, wav_name, text
