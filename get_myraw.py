import os.path
import skgeom as sg
import tqdm
import pickle
from example_canonical_transform import *
from geo_utils import inverse_warp_bldg_by_midaxis

raw_dir = r'dataset/raw_geo'
processed_dir = r'dataset/processed'


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


if __name__ == '__main__':
    min_all = 100000
    max_all = -1
    the_diff = 0
    with open('res.pkl', 'rb') as f:
        res = pickle.load(f)
    the_num = len(res)
    index = 0
    for file_ in tqdm.tqdm(os.listdir(raw_dir)):
        index = index + 1
        if (index < the_num + 1):
            continue
        try:
            raw_file = os.path.join(raw_dir, file_)
            prcoessed_file = os.path.join(processed_dir, file_ + '.gpickle', )
            with open(raw_file, 'rb') as f, open(prcoessed_file, 'rb') as f2:
                data = pickle.load(f)
                G_pro = nx.read_gpickle(f2)

                G_node = [G_pro.nodes[i] for i in G_pro.nodes if G_pro.nodes[i]['exist'] == 1]
                norm_blk_poly, norm_bldg_poly = move_to_origin_efficient(data[0], data[1])

                norm_blk_poly = norm_blk_poly.simplify(0.7)
                poly_list = list(norm_blk_poly.exterior.coords)[:-1]
                poly_list.reverse()
                poly = sg.Polygon(poly_list)

                skel = sg.skeleton.create_interior_straight_skeleton(poly)
                G, longest_skel = get_polyskeleton_longest_path(skel, poly)
                medaxis = modified_skel_to_medaxis(longest_skel, norm_blk_poly)
                # 坐标变换
                pos_xsorted, size_xsorted, xsort_idx, aspect_rto = warp_bldg_by_midaxis(
                    norm_bldg_poly, norm_blk_poly, medaxis
                )
                res.append({"pos": pos_xsorted, "size": size_xsorted, "midaxis": medaxis, "aspect_rto": aspect_rto,
                            "x_ids": xsort_idx})
                if (index % 100 == 0):
                    # 保存res为pickle
                    with open('res.pkl', 'wb') as f:
                        pickle.dump(res, f)
                        print('res saved', index)

        except NotImplementedError:
            print(f"An error occurred with file {file_}. Skipping this file.")
            continue

    with open('res.pkl', 'wb') as f:
        pickle.dump(res, f)
        print('res saved', index)
    data_norn(res)
