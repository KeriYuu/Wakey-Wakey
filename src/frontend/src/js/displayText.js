import * as Typr from '@fredli74/typr'
import * as d3 from 'd3'


function load(self, step, resp)
{
    var request = new XMLHttpRequest();
    request.open("GET", self.fontURL, true);
    request.responseType = "arraybuffer";
    request.onload = function(e){resp(self, step, e.target.response);};
    request.send();
}

function fontLoaded(self, step, resp)
{
    console.log("fonttest", resp)
    let font = new Typr.Font(resp)
    drawWord(self, step, font)

}

// functions
function getDPR() { return window["devicePixelRatio"] || 1; }
function scaleCnv(cnv) {  cnv.setAttribute("style", "width:"+(cnv.width/getDPR())+"px; height:"+(cnv.height/getDPR())+"px");  }

function TyprShape(font,str) {
		
    var getGlyphPosition = function(font, gls,i1)
    {
        var g1=gls[i1],g2=gls[i1+1], kern=font["kern"];
        if(kern) {
            var ind1 = kern.glyph1.indexOf(g1);
            if(ind1!=-1)
            {
                var ind2 = kern.rval[ind1].glyph2.indexOf(g2);
                if(ind2!=-1) return [0,0,kern.rval[ind1].vals[ind2],0];
            }
        }
        //console.log("no kern");
        return [0,0,0,0];
    }
    
    
    var gls = [];
    for(let i=0; i<str.length; i++) {
        var cc = str.codePointAt(i);  if(cc>0xffff) i++;
        gls.push(font.codeToGlyph(cc));
    }
    var shape = [];
    // var x = 0, y = 0;
    
    for(let i=0; i<gls.length; i++) {
        var padj = getGlyphPosition(font, gls,i);
        var gid = gls[i];
        var ax=font["hmtx"].aWidth[gid]+padj[2];
        shape.push({"g":gid, "cl":i, "dx":0, "dy":0, "ax":ax, "ay":0});
        // x+=ax;
    }
    return shape;
}

function TyprShapeToPath(font,shape,clr) {
    var tpath = {cmds:[], crds:[]};
    var x = 0, y = 0;
    
    for(let i=0; i<shape.length; i++) {
        var it = shape[i]
        var path = font.glyphToPath(it["g"]), crds=path["crds"];
        for(let j=0; j<crds.length; j+=2) {
            tpath.crds.push(crds[j  ] + x + it["dx"]);
            tpath.crds.push(crds[j+1] + y + it["dy"]);
        }
        if(clr) tpath.cmds.push(clr);
        for(let j=0; j<path["cmds"].length; j++) tpath.cmds.push(path["cmds"][j]);
        var clen = tpath.cmds.length;
        if(clr) if(clen!=0 && tpath.cmds[clen-1]!="X") tpath.cmds.push("X");  // SVG fonts might contain "X". Then, nothing would stroke non-SVG glyphs.
        
        x += it["ax"];  y+= it["ay"];
    }
    return {"cmds":tpath.cmds, "crds":tpath.crds};
}

function drawOutline(font, path, ctx)
{
    // var ci=0, x=0, y=0;
    var crds = path.crds;
    console.log(crds, font.head)
    var w = 0.0025 * font.head.unitsPerEm;
    
    ctx.lineWidth = w;
    ctx.strokeStyle = "#00ffff";
    font.pathToContext(path,ctx);
    
    // ctx.stroke();
    
    var ss = w*4;
    // let ss = 1
    // ctx.fillStyle = "#ff0055";
    ctx.fillStyle = "red"
    for(var i=0; i<crds.length; i+=2) ctx.fillRect(crds[i]-ss,crds[i+1]-ss,2*ss,2*ss); 
    // for(var i=0; i<7; i+=2) ctx.fillRect(crds[i]-ss,crds[i+1]-ss,2*ss,2*ss); 
}

function drawWord(self, step, font)
{
    let divName = '.textCanvas'
    let canvasName = 'wordcanvas'
    if(step === "step3"){
        divName = '#step3-textCanvas'
        canvasName = 'step3-wordcanvas'
    }

    let div = d3.select(divName)
    let bbox = div.node().getBoundingClientRect()
    let width = Math.ceil(bbox.width)
    let height = Math.ceil(bbox.height)
    let margin = {top: height * 0.08, right: width * 0.08, bottom: height * 0.08, left: width * 0.08}

    let cnv = document.getElementById(canvasName);
    cnv.width = Math.floor((width - margin.left - margin.right) * getDPR());
    cnv.height = Math.floor((height - margin.top - margin.bottom) * getDPR());
    scaleCnv(cnv);
    var ctx = cnv.getContext("2d");
    ctx.fillStyle = "white"
    ctx.fillRect(0,0,cnv.width,cnv.height);
    var scale = Math.min((1.3 / self.msg.length), 0.23) * width * getDPR() / font.head.unitsPerEm;
    
    var shape = TyprShape(font, self.msg);
    var path = TyprShapeToPath(font, shape);
    console.log("pathaaaa", path)

    if(step === "step3"){
        self.step3height = cnv.height
        self.step3width = cnv.width
        path.crds = self.newCrds[self.step3index]
        self.step3left = margin.left * getDPR()
        self.step3top = margin.top * getDPR() + Math.round(font.hhea.ascender * scale)
        self.step3scale = scale
    }


    
    ctx.translate(margin.left * getDPR(), margin.top * getDPR() + Math.round(font.hhea.ascender * scale));  
    
    let ifline = self.ifline
    let iftext = self.iftext
    let ifpoint = self.ifpoint
    if(step === "step3"){
        ifline = self.step3ifline
        iftext = self.step3iftext
        ifpoint = self.step3ifpoint
    }
    if(ifline){
        ctx.fillStyle = "gray";
        ctx.fillRect(0,0,cnv.width,1);
        ctx.fillRect(0,- Math.round(font.hhea.ascender *scale),cnv.width,1);
        ctx.fillRect(0,- Math.round(font.hhea.descender * scale),cnv.width,1);
    }
    ctx.scale(scale,-scale);
    
    if(iftext){
        font.pathToContext(path, ctx);  // setting color and calling fill() already in path
        ctx.fillStyle = self.color;
        ctx.fill();
    }

    if(ifpoint){
        drawOutline(font, path, ctx);
    }

    if(step === "step1"){
        self.coordinates = path.crds
        self.left = margin.left * getDPR()
        self.top = margin.top * getDPR() + Math.round(font.hhea.ascender * scale)
        self.scale = scale
    }
}

function drawWithFont(self, step){
    load(self, step, fontLoaded)
}

export  { drawWithFont }

