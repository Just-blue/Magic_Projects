import os
from multiprocessing import Manager, Pool

from core.make_file import CreatPTFile

# ------------- 项目配置 ---------------- #
from core.maping_wavs import creat_mapping

project_root_path = '/newdisk1_8T/haozhiqing/Ali_kx/Pretreatment'
project_path = '/newdisk1_8T/haozhiqing/Ali_kx/Pretreatment/GN0001D190118S002BP3'
project_txts_path = r'/newdisk1_8T/haozhiqing/Ali_kx/Pretreatment/origin_wavs'
project_name = os.path.basename(project_path)
save_upl_path = os.path.join(project_root_path, project_name + '.txt')

# --------------- 分包数--------------- #
classfy = 100

if __name__ == '__main__':

    result = []
    dic_map = {}
    pool = Pool(processes=20)

    for root, dirs, files in os.walk(project_path):
        for file in files:
            wav_name, suf = os.path.splitext(file)

            if suf != '.wav':
                continue

            result.append(pool.apply_async(creat_mapping, args=(file, root)))  # 维持执行的进程总数为10，当一个进程执行完后启动一个新进程.

    pool.close()
    pool.join()

    for i in result:
        dic_map.update(i.get())

    item = CreatPTFile(project_txts_path, dic_map, save_upl_path)

    item.run(classfy)
