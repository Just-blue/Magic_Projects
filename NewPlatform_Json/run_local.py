import sys

from core.make_file import CreatPTFile

# ------------- 项目配置 ---------------- #
config_path = 'config.ini'
wav_path= r'I:\child-English-2018-12-3\data\child_check_1217_16000'
# ------------ 不定义 默认分包------------ #
classfy = 100

item = CreatPTFile(config_path, wav_path)

if 'classfy' in locals():
    package_num = classfy
    item.run(package_num)
else:
    item.run()
