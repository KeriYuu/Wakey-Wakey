
from pickle import TRUE
import matplotlib
from sklearn import neighbors
from sqlalchemy import true
matplotlib.use('Agg')
import os, sys
import yaml
from tqdm import tqdm

import imageio
import numpy as np
from skimage.transform import resize
from skimage import img_as_ubyte
import torch
from models.sync_batchnorm import DataParallelWithCallback

from models.modules.generator import OcclusionAwareGenerator
from models.modules.keypoint_detector import KPDetector
from models.animate import normalize_kp
from scipy.spatial import ConvexHull
import cv2


if sys.version_info[0] < 3:
    raise Exception("You must use Python 3 or higher. Recommended version is Python 3.7")

def load_checkpoints(config_path, checkpoint_path, cpu=False):

    with open(config_path) as f:
        config = yaml.load(f)

    generator = OcclusionAwareGenerator(**config['model_params']['generator_params'],
                                        **config['model_params']['common_params'])
    if not cpu:
        generator.cuda()

    kp_detector = KPDetector(**config['model_params']['kp_detector_params'],
                             **config['model_params']['common_params'])
    if not cpu:
        kp_detector.cuda()
    
    if cpu:
        checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
    else:
        checkpoint = torch.load(checkpoint_path)
 
    generator.load_state_dict(checkpoint['generator'])
    kp_detector.load_state_dict(checkpoint['kp_detector'])
    
    if not cpu:
        generator = DataParallelWithCallback(generator)
        kp_detector = DataParallelWithCallback(kp_detector)

    generator.eval()
    kp_detector.eval()
    
    return generator, kp_detector


def make_animation(source_image, driving_video, generator, kp_detector, relative=True, adapt_movement_scale=True, cpu=False, specified=False, skeypoints=None, dkeypoints=None):
    neighbor_frame = False
    with torch.no_grad():
        predictions = []
        source = torch.tensor(source_image[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2)

        if not cpu:
            source = source.cuda()
        driving = torch.tensor(np.array(driving_video)[np.newaxis].astype(np.float32)).permute(0, 4, 1, 2, 3)

        kp_source = kp_detector(source)
        kp_driving_initial = kp_detector(driving[:, :, 0])

        if specified:
            # kp_source['value'] = torch.tensor([skeypoints[0]])
            kp_driving_initial['value'] = torch.tensor([dkeypoints[0]])

        keypoints = []
        source_keypoints = []

        for frame_idx in tqdm(range(driving.shape[2])):
            driving_frame = driving[:, :, frame_idx]
            if not cpu:
                driving_frame = driving_frame.cuda()
            kp_driving = kp_detector(driving_frame, )
            if specified:
                kp_driving['value'] = torch.tensor([dkeypoints[frame_idx]])
            keypoints.append(kp_driving['value'].cpu().numpy()[0])
            kp_norm = normalize_kp(kp_source=kp_source, kp_driving=kp_driving,
                                   kp_driving_initial=kp_driving_initial, use_relative_movement=relative,
                                   use_relative_jacobian=relative, adapt_movement_scale=adapt_movement_scale)
            out = generator(source, kp_source=kp_source, kp_driving=kp_norm)

            predictions.append(np.transpose(out['prediction'].data.cpu().numpy(), [0, 2, 3, 1])[0])

            temp_source = out['prediction']
            temp_kp_source = kp_detector(temp_source)
            # if specified:
            #     temp_kp_source['value'] = torch.tensor([skeypoints[frame_idx]])
            source_keypoints.append(temp_kp_source['value'].cpu().numpy()[0])

            if neighbor_frame:
                kp_driving_initial = kp_driving
                # kp_source = temp_kp_source
                # source = temp_source

    return source_keypoints, predictions, keypoints
    

def generate(opt, specified=False, skeypoints=None, dkeypoints=None):
    # parser.add_argument("--config", default='config/vox-256.yaml', help="path to config")
    # parser.add_argument("--checkpoint", default='vox-cpk.pth.tar', help="path to checkpoint to restore")
    if specified:
        # skeypoints = (np.array(skeypoints).astype(np.float32) - 128) / 128
        dkeypoints = (np.array(dkeypoints).astype(np.float32) - 128) / 128

    source_image = imageio.imread(opt['source_image'])

    reader = imageio.get_reader(opt['driving_video'])
    # fps = opt['fps']
    driving_video = []
    try:
        for im in reader:
            driving_video.append(im)
    except RuntimeError:
        pass
    fps = max(1000 / (1e-8 + reader.get_meta_data()['duration']), 5)
    reader.close()
    print('SHAPPPPeee', driving_video[0].shape)
    source_image = resize(source_image, (256, 256))[..., :3]

    driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]
    print('SHAPPPPeee', (np.array(driving_video)).shape)
    generator, kp_detector = load_checkpoints(config_path=opt['config'], checkpoint_path=opt['checkpoint'], cpu=opt['cpu'])


    s_keypoints, predictions, keypoints = make_animation(source_image, driving_video, generator, kp_detector, relative=opt['relative'], adapt_movement_scale=opt['adapt_scale'], cpu=opt['cpu'], specified=specified, skeypoints=skeypoints, dkeypoints=dkeypoints)
    # colors = [(101, 67, 254), (154, 157, 252), (173, 205, 249), (169, 200, 200), (155, 175, 131), 
    #             (113, 227, 250), (192, 157, 137), (187, 200, 178), (46, 75, 82), (98, 72, 39)]
    colors = [(233, 208, 48), (111, 6, 126), (234, 94, 28), (124, 198, 224), (200, 0, 41), 
              (185, 187, 119), (119, 117, 118), (55, 64, 60), (218, 112, 167), (47, 99, 171),
              (232, 120, 86), (71, 17, 140), (233, 157, 37), (132, 9, 118), (221, 246, 70),
              (134, 0, 17), (126, 174, 48), (106, 45, 18), (230, 0, 28), (36, 51, 23)]

    driving_keypoints = []
    # np.save('driving_keypoints.npy', np.array(keypoints))
    driving_point = []
    for i in range(len(driving_video)):
        driving, keypoint = np.ascontiguousarray((driving_video[i] * 255).astype(np.uint8)), (keypoints[i] * 128 + 128).astype(int)
        driving_keypoints.append(keypoint)
        imageio.imsave(os.path.join('./userResults/driving_frames', 'frame' + str(i) + '.png'), driving)
        for j, (x, y) in enumerate(keypoint):
            cv2.circle(driving,(x, y), 5, colors[j],-1)
        driving_point.append(driving)
    np.save('./userResults/keypoints/driving_keypoints.npy', np.array(driving_keypoints))


    source_keypoints = []
    source_point = []
    # np.save('source_keypoints.npy', np.array(s_keypoints))
    for i, frame in enumerate(predictions):
        source, keypoint = np.ascontiguousarray((frame * 255).astype(np.uint8)), (s_keypoints[i] * 128 + 128).astype(int)
        source_keypoints.append(keypoint)
        imageio.imsave(os.path.join('./userResults/source_frames', 'frame' + str(i) + '.png'), source)
        for j, (x, y) in enumerate(keypoint):
            cv2.circle(source,(x, y), 5, colors[j],-1)
        source_point.append(source)
    np.save('./userResults/keypoints/source_keypoints.npy', np.array(source_keypoints))


    imageio.mimsave(opt['source_keypoint'], [img_as_ubyte(frame) for frame in source_point], fps=fps)
    imageio.mimsave(opt['driving_keypoint'], [img_as_ubyte(frame) for frame in driving_point], fps=fps)
    return fps


