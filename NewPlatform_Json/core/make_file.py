import contextlib
import json
import os
import re
import subprocess
import wave
from datetime import datetime
from core.parse_config import Parse, CustomError
from log.log import logger


class CreatPTFile(Parse):
    def __init__(self, config_path, wav_path):
        """
        :param config_path: config文件路径
        :param wav_path: 对应音频文件路径
        """
        super(CreatPTFile, self).__init__(config_path)
        self.wav_path = wav_path
        self.wav_map = {}
        self.creat_mapping()  # 创建音频地址映射关系

    def creat_mapping(self):
        """
        创建音频地址映射关系map表
        """
        for root, dirs, files in os.walk(self.wav_path):
            for file in files:
                wav_name, *_ = os.path.splitext(file)
                self.wav_map[wav_name] = os.path.join(root, file)

    @staticmethod
    def mkdir(path):
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @staticmethod
    def acquire_time(wav_path):
        """
        获取音频时长
        :param wav_path: 音频路径
        :return: 音频时长
        """
        if re.match('.*?sox.*', os.getenv('PATH')):                     # 判断环境变量里是否有sox
            cmd = 'sox --i -D %s' % wav_path
            logger.debug('[cmd]%s'%cmd)
            p = subprocess.Popen(cmd,                                   # 使用sox计算音频时长
                                 stdout=subprocess.PIPE, shell=True,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out = p.stdout.read().decode()
            err = p.stderr.read().decode()

            if out and re.match('[0-9.]+',out) and not err:             # 判断sox是否成功
                logger.debug('[out] %s' % out)
                wav_time = float(out)
                return wav_time
            else:
                logger.debug('[err] %s' % err)

        logger.warning('[%s] 文件未能通过sox统计时长 ' % wav_path)
        try:
            with contextlib.closing(wave.open(wav_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception:
            raise CustomError('[%s] 未能获取音频时长，请检查音频格式') from None

    def run(self, custom_classfy=0):
        """
        遍历config文件和音频路径，将其新平台文本格式信息写到output/result.txt文件中
        :param custom_classfy: 自定义分包条数，默认按spk音频数分包
        """
        logger.debug('遍历config文件wav_name,text信息')
        wav_suf = 'wav'
        counter = 0
        wavs_info_list, spk_list = [], []
        output_path = self.mkdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output'))\
                      + os.sep + 'result_%s.txt' % datetime.now().strftime('%H_%M')
        with open(output_path, 'w', encoding='utf-8') as f:
            for index,(SPK, wav_name, content) in enumerate(self.get_info()):      # 遍历说话人id，音频名，音频内容 信息
                logger.debug('[wav_info] %s - %s - %s '%(SPK,wav_name,content))
                if wav_name in self.wav_map:
                    wav_path = self.wav_map.get(wav_name)
                    wav_time = self.acquire_time(wav_path)
                    wav_info = [  # 填充新平台文本格式
                        {
                            "Wav_name": wav_name,
                            "Length_time": wav_time,
                            "Data": [
                                {
                                    "text": content,
                                    "start_time": 0,
                                    "end_time": wav_time
                                }
                            ],
                            "Wav_suf": wav_suf
                        }
                    ]

                    wavs_info_list.append(wav_info)                     # 将每条wav_info信息暂存于list中
                    counter += 1
                    if custom_classfy:                                  # 指定分包数的模式
                        if counter % custom_classfy == 0 :
                            logger.info('已处理包数 %s ' % counter)
                            f.write(json.dumps(wavs_info_list, ensure_ascii=False) + '\n')
                            wavs_info_list.clear()                      # 清除存放信息的list

                    else:                                               # 默认分包模式
                        if SPK not in spk_list :
                            if counter == 1:                            # 首次遍历赋予初值
                                spk_list.append(SPK)
                                continue

                            logger.info('已处理SPK批次 %s ' % (len(spk_list)))
                            f.write(json.dumps(wavs_info_list[:-1], ensure_ascii=False) + '\n')
                            wavs_info_list[:-1] = ''                     # 清除存放信息的list
                            spk_list.append(SPK)
                else:
                    logger.warning('[%s] 未找到音频'%wav_name)

            logger.info('处全部批次理完毕 %s'%len(spk_list) if custom_classfy else counter)
            f.write(json.dumps(wavs_info_list, ensure_ascii=False) )    # 写入最后一包信息
