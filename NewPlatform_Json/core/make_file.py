import contextlib
import glob
import json
import os
from functools import reduce

from core.parse_config import Parse, CustomError
from log.log import logger


class CreatPTFile(Parse):
    def __init__(self, ost, wavs_map, _save_path):
        """
        :param config_path: config文件路径
        :param wav_path: 对应音频文件路径
        """
        super(CreatPTFile, self).__init__(ost)
        self.wav_time_map = wavs_map  # 创建音频地址映射关系
        self._save_path = _save_path

    @staticmethod
    def mkdir(path):
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def run(self, custom_classfy):
        """
        遍历config文件和音频路径，将其新平台文本格式信息写到output/result.txt文件中
        :param custom_classfy: 自定义分包条数，默认按spk音频数分包
        """
        logger.debug('遍历wav_name,text信息')
        wav_suf = 'wav'
        counter = 0
        wavs_info_map = {}

        for SPK, wav_name, content in self.get_info():  # 遍历说话人id，音频名，音频内容 信息
            logger.debug('[wav_info] %s - %s - %s ' % (SPK, wav_name, content))

            if wav_name not in self.wav_time_map:
                logger.warning('[%s] 未找到音频' % wav_name)
                continue

            wav_time = self.wav_time_map.get(wav_name)
            if not wav_time:
                continue

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

            if custom_classfy:  # 指定分包数的模式
                id = f'line_{counter}'
                if id not in wavs_info_map:
                    wavs_info_map[id] = [wav_info]

                else:
                    if len(wavs_info_map[id]) == custom_classfy - 1:
                        counter += 1

                    wavs_info_map[id].append(wav_info)

            else:  # 默认分包模式
                if SPK not in wavs_info_map:
                    wavs_info_map[SPK] = [wav_info]
                else:
                    wavs_info_map[SPK].append(wav_info)

        logger.info(
            '处理完毕！ 共 %s 批次 [%s]' % (len(wavs_info_map.keys()), wavs_info_map.keys()) if not custom_classfy else (
                counter, len(reduce(lambda x, y: x + y, wavs_info_map.values()))))

        with open(self._save_path, 'w', encoding='utf-8') as f:
            for key, value in wavs_info_map.items():
                f.write(json.dumps(value, ensure_ascii=False) + '\n')
