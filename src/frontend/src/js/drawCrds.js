import * as d3 from 'd3'
import axios from 'axios'
import { drawWithFont } from "./displayText.js"

function drawCrds(self){
  console.log(self.step3top, self.step3scale, self.step3width, "debugg")
    axios.post("http://localhost:12050/getCoordinatesKeypoints", {
      'epsilon': self.epsilon,
      'alpha': self.alpha,
      'scale': self.step3scale,
      'top': self.step3top,
      'left': self.step3left,
      'width': self.step3width,
      'height': self.step3height,
      'coordinates': self.coordinates,
      'drivingKeypoints': self.drivingKeypoints,
      'sourceKeypoints': self.sourceKeypoints,
      'ifdriving': self.ifdriving
    })
    .then(data => {
      self.newCrds = data.data['new_coordinates']
      console.log('for test', data.data['new_coordinates'])
      drawWithFont(self, 'step3')
    })
    .then(()=>{
      getFinalRes(self)
    })
}
function getFinalRes(self){
  self.step3ifline = false
  self.step3index = 0
  self.canvasList = []
  if(self.mode === "default"){
    axios.get("http://localhost:12050/getdefaultFinalCanvas")
    .then(d => {
      self.resultGIF = d.data['resultGIF']
    })
  }
  if (self.mode === "user"){
    self.step3nIntervId = setInterval(function() {
        let node = document.getElementById('step3-wordcanvas') // 通过id获取dom
        self.canvasList.push(node.toDataURL('image/png'))
        self.step3index += 1
        if (self.step3index === self.frameNums){
          self.step3index = 0
          clearInterval(self.step3nIntervId)
          self.step3nIntervId = null;
          self.step3ifline = true
          axios.post("http://localhost:12050/getfinalCanvas", {
            'fps': self.fps,
            'canvasList': self.canvasList,
          })
          .then(d => {
            self.resultGIF = d.data['resultGIF']
          })
        }
        drawWithFont(self, 'step3')
    }, 1000 / self.fps)
  }
}
function dragCrds(self) {
    const width = self.step3width
    const height = self.step3height
    let div = d3.select("#step3-overlayImage")
    let svg = div.html('')
      .append("svg")
      .attr("width", width)
      .attr("height", height)

    if (self.ifedit){
        let radius = 2
    
        let color = 'red'
    
        let crds = self.newCrds[self.step3index]
    
        let curdata = []
    
        for (let i=0; i < crds.length / 2; i++){
            curdata.push({'x': self.step3scale * crds[i * 2] + self.step3left, 'y': -self.step3scale * crds[i * 2 + 1] + self.step3top, 'id': i})
        }
    
        // svg.append('rect').attr('width', width).attr('height', height).attr('fill', 'red')
        svg.selectAll("step3circle")
        .data(curdata)
        .enter().append("circle")
        .attr("cx", function(d) { return  d.x; })
        .attr("cy", function(d) { return  d.y; })
        .attr("r", radius)
        .attr('stroke', 'white')
        .style("fill", function() { return color; })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
    }
    function dragstarted() {
        d3.select(this).raise().classed("active", true);
    }

    function dragged(e, d) {
        d3.select(this).attr("cx", d.x = e.x).attr("cy", d.y = e.y);
    }

    function dragended(e, d) {
        console.log(e, d, "dragended")
        d3.select(this).classed("active", false);
        self.newCrds[self.step3index][d.id * 2] = (d.x - self.step3left) / self.step3scale
        self.newCrds[self.step3index][d.id * 2 + 1] = (d.y - self.step3top) / (-self.step3scale)
        drawWithFont(self, 'step3')
    }
}

export {drawCrds, getFinalRes, dragCrds}