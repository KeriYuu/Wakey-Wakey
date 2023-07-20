<template>
  <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
  <!-- <HelloWorld msg="Welcome to Your Vue.js App"/> -->
  <div class="whole">
    <div class="pageHeader">
      <el-page-header :icon="ArrowLeft">
        <template #content>
          <div class="flex items-center">
            <el-avatar
            :size="50"
            class="mr-3"
            :src="headerImg"
            />
            <div class="title"> AnimaText </div>
            <!-- <el-tag>Default</el-tag> -->
          </div>
        </template>
      </el-page-header>
    </div>

    <el-divider />

    <div class="mainContent">

      <div class="step1">

        <div class="inputBox">
          <el-row :gutter="20">
            <el-col :span="14">
              <el-input 
              v-model="msg" 
              placeholder="Please input" 
              @change="textChange"
              clearable 
              >
                <template #prefix>
                  <el-icon class="el-input__icon"><edit /></el-icon>
                </template>
              </el-input>
            </el-col>

            <el-col :span="4">
            </el-col>

            <el-col :span="1">
              <el-button circle @click="shotPic">
                <el-icon><Camera /></el-icon>
              </el-button>
            </el-col>

            <el-col :span="2">
            </el-col>

            <el-col :span="1">
              <el-button circle @click="gotoStepTwo">
                <el-icon><Right /></el-icon>
              </el-button>
            </el-col>

          </el-row>
        </div>

        <div class="textCanvas">
          <canvas id="wordcanvas"></canvas>
        </div>

        <div class="selectElement">
          <el-row :gutter="40">
            <el-col :span="8">
              <el-checkbox label="text" v-model="iftext" @change="textChange"/>
            </el-col>
            <el-col :span="8">
              <el-checkbox label="point" v-model="ifpoint" @change="textChange"/>
            </el-col>
            <el-col :span="8">
              <el-checkbox label="line" v-model="ifline" @change="textChange"/>
            </el-col>
          </el-row>
        </div>

        <div class="editStyle">
            <el-row :gutter="20">
              <el-col :span="7">
                <el-input 
                v-model="color" 
                placeholder="Please input" 
                clearable 
                >
                </el-input>
              </el-col>
              <el-col :span="6">
                <el-color-picker v-model="color" show-alpha @change="textChange"/>
              </el-col>
              <el-col :span="10">
                <el-select v-model="font" value-key="font" placeholder="Select" @change="fontChange">
                  <el-option
                    v-for="item in fontsList"
                    :key="item.font"
                    :label="item.font"
                    :value="item"
                  >
                    <span :style="{'font-family': item.font }">{{ item.font }}</span>
                  </el-option>
                </el-select>
              </el-col>
            </el-row>
        </div>
        
        <div class="upload">
          <div class="preview">
            <el-image :src="imageUrl" alt="Preview Image" 
            style="width: 200px;"
            :preview-src-list="previewList"
            :initial-index="0"/>
          </div>
          <div class="uploadlist">
            <el-upload
              :file-list="fileList"
              action="#"
              list-type=""
              :auto-upload="true"
              :http-request="uploadFile"
              :on-preview="handlePictureCardPreview"
              :on-remove="handleRemove"
              :show-file-list="true"
              :on-change="handleChange"
            >
              <el-button circle><el-icon><Upload /></el-icon></el-button>
            </el-upload>

          </div>
        </div>

      </div>

      <div class="step2">
        <div class="imgButton">
          <el-row :gutter="20">
            <el-col :span="10"><img id="drivingImage" class="activeImage" :src="drivingKeypointImage" style="height: 15vh;" @click="changeDriving"/></el-col>
            <el-col :span="10"><img id="sourceImage" class="inactiveImage" :src="sourceKeypointImage" style="height: 15vh;" @click="changeSource"/></el-col>
            <el-col :span="4"><el-button circle @click="gotoStepThree"><el-icon><Right /></el-icon></el-button></el-col>
          </el-row>
        </div>
        <div class="circleLabelWrapper">
          <el-row :gutter="20">
            <el-col :span="1"></el-col>
            <el-col :span="1"><el-button circle @click="refresh"><el-icon><RefreshRight /></el-icon></el-button></el-col>
            <el-col :span="22"><div id="circles"></div></el-col>
          </el-row>
        </div>
        <div class="wrapper-father">
          <div class="wrapper"><img id="pointImage" style="height: 100%;" :src="pointImage"/></div>
          <div class="wrapper" id="overlayImage"></div>
        </div>
        <div class="slider">
          <el-row :gutter="10">
            <el-col :span = 1></el-col>
            <el-col :span = 1.5>
              <el-button circle @click="videoPlay"><el-icon><VideoPlay /></el-icon></el-button>
            </el-col>
            <el-col :span = 1.5>
              <el-button circle @click="videoStop"><el-icon><VideoPause /></el-icon></el-button>
            </el-col>
            <el-col :span = 1></el-col>
            <el-col :span = 17>
              <div class="slider"><el-slider v-model="imgIndex" :step='1' :min="0" :max="frameNums" show-stops @change="frameChange"/></div>
            </el-col>
            <el-col :span = 1></el-col>
          </el-row>
        </div>
      </div>

      <div class="step3">
        <div class="step3top">
          <div class="step3settings">
            <el-row :gutter="24">
              <el-col :span="2"><el-button circle @click="gotoFinal"><el-icon><Right /></el-icon></el-button></el-col>
              <el-col :span="2"><el-button circle @click="downloadFinal"><el-icon><Download /></el-icon></el-button></el-col>
              <el-col :span="1"></el-col>
              <el-col :span="2">fps: </el-col>
              <el-col :span="3"><el-input v-model="fps" placeholder="Please input" clearable /></el-col>
              <el-col :span="1">ε: </el-col>
              <el-col :span="4"><el-input v-model="epsilon" placeholder="Please input" clearable /></el-col>
              <el-col :span="1">α: </el-col>
              <el-col :span="4"><el-input v-model="alpha" placeholder="Please input" clearable /></el-col>
              <el-col :span="2"><el-checkbox label="fromD" v-model="ifdriving" @change="textChange"/></el-col>
            </el-row>

          </div>
          <div class="step3res"><div class="finalGIF"><img :src="resultGIF" style="height: 100%;"/></div><div class="step3border"></div></div>
        </div>

        <div class="step3-selectElement">
          <el-row :gutter="40">
            <el-col :span="8">
              <el-button circle @click="startEdit"><el-icon><pointer /></el-icon></el-button>
            </el-col>
            <el-col :span="8">
              <el-checkbox label="text" v-model="step3iftext" @change="step3textChange"/>
            </el-col>
            <el-col :span="8">
              <el-checkbox label="line" v-model="step3ifline" @change="step3textChange"/>
            </el-col>
          </el-row>
        </div>

        <div class="step3-wrapper-father">
          <div class="step3-wrapper" id="step3-textCanvas"><canvas id="step3-wordcanvas"></canvas></div>
          <div class="step3-wrapper" id="step3-overlayImage"></div>
        </div>
        <div class="slider">
          <el-row :gutter="10">
            <el-col :span = 1></el-col>
            <el-col :span = 1.5>
              <el-button circle @click="step3videoPlay"><el-icon><VideoPlay /></el-icon></el-button>
            </el-col>
            <el-col :span = 1.5>
              <el-button circle @click="step3videoStop"><el-icon><VideoPause /></el-icon></el-button>
            </el-col>
            <el-col :span = 1></el-col>
            <el-col :span = 17>
              <div class="slider"><el-slider v-model="step3index" :step='1' :min="0" :max="frameNums" show-stops @change="step3frameChange"/></div>
            </el-col>
            <el-col :span = 1></el-col>
          </el-row>
        </div>

      </div>

    </div>



    <div class="stepSlider">
        <el-steps :active="stepIndex" finish-status="success">
          <el-step title="TextandGIF Input" />
          <el-step title="Keypoint Correction" />
          <el-step title="Result Refinement"/>
        </el-steps>
    </div>

  </div>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'
// import DisplayText from './components/DisplayText.vue'
import { drawWithFont } from "./js/displayText.js"
import { drawCrds, getFinalRes, dragCrds } from "./js/drawCrds.js"
import { dragPoint, drawCircle } from "./js/drawPoint.js"
import FileSaver from 'file-saver'
import '@/fonts/google-webfonts.ttf.css'
import { ElMessage } from 'element-plus'
import * as d3 from 'd3'
import axios from 'axios'
import path from 'path'
// import { ArrowLeft } from '@element-plus/icons-vue'
export default {
  name: 'App',
  components: {
    // ArrowLeft
    // HelloWorld
    // DisplayText
  },
  data(){
    return {
      // header
      headerImg:require("../public/WechatIMG660.jpeg"),
      stepIndex: 0,
      mode: 'default',
      // step 1
      msg: "idea",
      color:"#000000",
      iftext: true,
      ifpoint: false,
      ifline: false,
      fontsList: [],
      font: 'ABeeZee',
      fontURL: "http://themes.googleusercontent.com/static/fonts/abeezee/v1/JYPhMn-3Xw-JGuyB-fEdNA.ttf",
      // font: 'Acme',
      // fontURL: "http://themes.googleusercontent.com/static/fonts/acme/v2/h0STFiiHJJuefGZJAxrSiA.ttf",
      imageUrl: '',
      imageName: '',
      previewList: [],
      fileList: [],
      gifLimit: 1,
      // step2
      carouselItems: [],
      carouselKeypoints: [],
      pointImage: '',
      imgIndex: 0,
      frameNums: 0,
      kpNums: 0,
      kp_index: null,
      drivingFrames: [],
      sourceFrames: [],
      sourceKeypointImage: '',
      drivingKeypointImage: '',
      imageWidth: 0,
      imageHeight: 0,
      drivingKeypoints: [],
      sourceKeypoints: [],
      nIntervId: null,
      // step3
      step3nIntervId: null,
      left: 0,
      top: 0,
      scale: 0,
      step3left: 0,
      step3top: 0,
      step3scale: 0,
      coordinates: [],
      step3iftext: true,
      step3ifpoint: false,
      step3ifline: false,
      newCrds: [],
      step3index: 0,
      canvasList: [],
      resultGIF: '',
      fps: 5,
      step3height: 0,
      step3width: 0,
      ifedit: false,
      epsilon: 2,
      alpha: 0,
      ifdriving: false
    }
  },

  mounted(){
    let self = this
    // 读取默认 GIF 列表
    let gifs = require.context('../public/defaultGIF', false, /.gif$/).keys()
    self.gifLimit = gifs.length
    self.fileList = gifs.map(x => ({name:x.split("/").slice(-1)[0], url: path.join("./defaultGIF", x)}))
    self.previewList = self.fileList.map(x => x.url)
    self.imageUrl = self.fileList[0].url
    self.imageName = self.fileList[0].name

    // 画出文字
    drawWithFont(self, 'step1')
    //读取字体列表，读多了会被google拦截好像
    d3.json("./fonts.json").then(function(data) {
      self.fontsList = data.slice(0, 10)
    })
    // 画 step 2
    dragPoint(self)
    // 画 step 3
    drawWithFont(self, 'step3')
    setTimeout(()=>{
      drawCrds(self)
    }, 500)
  },

  methods: {
    textChange(){
      drawWithFont(this, 'step1')
    },
    fontChange(item){
      this.fontURL = item.url
      drawWithFont(this, 'step1')
    },
    shotPic() {
      let node = document.getElementById('wordcanvas') // 通过id获取dom
      let dataUrl = node.toDataURL('image/png')
      FileSaver.saveAs(dataUrl, 'text.png')
    },
    handleRemove(file, fileList) {
      URL.revokeObjectURL(file.url)
      if (fileList.length > 0){
        this.imageUrl = fileList[0].url
        this.imageName = fileList[0].name
      }
    },
    handleChange(file, fileList) {
      if(fileList.length > this.gifLimit){
        URL.revokeObjectURL(fileList[0].url)
        fileList.splice(0, 1)
        this.previewList = fileList.map(x => x.url)
      }
      let url = URL.createObjectURL(file.raw)
      console.log(file, "herea")
      fileList[this.gifLimit - 1].url = url
      this.previewList = fileList.map(x => x.url)
      this.imageUrl = url
      this.imageName = file.name
    },
    handlePictureCardPreview(file) {
      this.imageUrl = file.url;
      this.imageName = file.name
    },
    uploadFile(params) {
      console.log("params", params)
      let form = new FormData();
      form.append("file", params.file);

      axios.post("http://localhost:12050/getGif", form);
    },
    gotoStepTwo(){
      this.mode = "user"
      let node = document.getElementById('wordcanvas') // 通过id获取dom
      let dataUrl = node.toDataURL('image/png')
      console.log('dataUrl', dataUrl)
      axios.post("http://localhost:12050/getTextandGenerate", {
        'fps': this.fps,
        'imageName': this.imageName,
        'dataUrl': dataUrl
      })
      .then((data) => {
        this.fps = data.data['fps']
        dragPoint(this)
        this.stepIndex = 1
      })
      .then(()=>{
        setTimeout(()=>{
          drawCrds(this)
        })
      })
      // .then(()=>{
      //   setTimeout(()=>{
      //     ElMessage({
      //     message: 'Generation Completed!',
      //     type: 'success',
      //     })
      //   }, 12000 / this.fps)
      // })
    },

    changeSource(){
      d3.select("#sourceImage").attr('class', "activeImage")
      d3.select("#drivingImage").attr('class', "inactiveImage")
      this.carouselItems = this.sourceFrames
      this.carouselKeypoints = this.sourceKeypoints
      this.pointImage = this.carouselItems[this.imgIndex]
      drawCircle(this)
    },
    changeDriving(){
      d3.select("#sourceImage").attr('class', "inactiveImage")
      d3.select("#drivingImage").attr('class', "activeImage")
      this.carouselItems = this.drivingFrames
      this.carouselKeypoints = this.drivingKeypoints
      this.pointImage = this.carouselItems[this.imgIndex]
      drawCircle(this)
    },
    refresh(){
      this.kp_index = null
      d3.selectAll('.circleLabel').attr('stroke', "white")
      drawCircle(this)
    },
    frameChange(val){
      this.pointImage = this.carouselItems[val]
      drawCircle(this)
    },
    videoPlay() {
      let self = this
      if (!self.nIntervId) {
        self.imgIndex = 0
        self.nIntervId = setInterval(function() {
          self.imgIndex += 1
          if (self.imgIndex === self.frameNums){
            self.imgIndex = 0
            self.pointImage = self.carouselItems[self.imgIndex]
            drawCircle(self)
            clearInterval(self.nIntervId)
            self.nIntervId = null;
          }
          self.pointImage = self.carouselItems[self.imgIndex]
          drawCircle(self)
        }, 1000 / self.fps);
      }
    },
    videoStop() {
      clearInterval(this.nIntervId);
      this.nIntervId = null;
    },


    gotoStepThree() {
      this.mode = "user"
      let node = document.getElementById('wordcanvas') // 通过id获取dom
      let dataUrl = node.toDataURL('image/png')
      console.log('dataUrl', dataUrl)
      axios.post("http://localhost:12050/modifyKeypointsandGenerate", {
        'fps': this.fps,
        'imageName': this.imageName,
        'dataUrl': dataUrl,
        'skeypoints': this.sourceKeypoints,
        'dkeypoints': this.drivingKeypoints
      })
      .then(() => {
        dragPoint(this)
        this.stepIndex = 2
      })
      .then(()=>{
        setTimeout(()=>{
          drawCrds(this)
        })
      })
      // .then(()=>{
      //   setTimeout(()=>{
      //     ElMessage({
      //     message: 'Generation Completed!',
      //     type: 'success',
      //     })
      //   }, 12000 / this.fps)
      // })
    },

    step3textChange(){
      drawWithFont(this, 'step3')
      dragCrds(this)
    },
    step3frameChange(){
      drawWithFont(this, 'step3')
      console.log(this.step3index, "debug")
      dragCrds(this)
      console.log(this.step3index, "debug2")
    },
    step3videoPlay() {
      let self = this
      if (!self.step3nIntervId) {
        self.step3index = 0
        self.step3nIntervId = setInterval(function() {
          self.step3index += 1
          if (self.step3index === self.frameNums){
            self.step3index = 0
            drawWithFont(self, 'step3')
            dragCrds(self)
            clearInterval(self.step3nIntervId)
            self.step3nIntervId = null;
          }
          drawWithFont(self, 'step3')
          dragCrds(self)
        }, 1000 / self.fps);
      }
    },
    step3videoStop() {
      clearInterval(this.step3nIntervId);
      this.step3nIntervId = null;
    },
    startEdit(){
      // let node = document.getElementById('step3-wordcanvas') // 通过id获取dom
      // let dataUrl = node.toDataURL('image/png')
      // FileSaver.saveAs(dataUrl, 'text.png')
      // console.log(getFinalRes)
      this.mode = "user"
      this.ifedit = !this.ifedit
      dragCrds(this)
      if (!this.ifedit){
        getFinalRes(this)
        setTimeout(()=>{
          ElMessage({
          message: 'Generation Completed!',
          type: 'success',
          })
        }, 3000 / this.fps)
      }
    },
    downloadFinal(){
      FileSaver.saveAs(this.resultGIF, 'result.gif');
    },
    gotoFinal() {
      this.mode = "user"
      drawCrds(this)
      this.stepIndex = 3
      // setTimeout(()=>{
      //   ElMessage({
      //   message: 'Generation Completed!',
      //   type: 'success',
      //   })
      // }, 3000 / this.fps)
    },

  }
}
</script>

<style lang="scss">
#app {
  /* font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale; */
  text-align: center;
  /* color: #2c3e50;
  margin-top: 60px; */
}
/* .pageHeader {
  margin-top: 20px;
  margin-bottom: 20px;
} */
.whole {
  margin-left: 2vw;
  margin-right: 2vw;
  margin-bottom: 1vw;
}
.mainContent {
    width: 100%;
    height: 80vh;
    display: flex;
}
.step1{
  width: 30%;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  margin-bottom: 2vh;
  margin-right: 2vw;
}
.inputBox{
  width: 80%;
  margin-top: 2vh;
  margin-left: 1vw;
}
.textCanvas{
  margin-left: 1vw;
  width: 93%;
  height: 30vh;
  margin-top:2vh;
}
.selectElement{
  margin-left: 1vw;
  width: 93%;
}
.editStyle{
  margin-left: 1vw;
  margin-top: 2vh;
}


.step2{
  width: 30%;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  margin-bottom: 2vh;
  margin-right: 2vw;
  margin-left: 2vw;
}
.activeImage { 
  border:solid 5px #5a5957;
  /* border-radius: 3rem; */
  border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
} 
.inactiveImage { 
  border-width: 5px;
  border-style: double;
  Border-color: #ccc;
  /* border-radius: 3rem; */
  border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
} 
.imgButton{
  margin-top: 5vh;
  margin-bottom: 5vh;
  margin-left: 2vw;
  margin-right: 2vw;
}

.step3{
  width: 30%;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  margin-bottom: 2vh;
  margin-right: 2vw;
  margin-left: 2vw;
}
.step3-wrapper-father {
  text-align: center;
  position: relative !important;
  height: 30vh;
  .step3-wrapper {
    position: absolute !important;
    y: 0;
    text-align: center;
    width: 100%;
    margin: auto;
    height: 100%;
  }
}
// .step3top{
// }
.finalGIF{
  // margin-left: 1vw;
  // width: 93%;
  // height: 23vh;
  // margin-top:2vh;
  position: absolute;
  width: 100%;
  height: 100%
}
.step3settings{
  margin-top: 4vh;
  margin-right: 2vw;
  margin-left: 2vw;
}
.step3res{
  height: 18vh;
  position: relative;
  margin-left: 3vw;
  margin-right: 3vw;
  margin-top: 4vh;
  margin-bottom: 5vh
}
.step3border{
  height: 100%;
  width: 100%;
  border-width: 5px;
  border-style: double;
  Border-color: #ccc;
  // border-radius: 3rem;
  border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  position: absolute
}
.stepSlider {
    width: 90%;
    height: 5vh;
    margin-left: 5vw;
    margin-right: 5vw;
    text-align:left
}
.upload{
  margin-left: 1vw;
  margin-right: 1vw;
  margin-top: 3vh;
  display: flex;
}
.preview{
  width: 60%;
}
.uploadlist{
  width:35%;
}

.el-carousel {
    --el-carousel-indicator-width: 15px !important
}

.wrapper-father {
  text-align: center;
  position: relative !important;
  height: 40vh;
  .wrapper {
    position: absolute !important;
    y: 0;
    text-align: center;
    width: 100%;
    margin: auto;
    height: 100%;
  }
}

.active {
  stroke: #000;
  stroke-width: 2px;
}

.circleLabelWrapper{
  height: 5vh;
  margin-top: 5vh;
  text-align: center;
}
#circles{
  height: 100%;
}
.step3-selectElement{
  margin-left: 1vw;
  margin-top: 2vh;
  width: 93%;
}
// .el-page-header__content {
//   margin-top: -2vh
// }
.el-avatar--circle {
    border-radius: 50%;
    --el-avatar-size: 70px;
}
.title{
  margin-top: 1.5vh !important;
  margin-left: 1vw !important
}
.flex.items-center{
  display: flex !important;
}
/* .activeImage { 
  box-shadow: 20px 38px 34px -26px hsla(0,0%,0%,.2);
  border-radius: 37px 140px 23px 130px/110px 19px 120px 24px;
  border:solid 2px #41403E;
  border-top-left-radius: 37px, 140px;
  border-top-right-radius: 23px, 130px;
  border-bottom-left-radius: 110px, 19px;
  border-bottom-right-radius: 120px, 24px;
}  */
/* .inactiveImage { 
  box-shadow: 20px 38px 34px -26px hsla(0,0%,0%,.2);
  border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
  border:dotted 2px #41403E;
}  */
</style>
