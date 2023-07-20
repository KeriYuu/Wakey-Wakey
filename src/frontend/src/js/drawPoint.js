import * as d3 from 'd3'
import axios from 'axios'

function dragPoint(self) {
    axios.post("http://localhost:12050/getFrames", {
        'type': self.mode
    })
    .then(data=>
        {
            // this.testUrl = data.data.img_stream
            self.sourceKeypointImage = data.data['source_img_stream']
            self.drivingKeypointImage = data.data['driving_img_stream']
            self.drivingFrames = data.data['driving_frames']
            self.sourceFrames = data.data['source_frames']
            self.drivingKeypoints = data.data['driving_keypoints']
            self.sourceKeypoints = data.data['source_keypoints']
            self.carouselItems = self.drivingFrames
            self.carouselKeypoints = self.drivingKeypoints
            self.pointImage = self.carouselItems[self.imgIndex]
            self.frameNums = self.carouselItems.length - 1
            self.kpNums = (self.carouselKeypoints[0]).length
        }).then(()=>{
          const img = document.getElementById("pointImage")
          const width = img.width
          const height = img.height
          self.imageHeight = height
          self.imageWidth = width
        }).then(()=>{
            drawCircle(self)
            drawCircleLabel(self)
        })
}
function drawCircle(self){
    let imageHeight = self.imageHeight
    let imageWidth = self.imageWidth
    let keypoints = self.carouselKeypoints[self.imgIndex]
    let kpindex = self.kp_index
    let div = d3.select("#overlayImage")
    let svg = div.html('')
      .append("svg")
      .attr("width", imageWidth)
      .attr("height", imageHeight)

    // let svg = d3.select("#overlaySvg")
    let radius = 5
    
    let color = ['#e9d030', '#6f067e', '#ea5e1c', '#7cc6e0', '#c80029', '#b9bb77', '#777576', '#37403c', '#da70a7', '#2f63ab', '#e87856', '#47118c', '#e99d25', '#840976', '#ddf646', '#860011', '#7eae30', '#6a2d12', '#e6001c', '#243317'];

    let yScale = imageHeight / 255
    let xScale = imageWidth / 255

    let curKeypoints
    let curdata = []
    if(kpindex != null){
        console.log(keypoints[kpindex], kpindex, "debug2")
        curKeypoints = [keypoints[kpindex]]
        curKeypoints.forEach(function(d){
            curdata.push({'x': d[0] * xScale, 'y': d[1] * yScale, 'id': kpindex})
        })
    }else{
        curKeypoints = keypoints
        curKeypoints.forEach(function(d, i){
            curdata.push({'x': d[0] * xScale, 'y': d[1] * yScale, 'id': i})
        })
    }

    console.log(curKeypoints, curdata, "debug")
    svg.selectAll("circle")
    .data(curdata)
    .enter().append("circle")
    .attr("cx", function(d) { return  d.x; })
    .attr("cy", function(d) { return  d.y; })
    .attr("r", radius)
    .attr('stroke', 'white')
    .style("fill", function(d) { return color[d.id]; })
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    function dragstarted() {
        d3.select(this).raise().classed("active", true);
    }

    function dragged(e, d) {
        d.x = e.x
        d.y = e.y
        d3.select(this).attr("cx", d.x = e.x).attr("cy", d.y = e.y);
    }

    function dragended(e, d) {
        console.log(e)
        console.log(self.carouselKeypoints[self.imgIndex][d.id][0], self.carouselKeypoints[self.imgIndex][d.id][1], "dragended")
        console.log(self.carouselKeypoints)
        d3.select(this).classed("active", false);
        self.carouselKeypoints[self.imgIndex][d.id][0] = d.x / xScale, 
        self.carouselKeypoints[self.imgIndex][d.id][1] = d.y / yScale
    }
}

function drawCircleLabel(self){
    let circles = ['#e9d030', '#6f067e', '#ea5e1c', '#7cc6e0', '#c80029', '#b9bb77', '#777576', '#37403c', '#da70a7', '#2f63ab', '#e87856', '#47118c', '#e99d25', '#840976', '#ddf646', '#860011', '#7eae30', '#6a2d12', '#e6001c', '#243317']
    let radius = 8
    let circle_data = []
    for(let i=0; i < self.kpNums; i++){
        circle_data.push({"id": i, "color": circles[i]})
    }
    let div = d3.select("#circles")
    let bbox = div.node().getBoundingClientRect()
    let width = Math.ceil(bbox.width)
    let height = Math.ceil(bbox.height)
    let margin = {top: 0.2 * height, right: 0 * width, bottom: 0 * height, left: 0 * width}
    let each = width / (Math.min(self.kpNums, 10) + 1)
    let svg = div.html('')
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")


    var defs = svg.append("defs");


    var dropShadowFilter = defs.append('svg:filter')
      .attr('id', 'drop-shadow')
      .attr('filterUnits', "userSpaceOnUse")
      .attr('width', '250%')
      .attr('height', '250%');
    dropShadowFilter.append('svg:feGaussianBlur')
      .attr('in', 'SourceGraphic')
      .attr('stdDeviation', 2)
      .attr('result', 'blur-out');
    // dropShadowFilter.append('svg:feColorMatrix')
    //   .attr('in', 'blur-out')
    //   .attr('type', 'hueRotate')
    //   .attr('values', 180)
    //   .attr('result', 'color-out');
    dropShadowFilter.append('svg:feOffset')
      .attr('in', 'color-out')
      .attr('dx', 3)
      .attr('dy', 3)
      .attr('result', 'the-shadow');
    dropShadowFilter.append('svg:feBlend')
      .attr('in', 'SourceGraphic')
      .attr('in2', 'the-shadow')
      .attr('mode', 'normal');

    svg.selectAll("circleLabel")
    .data(circle_data)
    .enter().append("circle")
    .attr("class", 'circleLabel')
    .attr("id", function(d){ return "circle_" + d.id })
    .attr("cx", function(d) { return  each * (d.id + 1); })
    .attr("cy", function(d) { return  radius + 2 + Math.floor(d.id / 10) * 2 * radius; })
    .attr("r", radius)
    .attr('stroke', 'white')
    .style("filter", "url(#drop-shadow)")
    .style("fill", function(d) { return d.color; })
    .on("click", function(){
        d3.selectAll('.circleLabel').attr('stroke', "white")
        d3.select(this).attr('stroke', "black")
        self.kp_index = Number(d3.select(this).attr('id').split('_')[1])
        drawCircle(self)
        console.log(d3.select(this).attr('id').split('_')[1])
    })
}

export { dragPoint, drawCircle }