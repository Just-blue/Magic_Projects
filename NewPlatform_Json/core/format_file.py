import glob
import os

from log.log import logger


class Format_File():
    def __init__(self, ost):
        """
        输入文件或路径 解析成标注平台所需内容
        :param ost: list >> config路径,index行数
                    path >> 采集工具生成的文本路径
        """
        res = self.init_format(ost)
        self.lines = res

    def init_format(self, ost):
        if ost is list:
            file_path, index = ost
            res = self.parse_config(file_path, index)
        else:
            res = self.combine_config(ost)

        return res

    @staticmethod
    def combine_config(project_txts_path):
        lines = []
        for file in glob.glob1(project_txts_path, '*.txt'):
            file_path = os.path.join(project_txts_path, file)
            logger.info('解析%s文件完毕' % file)
            with open(file_path, 'r', encoding='utf-8') as fr:
                for line in fr.readlines()[2:]:
                    wav_name, *_, txt = line.split('\t')
                    lines.append(wav_name + '\t' + txt)
        return lines

    @staticmethod
    def parse_config(file_path, index):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        return lines[index:]
