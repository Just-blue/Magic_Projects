import contextlib
import os
import re
import subprocess
import wave
from log.log import logger


def acquire_time(wav_path):
    """
    获取音频时长
    :param wav_path: 音频路径
    :return: 音频时长
    """
    # if re.match('.*?sox.*', os.getenv('PATH')):                     # 判断环境变量里是否有sox
    cmd = 'sox --i -D %s' % wav_path
    logger.debug('[cmd]%s' % cmd)
    p = subprocess.Popen(cmd,  # 使用sox计算音频时长
                         stdout=subprocess.PIPE, shell=True,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out = p.stdout.read().decode()
    err = p.stderr.read().decode()

    if out and re.match('[0-9.]+', out) and not err:  # 判断sox是否成功
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
        pass
        # raise CustomError('[%s] 未能获取音频时长，请检查音频格式') from None
    return None


def creat_mapping(file, root):
    """
    创建音频地址映射关系map表
    """
    file_path = os.path.join(root, file)

    time = acquire_time(file_path)

    return {file.rstrip('.wav'): time}
