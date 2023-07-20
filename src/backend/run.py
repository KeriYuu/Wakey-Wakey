from flask import Flask
from flask_cors import CORS
import json
import os
from flask import send_file, request, jsonify, send_from_directory
import base64

import numpy as np
import shutil   

from models.demo import generate
from deformation.localTrans import getTransCdrs
from deformation.laplacianOpt import get_opt_coords
from utils import generateGIF

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
# flask_cors: Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
CORS(app)


text_path = './textImage/text.png'
image_name = "00112.gif"
opt = {
    'config': './models/config/mgif-256.yaml',
    'checkpoint': './models/mgif-cpk.pth.tar',
    # 'checkpoint': './models/00000119-checkpoint.pth.tar',
    # 'config': './models/config/vox-256.yaml',
    # 'checkpoint': './models/vox-cpk.pth.tar',
    # 'config': './models/config/fashion-256.yaml',
    # 'checkpoint': './models/fashion.pth.tar',
    # 'config': './models/config/taichi-256.yaml',
    # 'checkpoint': './models/taichi-cpk.pth.tar',
    # 'config': './models/config/nemo-256.yaml',
    # 'checkpoint': './models/nemo-cpk.pth.tar',
    'source_image': text_path,
    'driving_video': os.path.join('./userGIF/', image_name),
    'source_keypoint': './userResults/result1/source_keypoint.gif',
    'driving_keypoint': './userResults/result1/driving_keypoint.gif',
    'relative': True,
    'adapt_scale': False,
    'cpu': True,
    'fps': 5
}


@app.route('/getGif', methods=['POST'])
def _getGIF():
    file = request.files.get('file')
    if file:
        print(file.filename)
        file.save(os.path.join("./userGIF/", file.filename))
    return "Done"

@app.route('/getTextandGenerate', methods=['POST'])

def _getTextandGenerate():
    data = request.get_json(silent=True)
    fps = int(data['fps'])
    text_url = data['dataUrl']
    image_name = data['imageName']
    text_path = './textImage/text.png'
    img_url = text_url.split(",")[1]
    imgdata = base64.b64decode(img_url)
    with open(text_path, mode="wb") as f:
        f.write(imgdata)

    print(image_name)
    opt['driving_video'] = os.path.join('./userGIF/', image_name)
    opt['fps'] = fps

    shutil.rmtree("./userResults/driving_frames")
    os.makedirs("./userResults/driving_frames")

    shutil.rmtree("./userResults/source_frames")
    os.makedirs("./userResults/source_frames")

    fps = generate(opt, False, None, None) 
    print('=======fps: ', fps)
    return json.dumps({
        "fps": fps
    })

@app.route('/getFrames', methods=['POST'])
def _getFrames():
    # post_data = json.loads(request.data.decode())
    type = request.get_json(silent=True)['type']
    if type == "default":
        dirpath = "./defaultResults"
    if type == "user":
        dirpath = "./userResults"
    #Frames
    # driving
    drivingDir = os.path.join(dirpath, "./driving_frames")
    file_list = [x for x in os.listdir(drivingDir) if x.endswith('png')]
    file_list.sort(key=lambda x: int(x.split('.')[0][5:]))
    driving_frames = []
    for each in file_list:
        with open(os.path.join(drivingDir, each), 'rb') as img_f:
            img_stream = img_f.read()
            img_stream = 'data:image/png;base64,' + base64.b64encode(img_stream).decode()
            driving_frames.append(img_stream)
    # source
    sourceDir = os.path.join(dirpath, "./source_frames")
    file_list = [x for x in os.listdir(sourceDir) if x.endswith('png')]
    file_list.sort(key=lambda x: int(x.split('.')[0][5:]))
    source_frames = []
    for each in file_list:
        with open(os.path.join(sourceDir, each), 'rb') as img_f:
            img_stream = img_f.read()
            img_stream = 'data:image/png;base64,' + base64.b64encode(img_stream).decode()
            source_frames.append(img_stream)
    #GIF
    # driving
    path = os.path.join(dirpath, './result1/driving_keypoint.gif')
    with open(path, 'rb') as img_f:
        img_stream = img_f.read()
        driving_img_stream = 'data:image/gif;base64,' + base64.b64encode(img_stream).decode()
    # source
    path = os.path.join(dirpath, './result1/source_keypoint.gif')
    with open(path, 'rb') as img_f:
        img_stream = img_f.read()
        source_img_stream = 'data:image/gif;base64,' + base64.b64encode(img_stream).decode()
    # keypoints
    driving_keypoints = [[[float(x) for x in each] for each in item] for item in np.load(os.path.join(dirpath, './keypoints/driving_keypoints.npy'))]
    source_keypoints = [[[float(x) for x in each] for each in item] for item in np.load(os.path.join(dirpath, './keypoints/source_keypoints.npy'))]
    
    return json.dumps({
        "driving_frames": driving_frames,
        "source_frames": source_frames,
        "driving_img_stream": driving_img_stream,
        "source_img_stream": source_img_stream,
        "driving_keypoints": driving_keypoints,
        "source_keypoints": source_keypoints
    })

@app.route('/modifyKeypointsandGenerate', methods=['POST'])
def _modifyKeypointsandGenerate():
    data = request.get_json(silent=True)
    fps = data['fps']
    text_url = data['dataUrl']
    image_name = data['imageName']
    skeypoints = data['skeypoints']
    dkeypoints = data['dkeypoints']
    text_path = './textImage/text.png'
    img_url = text_url.split(",")[1]
    imgdata = base64.b64decode(img_url)
    with open(text_path, mode="wb") as f:
        f.write(imgdata)

    print(image_name)
    opt['driving_video'] = os.path.join('./userGIF/', image_name)
    opt['fps'] = fps
    

    shutil.rmtree("./userResults/driving_frames")
    os.makedirs("./userResults/driving_frames")

    shutil.rmtree("./userResults/source_frames")
    os.makedirs("./userResults/source_frames")

    fps = generate(opt, True, skeypoints, dkeypoints)

    return "Done"

@app.route('/getCoordinatesKeypoints', methods=['POST'])
def _getCoordinatesKeypoints():
    data = request.get_json(silent=True)
    epsilon, alpha, scale, left, top, width, height, coordinate, drivingKeypoints, sourceKeypoints, ifdriving  = float(data['epsilon']), float(data['alpha']), data['scale'], data['left'], data['top'], data['width'], data['height'], data['coordinates'], data['drivingKeypoints'], data['sourceKeypoints'], data['ifdriving']
    # print(epsilon, alpha, scale, left, top, width, height)
    # print('coordinate', coordinate)
    if ifdriving:
        sourceKeypoints = drivingKeypoints
    sourceKeypoints = np.array(sourceKeypoints)
    # sourceKeypoints[:,:,0] = sourceKeypoints[:,:,0] * width / 256
    # sourceKeypoints[:,:,1] = sourceKeypoints[:,:,1] * height / 256
    # print(epsilon, scale, left, top, width, height)

    scale_coordinate = []
    for i in range(len(coordinate) // 2):
        x, y = coordinate[i * 2], coordinate[i * 2 + 1]
        nx, ny = round(scale * x + left), round(-scale * y + top)
        scale_coordinate.append(nx)
        scale_coordinate.append(ny)
    scale_new_coordinates = getTransCdrs(epsilon, scale_coordinate, sourceKeypoints)
    if alpha > 1e-6:
        scale_new_coordinates = get_opt_coords(scale_new_coordinates, alpha = alpha, k=5, num_iters=20, lr=0.5)
    new_coordinates = []
    for frame_crds in scale_new_coordinates:
        temp = []
        for i in range(len(frame_crds) // 2):
            x, y = frame_crds[i * 2], frame_crds[i * 2 + 1]
            nx, ny = round((x - left) / scale), round((y - top) / (-scale))
            temp.append(nx)
            temp.append(ny)
        new_coordinates.append(temp)

    # print('sourceKeypoints', sourceKeypoints)
    # print('new_coordinates', new_coordinates)
    # if alpha < 1e-6:
    # if True:
    return json.dumps({
        "new_coordinates": new_coordinates
        # "new_coordinates": nnew_coordinatesåå
    })
    # else:
    #     nnew_coordinates = get_opt_coords(new_coordinates, alpha = alpha, k=5, num_iters=20, lr=0.5)
    #     return json.dumps({
    #         "new_coordinates": nnew_coordinates
    #     })

@app.route('/getdefaultFinalCanvas', methods=['GET'])
def _getdefaultFinalCanvas():
    tpath = './defaultResults/result2/result.gif'
    with open(tpath, 'rb') as img_f:
        img_stream = img_f.read()
        result_img_stream = 'data:image/gif;base64,' + base64.b64encode(img_stream).decode()
    return json.dumps({
        "resultGIF": result_img_stream,
    })

@app.route('/getfinalCanvas', methods=['POST'])
def _getfinalCanvas():
    data = request.get_json(silent=True)
    fps = int(data['fps'])
    text_url = data['canvasList']

    shutil.rmtree("./userResults/finalCanvas")
    os.makedirs("./userResults/finalCanvas")

    text_path = './userResults/finalCanvas/frame%d.png'
    for i, img in enumerate(text_url):
        img_url = img.split(",")[1]
        imgdata = base64.b64decode(img_url)
        with open(text_path%i, mode="wb") as f:
            f.write(imgdata)
    tpath = './userResults/result2/result.gif'
    generateGIF(fps, './userResults/finalCanvas', tpath)
    with open(tpath, 'rb') as img_f:
        img_stream = img_f.read()
        result_img_stream = 'data:image/gif;base64,' + base64.b64encode(img_stream).decode()
    return json.dumps({
        "resultGIF": result_img_stream,
    })


if __name__=='__main__':

        # x = os.fork()
        # if x:
        #     print('I am son')
        #     os.system("cd ../frontend; npm run serve")
        # else:
            # print('I am papa')
    try:
        app.run(host='127.0.0.1', port=12050, use_reloader=False, debug=True)
    except:
        print("Something wrong!")

    # opt = {
    #     'config': './models/config/mgif-256.yaml',
    #     'checkpoint': './models/mgif-cpk.pth.tar',
    #     'source_image': './textImage/text.png',
    #     'driving_video': './userGIF/00112.gif',
    #     'source_keypoint': './result1/source_keypoint.gif',
    #     'driving_keypoint': './result1/driving_keypoint.gif',
    #     'relative': True,
    #     'adapt_scale': False,
    #     'cpu': True,
    #     'fps': 5
    # }
    # generate(opt)