import os.path

import networkx as nx
import numpy as np
import skgeom as sg
import tqdm
from skgeom.draw import draw
import pickle
import matplotlib.pyplot as plt
from example_canonical_transform import *
from geo_utils import inverse_warp_bldg_by_midaxis
from graph_util import visual_block_graph
from matplotlib.patches import Rectangle


def draw_skeleton(polygon, skeleton, show_time=False):
    draw(polygon)
    # plt.show()

    for h in skeleton.halfedges:
        if h.is_bisector:
            p1 = h.vertex.point
            p2 = h.opposite.vertex.point
            plt.plot([p1.x(), p2.x()], [p1.y(), p2.y()], 'r-', lw=2)

    if show_time:
        for v in skeleton.vertices:
            plt.gcf().gca().add_artist(plt.Circle(
                (v.point.x(), v.point.y()),
                v.time, color='blue', fill=False))
    plt.show()


def draw_longest(line):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x, y = line.xy
    ax.plot(x, y, color='#6699cc', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)

    # 显示图形
    plt.show()


raw_dir = r'dataset/raw_geo'
processed_dir = r'dataset/processed'
count_sim = 0
count_diff = 0


def num_diff(raw_data_dir, processed_data_dir):
    for raw_data_name in os.listdir(raw_data_dir):
        with open(os.path.join(raw_data_dir, raw_data_name), 'rb') as f:
            raw_data = pickle.load(f)
            for processed_data_name in os.listdir(processed_data_dir):
                with open(os.path.join(processed_data_dir, processed_data_name), 'rb') as f2:
                    processed_data = nx.read_gpickle(f2)
                    if raw_data[0] == processed_data.graph['blk_poly'] and raw_data[1] == processed_data.graph[
                        'bldg_poly']:
                        global count_sim
                        count_sim += 1
                        break


def draw_pro_data(pos_xsorted, size_xsorted, file_name):
    plt.scatter(pos_xsorted[:, 0], pos_xsorted[:, 1], c='red', s=50)
    ax = plt.gca()
    for i in range(size_xsorted.shape[0]):
        ax.add_patch(Rectangle(
            (pos_xsorted[i, 0] - size_xsorted[i, 0] / 2.0, pos_xsorted[i, 1] - size_xsorted[i, 1] / 2.0),
            size_xsorted[i, 0], size_xsorted[i, 1], linewidth=2, edgecolor='r', facecolor='b', alpha=0.3))
    plt.savefig(file_name + '.png')
    plt.clf()


if __name__ == '__main__':

    # num_diff(raw_dir, processed_dir)
    # 1002  只有一个建筑 好好参考
    for file_ in tqdm.tqdm(os.listdir(raw_dir)):
        raw_file = os.path.join(raw_dir, file_)
        prcoessed_file = os.path.join(r'dataset/processed', file_ + '.gpickle', )

        with open(raw_file, 'rb') as f, open(prcoessed_file, 'rb') as f2:
            data = pickle.load(f)
            G_pro = nx.read_gpickle(f2)
            # 过滤掉不存在的节点
            G_node = [G_pro.nodes[i] for i in G_pro.nodes if G_pro.nodes[i]['exist'] == 1]
            # 移动到中间
            norm_blk_poly, norm_bldg_poly = move_to_origin_efficient(data[0], data[1])

            # 计算主轴
            norm_blk_poly = norm_blk_poly.simplify(0.7)
            poly_list = list(norm_blk_poly.exterior.coords)[:-1]
            poly_list.reverse()  # 逆时针
            poly = sg.Polygon(poly_list)
            skel = sg.skeleton.create_interior_straight_skeleton(poly)
            G, longest_skel = get_polyskeleton_longest_path(skel, poly)
            medaxis = modified_skel_to_medaxis(longest_skel, norm_blk_poly)

            # 坐标变换， 获得我的理论位置
            pos_xsorted, size_xsorted, xsort_idx, aspect_rto = warp_bldg_by_midaxis(
                norm_bldg_poly, norm_blk_poly, medaxis
            )

            # 实际位置
            pos_all = np.array([[i['posx'], i['posy']] for i in G_node])
            size_all = np.array([[i['size_x'], i['size_y']] for i in G_node])

            res_G = inverse_warp_bldg_by_midaxis(pos_sorted=pos_all,
                                                 size_sorted=size_all,
                                                 midaxis=medaxis,
                                                 aspect_rto=G_pro.graph['aspect_ratio'])

            plt.title("origin data")
            for i in norm_bldg_poly:
                draw(sg.Polygon(i.exterior.coords[:-1]))
            plt.show()

            plt.title("inverse data")
            for i in res_G[0]:
                draw(sg.Polygon(i.exterior.coords[:-1]))
            plt.show()

            print("\n我计算出来的转换后坐标")
            print(pos_xsorted, '\n size \n', size_xsorted)
            # print('mean and std position:\n', np.mean(pos_xsorted), np.std(pos_xsorted),
            #       '\nmean and std size:\n', np.mean(size_xsorted), np.std(size_xsorted))
            print("\n从结果中读取的转换后坐标")
            print(pos_all, '\n size \n', size_all)
            # print(np.mean(pos_all), np.std(pos_all), np.mean(size_all), np.std(size_all))
            print("\n结果转换为正常坐标系")
            print(res_G[1])
            print(res_G[2])
            print("nmn")
