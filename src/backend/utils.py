import os
import imageio
from skimage import img_as_ubyte


def generateGIF(fps, spath, tpath):
    frames = []
    file_list = [x for x in os.listdir(spath) if x.endswith('png')]
    file_list.sort(key=lambda x: int(x.split('.')[0][5:]))
    for point_img in file_list:
        frames.append(imageio.imread(os.path.join(spath, point_img)))
    imageio.mimsave(tpath, [img_as_ubyte(frame) for frame in frames], fps=fps)