import os.path

import matplotlib.pyplot as plt
import numpy as np
import skgeom as sg
import tqdm
import pickle
from example_canonical_transform import *
from geo_utils import inverse_warp_bldg_by_midaxis
from skgeom.draw import draw
from matplotlib.patches import Rectangle

raw_dir = r'dataset/raw_geo'
result_dir = r'test/test_GlobalMapperGATConv_Max_dim256/latest_reconstruct_osm_cities/result/graph'
save_dir = r'test/test_GlobalMapperGATConv_Max_dim256/latest_reconstruct_osm_cities/result/visual'
if __name__ == '__main__':
    min_all = 100000
    max_all = -1
    the_diff = 0
    res = []
    idx = 0
    for file_ in tqdm.tqdm(os.listdir(result_dir)):
        raw_file = os.path.join(raw_dir, file_[:-8])
        result_file = os.path.join(result_dir, file_)
        with open(raw_file, 'rb') as f, open(result_file, 'rb') as f2:
            data = pickle.load(f)
            G_pro = nx.read_gpickle(f2)
            G_node = [G_pro.nodes[i] for i in G_pro.nodes if G_pro.nodes[i]['exist'] == 1]
            if (len(G_node) == 0):
                continue
            # 提取骨架
            norm_blk_poly, norm_bldg_poly = move_to_origin_efficient(data[0], data[1])
            norm_blk_poly = norm_blk_poly.simplify(0.7)
            poly_list = list(norm_blk_poly.exterior.coords)[:-1]
            poly_list.reverse()
            poly = sg.Polygon(poly_list)
            skel = sg.skeleton.create_interior_straight_skeleton(poly)
            G, longest_skel = get_polyskeleton_longest_path(skel, poly)
            medaxis = modified_skel_to_medaxis(longest_skel, norm_blk_poly)

            # 读取结果
            # pos_all=[]
            # size_all=[]
            # for i in range(G_node.number_of_nodes()):
            #     pos_all.append([G_node.nodes[i]['posx'], G_node.nodes[i]['posy']])
            #     size_all.append([G_node.nodes[i]['size_x'], G_node.nodes[i]['size_y']])

            pos_all = np.array([[i['posx'], i['posy']] for i in G_node])
            size_all = np.array([[i['size_x'], i['size_y']] for i in G_node])
            pos_all = np.array(pos_all, dtype=np.double)
            size_all = np.array(size_all, dtype=np.double)
            idx = idx + 1
            # print(idx)
            # 还原结果坐标
            res_G = inverse_warp_bldg_by_midaxis(pos_sorted=pos_all,
                                                 size_sorted=size_all,
                                                 midaxis=medaxis,
                                                 aspect_rto=G_pro.graph['aspect_ratio'])
            # 对结果进行可视化
            for i in res_G[0]:
                draw(sg.Polygon(i.exterior.coords[:-1]))
            plt.savefig(os.path.join(save_dir, f'{file_[:-8]}_res_G.png'))

            plt.scatter(res_G[1][:, 0], res_G[1][:, 1], c='red', s=50)
            ax = plt.gca()
            for i in range(res_G[2].shape[0]):
                ax.add_patch(Rectangle((res_G[1][i, 0] - res_G[2][i, 0] / 2.0, res_G[1][i, 1] - res_G[2][i, 1] / 2.0),
                                       res_G[2][i, 0], res_G[2][i, 1],
                                       linewidth=2, edgecolor='r', facecolor='b', alpha=0.3))
            plt.savefig(os.path.join(
                r'test/test_GlobalMapperGATConv_Max_dim256/latest_reconstruct_osm_cities/result/trans_block',
                f'{file_[:-8]}_res_G.png'))
