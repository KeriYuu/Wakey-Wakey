from collections import defaultdict
import numpy as np

def getTransCdrs(epsilon, coordinate, keypoints):
    # ifdriving = True
    
    nFrames = len(keypoints)
    new_coordinates = [list(map(float, coordinate))]
    dleft, dtop, dright, dbottom = 0, 0, 0, 0
    sleft, stop, sright, sbottom = 0, 0, 0, 0
    # V, alignV = 0, 0
    V = keypoints[0] # 相对于第一帧
    curcoordinate = new_coordinates[0]
    x_list, y_list = curcoordinate[::2], curcoordinate[1::2]
    dleft, dtop = np.min(V, axis=0)
    dright, dbottom = np.max(V, axis=0)
    sleft, stop = min(x_list), min(y_list)
    sright, sbottom = max(x_list), max(y_list)
    # 位置对齐
    dwidth, dheight = dright - dleft, dbottom - dtop
    swidth, sheight = sright - sleft, sbottom - stop
    alignV = (V-np.array([dleft, dtop])) * np.array([swidth / dwidth, sheight / dheight])
    print(dwidth, dheight, swidth, sheight)
    print(dleft, dtop, sleft, stop)
    print(V)
    print(alignV)

    for f in range(1, nFrames):

        e = epsilon  # 将 e 设置为2
        res = []
        # 对每一个像素点（对局部坐标点，d=0，会出现 inf/inf=nan，故要另外更新键值）
        # curcoordinate = new_coordinates[-1]
        # curcoordinate = new_coordinates[0]
        # x_list, y_list = curcoordinate[::2], curcoordinate[1::2]

        # V = keypoints[0] # 相对于第一帧

        # if f==1 and not ifdriving:
        #     alignV = V

        # if f == 1 and ifdriving:
        #     dleft, dtop = np.min(V, axis=0)
        #     dright, dbottom = np.max(V, axis=0)
        #     sleft, stop = min(x_list), min(y_list)
        #     sright, sbottom = max(x_list), max(y_list)
        #     # 位置对齐
        #     dwidth, dheight = dright - dleft, dbottom - dtop
        #     swidth, sheight = sright - sleft, sbottom - stop
        #     alignV = (V-np.array([dleft, dtop])) * scale * np.array([swidth / dwidth, sheight / dheight])
        # V = keypoints[f-1]

        U = keypoints[f]

        # 每个局部坐标点对应的仿射变换，这里对每个点都采用平移
        G = defaultdict(lambda: np.eye(3))  # 创建包含所有仿射变换的字典，并初始化平移矩阵
        for i in range(len(U)):
            G[i][2, :2] = U[i] - V[i]

        for k in range(len(x_list)):
        # for i in range(1):
            cur = np.zeros(3)
            x, y = x_list[k] - sleft, y_list[k] - stop
            # nx, ny = round(scale * x + left), round(-scale * y + top)
            D = np.sqrt(((np.array([x, y]) - alignV) ** 2).sum(axis=1)) + 1e-8  # 该像素点到每一个局部坐标的距离
            W = 1 / (D ** e)    # 每个局部坐标的仿射变化对该像素点位置影响的权重
            W = W / W.sum()     # 归一化
            # 对每一个局部坐标点
            for i in range(len(V)):
                cur += W[i] * np.dot(np.array([x, y, 1]), G[i])    # 加权平均
            # res.append(round((cur[0] - left) / scale + sleft))     # 取出 x, y 坐标
            # res.append(round((cur[1] - top) / (-scale) + stop))
            res.append(cur[0] + sleft)     # 取出 x, y 坐标
            res.append(cur[1] + stop)
        new_coordinates.append(res)
    return new_coordinates