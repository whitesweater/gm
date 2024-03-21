import os.path

import numpy as np
import skgeom as sg
import tqdm
import pickle
from example_canonical_transform import *
from geo_utils import inverse_warp_bldg_by_midaxis


def data_norn(data):
    pos = [i["pos"] for i in data]
    size = [i["size"] for i in data]
    # 计算所有坐标点的整体均值和标准差
    all_points = np.concatenate(pos, axis=0)  # 将所有坐标点合并到一个大的 ndarray 中
    mean = np.mean(all_points, axis=0)  # 计算均值
    std = np.std(all_points, axis=0)  # 计算标准差
    print(mean, std)

    all_points = np.concatenate(size, axis=0)  # 将所有坐标点合并到一个大的 ndarray 中
    mean = np.mean(all_points, axis=0)  # 计算均值
    std = np.std(all_points, axis=0)  # 计算标准差
    print(mean, std)

    all_points = all_points - mean
    print(np.mean(all_points, axis=0))
    all_points = all_points / std
    print(np.std(all_points, axis=0))
    print(all_points[:3, ])


if __name__ == "__main__":
    file_path = r'res.pkl'
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
        data_norn(data)
