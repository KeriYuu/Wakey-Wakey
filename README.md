# Wakey-Wakey
This repository contains the source code for the paper Wakey-Wakey: Animate Text by Mimicking Characters in a GIF.

![Interface](assets/interface.png)

## Authoring System

The frontend of Wakey-Wakey is built with Vue.js, providing an interactive user interface. It consists of three main views:

- **Input View**: Users input text and customize its static appearance. They can also upload and preview the driving GIF.
- **Correction View**: Users can adjust the key points of the animated text at specific frames.
- **Refinement View**: Users can refine the animation by adjusting the glyph's control points and configuring the algorithm’s parameters.

## Key Components

1. **Driving Animation Key Point Extraction**: The project first extracts key points from the given GIF using a pre-trained First Order Motion Model  [FOMM](https://github.com/AliaksandrSiarohin/first-order-model).
2. **Key Point and Text Control Point Alignment**: The extracted key points are then aligned with the control points of the text to generate the animated text.

The final output is a GIF that animates the input text according to the movements in the input GIF.

## Performance

Wakey-Wakey is designed for efficiency. An automatic generation takes around 300ms/frame (CPU: Intel i7 4.9 GHz).

## Installation

Clone the repository and navigate into the project directory. Then follow the steps to set up the backend and frontend.

```bash
# Clone the repository
git clone https://github.com/KeriYuu/Wakey-Wakey.git
cd wakey-wakey

# Set up the backend
cd backend
conda create -n wakey python==3.7
conda activate wakey
pip install -r requirements.txt

# Set up the frontend
cd ../frontend
npm install
```

### Download Pretrained Model

Download the pretrained [FOMM](https://github.com/AliaksandrSiarohin/first-order-model) model using the following command:

```bash
cd ../frontend/models
wget https://drive.google.com/u/0/uc?id=1UT8aBPrjMUPTCmbtDsKk-BCVgIHP5WFc&export=download
```

## Running the Project

To run the project, you need to start the backend and frontend servers.

```bash
# Start the backend server
cd backend
python run.py

# Start the frontend server in a new terminal
cd ../frontend
npm run serve
```

Now, navigate to `http://localhost:8080` in your web browser to use the application.
