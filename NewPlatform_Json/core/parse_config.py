import linecache
import re
from log.log import logger

class CustomError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo

    def __str__(self):
        return self.errorinfo

class Parse(object):
    def __init__(self,file_path):
        self.lines,self.output_list = [],[]
        file_type = self.file_type(file_path)
        self.file_prepare(file_path,file_type)                       # 检测输入文件类型

    def file_type(self,file_path):                                   # 判断输入的文件源
        theline = linecache.getline(file_path,1)                     # 第一个参数指读取的文件，第二个参数指文件的行数
        if theline:
            if theline[:11] == 'BASE_ENERGY':
                logger.info('输入文件识别为adapt_config文本')
                return 'adapt'
            else:
                logger.info('输入文件识别为通用文本')
                return 'normal'

    def file_prepare(self,file_path,file_type):
        if file_type == 'adapt':                                      # 判断输入文本类型
            index = 29
        elif file_type == 'normal':
            index = 0
        else:
            logger.error('未识别输入文本格式')
            raise CustomError('未识别输入文本格式')
        try:
            with open(file_path,'r',encoding='utf-8') as f:
                lines = f.readlines()
        except PermissionError:
            logger.error('请输入正确文件路径')
        except FileNotFoundError:
            logger.error('未找到该文件，请检查文件路径')
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gb2312') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                logger.error('文本未能解析，请将其转为utf-8')
            else:
                self.lines = lines[index:]
        else:
            self.lines = lines[index:]

    def get_info(self):
        for line in self.lines:
            if not re.match('Section.*',line):                              # 筛选过滤spker标题
                wav_name,text = line.rstrip('\n').split('\t')               # 获取文件名，文本内容
                try:
                    SPK,*_,suf = re.split('[^a-zA-Z0-9]+',wav_name)         # 获取SPK
                except ValueError:
                    message = '文件名不符合格式，未能解析出SPK'           # 文件名中没有下划线等符号     eg：SPK00010002
                    logger.critical(message)
                    raise CustomError(message) from None
                else:
                    if suf == 'wav':                                        # 文本格式为 SPK001_00123.wav 去掉 .wav
                        wav_name = re.sub('.wav','',wav_name)
                    yield SPK,wav_name,text

if __name__ == '__main__':
    item = Parse('../config.ini')
    item.get_info()