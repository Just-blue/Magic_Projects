import sys

from core.make_file import CreatPTFile

config_path, wav_path,*classfy = sys.argv[1:]

item = CreatPTFile(config_path, wav_path)
# config_path,wav_path= ['config.ini','F:\[Cmx]\out']
if len(classfy) >= 1:
    package_num = int(classfy[0])
    item.run(package_num)
else:
    item.run()

