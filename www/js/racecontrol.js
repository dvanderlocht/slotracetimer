/**
* Audio
*
*/

var beepElement, beepUrl;
var audio0, audio1, audio2, audio3, audio4, audio5, audioYellowFlag, audioRaceOver, audioAirhorn;

$(document).ready(function() {                

     beepElement = document.createElement('audio');
     beepUrl = 'http://'+window.location.host+'/sounds/beep-07.mp3'; 
     beepElement.setAttribute('src', beepUrl);
     
     audio0 = document.createElement('audio');
     audio1 = document.createElement('audio');
     audio2 = document.createElement('audio');
     audio3 = document.createElement('audio');
     audio4 = document.createElement('audio');
     audio5 = document.createElement('audio');
     audioYellowFlag = document.createElement('audio');
     audioRaceOver = document.createElement('audio');
     audioAirhorn = document.createElement('audio');
     audio0.setAttribute('src', 'http://'+window.location.host+'/sounds/woman_0.wav');
     audio1.setAttribute('src', 'http://'+window.location.host+'/sounds/woman_1.wav');
     audio2.setAttribute('src', 'http://'+window.location.host+'/sounds/woman_2.wav');
     audio3.setAttribute('src', 'http://'+window.location.host+'/sounds/woman_3.wav');
     audio4.setAttribute('src', 'http://'+window.location.host+'/sounds/woman_4.wav');
     audio5.setAttribute('src', 'http://'+window.location.host+'/sounds/woman_5.wav');    
     audioYellowFlag.setAttribute('src', 'http://'+window.location.host+'/sounds/yellowflag_w.wav');
     audioRaceOver.setAttribute('src', 'http://'+window.location.host+'/sounds/raceover_w.wav');      
     audioAirhorn.setAttribute('src', 'http://'+window.location.host+'/sounds/horn-trimmed.mp3');
 });   


/**
* Websocket for comms
* 
*/  
var ws = {};
var RASPBERRYPI_IP = window.location.host;
var RASPBERRYPI_PORT = "8888";

var FRAME_STATUS = 0;
var FRAME_LAP = 1;
var FRAME_POSITIONS = 2;
var FRAME_COUNTDOWN = 3;

function startWebsocket() {
    
    if(ws.readyState === undefined || ws.readyState > 1) {  
         ws = new WebSocket("ws://"+RASPBERRYPI_IP+":"+RASPBERRYPI_PORT+"/ws");   
    }   

    ws.onmessage = function(evt) {
        handleFrame(evt.data);
    };
    
    ws.onclose = function(evt) {
        //$("#wsStatusIcon").removeClass( "wsStatusIcon-connected" ).addClass( "wsStatusIcon" );
    };
    
    ws.onopen = function(evt) {
        //$("#wsStatusIcon").removeClass( "wsStatusIcon" ).addClass( "wsStatusIcon-connected" );
    };   
    
    ws.onerror = function(evt) {
        //$("#wsStatusIcon").removeClass( "wsStatusIcon-connected" ).addClass( "wsStatusIcon" );
    };       
}


/**
*
*
*/

var RACE_STATE_OFF = 0;     
var RACE_STATE_PRE_START = 1;
var RACE_STATE_START = 2;
var RACE_STATE_RACE = 3;
var RACE_STATE_FINISH = 4;
var RACE_STATE_YELLOW_FLAG = 5;
var RACE_STATE_FALSE_START = 6;

var raceLapCount = 0;

var lane1_bgcolor = "bg-primary";
var lane2_bgcolor = "bg-danger";


function resetView() {  
    $(".startlight-red1").attr("src", "./images/DomeLight_offRed-100px.png");    
    $(".startlight-red2").attr("src", "./images/DomeLight_offRed-100px.png");
    $(".startlight-red3").attr("src", "./images/DomeLight_offRed-100px.png");
    $(".startlight-red4").attr("src", "./images/DomeLight_offRed-100px.png");
    $(".startlight-red5").attr("src", "./images/DomeLight_offRed-100px.png");
    $(".startlight-green").attr("src", "./images/DomeLight_offGreen-100px.png");
    $(".startlight-yellow").attr("src", "./images/DomeLight_offYellow-100px.png");
    //$("#lane1-laps tbody").empty();
    //$("#lane2-laps tbody").empty();
    //$("#race-positions tbody").empty(); 
}


function handleFrame(data) {
    var position, lane, lap, time;

    var pos1_lane, pos1_lap, pos1_best_lap, pos1_best_lap_time, pos1_time, pos1_total_lap_time, pos1_race_percentage, pos1_lapseconds, pos1_bestlapseconds;   
    var pos2_lane, pos2_lap, pos2_best_lap, pos2_best_lap_time, pos2_time, pos2_total_lap_time, pos2_race_percentage, pos2_lapseconds, pos2_bestlapseconds, pos2_diff_lapcount;    
    
    var objFrame = JSON.parse(data);
        
    //var position, lane, lap, time, best_lap, best_lap_time, total_lap_time;
    //var a, b, lapseconds, bestlapseconds;
    //var lap_percentage;
    //var diff = "";
    
        
    // general info frame
    if (objFrame.frame_type === FRAME_STATUS) {        
        switch(objFrame.race_state) {
            case RACE_STATE_OFF:
                $(".racecontrol-race-state").html("Off");
                resetView();
                break;
                
            case RACE_STATE_PRE_START:
                // clear previous laps in view
                $("#lane1-laps tbody").empty();
                $("#lane2-laps tbody").empty();
                $("#race-positions tbody").empty();
                
                $(".racecontrol-race-state").html("Place cars");
                $(".startlight-red1").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red2").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red3").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red4").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red5").attr("src", "./images/DomeLight_onRed-100px.png");
                break;
                
            case RACE_STATE_START:                
                $(".racecontrol-race-state").html("Start");
                $(".startlight-red1").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red2").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red3").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red4").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red5").attr("src", "./images/DomeLight_offRed-100px.png");    
                $(".startlight-green").attr("src", "./images/DomeLight_offGreen-100px.png");
                $(".startlight-yellow").attr("src", "./images/DomeLight_offYellow-100px.png");            
                break;
                
            case RACE_STATE_RACE:
                //audioAirhorn.play();
                //audio0.play();                
                $(".racecontrol-race-state").html("Race in progress");
                $(".startlight-red1").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red2").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red3").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red4").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red5").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-green").attr("src", "./images/DomeLight_onGreen-100px.png");
                $(".startlight-yellow").attr("src", "./images/DomeLight_offYellow-100px.png");
                break;
                
            case RACE_STATE_FINISH:
                audioRaceOver.play();
                $(".racecontrol-race-state").html("Finished");
                $(".startlight-red1").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red2").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red3").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red4").attr("src", "./images/DomeLight_onRed-100px.png");
                $(".startlight-red5").attr("src", "./images/DomeLight_onRed-100px.png"); 
                $(".startlight-green").attr("src", "./images/DomeLight_offGreen-100px.png");
                $(".startlight-yellow").attr("src", "./images/DomeLight_offYellow-100px.png");  
                break;    
                       
            case RACE_STATE_YELLOW_FLAG:
                audioYellowFlag.play();
                $(".racecontrol-race-state").html("Yellow flag!");
                $(".startlight-red1").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red2").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red3").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red4").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-red5").attr("src", "./images/DomeLight_offRed-100px.png");
                $(".startlight-green").attr("src", "./images/DomeLight_offGreen-100px.png");
                $(".startlight-yellow").attr("src", "./images/DomeLight_onYellow-100px.png");                
                break;  
        }
    
        if (objFrame.race_laps) {
            raceLapCount = objFrame.race_laps;
            $(".racecontrol-race-laps").html(raceLapCount + " laps");
        }      
    }     
        
    // lap time frame
    else if (objFrame.frame_type === FRAME_LAP) {                
                
        lane = objFrame.lane;        
        lap = objFrame.lap;        
        time = objFrame.time;
        position = objFrame.position;
        
        var a = time.split(':'); // split it at the colons
        var lapseconds = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);
        
        // beep
        beepElement.play();
        
        // add to table view
        if (lane == 1) { 
            $("#lane1-laps tbody").prepend("<tr><td>"+lap+"</td><td>"+lapseconds.toFixed(3)+"</td><td>"+position+"</td></tr>");
        }
        else if (lane == 2) {
            $("#lane2-laps tbody").prepend("<tr><td>"+lap+"</td><td>"+lapseconds.toFixed(3)+"</td><td>"+position+"</td></tr>");            
        }
        
    }
    
    // position info frame     
    else if (objFrame.positions) {        

        pos1_lane = objFrame.positions.position1.lane;
        pos1_lap = objFrame.positions.position1.lap;
        pos1_best_lap = objFrame.positions.position1.best_lap;
        pos1_best_lap_time = objFrame.positions.position1.best_lap_time;
        pos1_time = objFrame.positions.position1.time;
        pos1_total_lap_time = objFrame.positions.position1.total_lap_time.substring(0, objFrame.positions.position1.total_lap_time.length-3);    // strip last 3 characters 
        pos1_race_percentage = pos1_lap/(raceLapCount/100);
        
        var a1 = pos1_time.split(':'); // split it at the colons
        pos1_lapseconds = (+a1[0]) * 60 * 60 + (+a1[1]) * 60 + (+a1[2]);
        var b1 = pos1_best_lap_time.split(':'); // split it at the colons
        pos1_bestlapseconds = (+b1[0]) * 60 * 60 + (+b1[1]) * 60 + (+b1[2]);
        
        pos2_lane = objFrame.positions.position2.lane;
        pos2_lap = objFrame.positions.position2.lap;
        pos2_best_lap = objFrame.positions.position2.best_lap;
        pos2_best_lap_time = objFrame.positions.position2.best_lap_time;
        pos2_time = objFrame.positions.position2.time;
        pos2_total_lap_time = objFrame.positions.position2.total_lap_time.substring(0, objFrame.positions.position2.total_lap_time.length-3);    // strip last 3 characters;        
        pos2_race_percentage = pos2_lap/(raceLapCount/100);
        pos2_diff_lapcount = objFrame.positions.position2.diff_lapcount;

        var a2 = pos2_time.split(':'); // split it at the colons
        pos2_lapseconds = (+a2[0]) * 60 * 60 + (+a2[1]) * 60 + (+a2[2]);
        var b2 = pos2_best_lap_time.split(':'); // split it at the colons
        pos2_bestlapseconds = (+b2[0]) * 60 * 60 + (+b2[1]) * 60 + (+b2[2]);         
        

        var pos1_lane_bg = "";
        var pos2_lane_bg = "";
               
        if (pos1_lane == 1) {                   // first position lane bg color 
            pos1_lane_bg = lane1_bgcolor;
        } else {
            pos1_lane_bg = lane2_bgcolor;
        }  
                    
        if (pos2_lane == 1) {                   // second position lane bg color  
            pos2_lane_bg = lane1_bgcolor;
        } else {
            pos2_lane_bg = lane2_bgcolor;
        }    
        
        // refresh view
        $("#race-position-1").remove();
        $("#race-position-2").remove();
        $("#race-positions tbody").append("<tr id=\"race-position-1\"><td>1</td><td class="+pos1_lane_bg+">Slot "+pos1_lane+"</td><td>"+pos1_lap+"<br><h2><progress class=\"progBarLaps\" id=\"progBar1\" value=\""+pos1_lap+"\" max=\""+raceLapCount+"\"></progress>&nbsp;&nbsp;"+pos1_race_percentage.toFixed(2)+"%</h2></td><td>"+pos1_lapseconds.toFixed(3)+"<br /><h2>Total: "+pos1_total_lap_time+"</h2></td><td></td><td>"+pos1_bestlapseconds.toFixed(3)+"<br /><h2>(lap "+pos1_best_lap+")</h2></td></tr>");
        $("#race-positions tbody").append("<tr id=\"race-position-2\"><td>2</td><td class="+pos2_lane_bg+">Slot "+pos2_lane+"</td><td>"+pos2_lap+"<br><h2><progress class=\"progBarLaps\" id=\"progBar1\" value=\""+pos2_lap+"\" max=\""+raceLapCount+"\"></progress>&nbsp;&nbsp;"+pos2_race_percentage.toFixed(2)+"%</h2></td><td>"+pos2_lapseconds.toFixed(3)+"<br /><h2>Total: "+pos2_total_lap_time+"</h2></td><td>+"+pos2_diff_lapcount+" <h2>lap(s)</h2></td><td>"+pos2_bestlapseconds.toFixed(3)+"<br /><h2>(lap "+pos2_best_lap+")</h2></td></tr>");        
    }
    
    // countdown frame
    else if (objFrame.frame_type === FRAME_COUNTDOWN) {
        if (objFrame.count_down == 5) {
            $(".startlight-red1").attr("src", "./images/DomeLight_onRed-100px.png");
            audio5.play();
        }
        else if (objFrame.count_down == 4) {
            $(".startlight-red1").attr("src", "./images/DomeLight_onRed-100px.png");
            $(".startlight-red2").attr("src", "./images/DomeLight_onRed-100px.png");
            audio4.play();
        } 
        else if (objFrame.count_down == 3) {
            $(".startlight-red1").attr("src", "./images/DomeLight_onRed-100px.png");
            $(".startlight-red2").attr("src", "./images/DomeLight_onRed-100px.png");            
            $(".startlight-red3").attr("src", "./images/DomeLight_onRed-100px.png");
            audio3.play();
        }
        else if (objFrame.count_down == 2) {
            $(".startlight-red1").attr("src", "./images/DomeLight_onRed-100px.png");
            $(".startlight-red2").attr("src", "./images/DomeLight_onRed-100px.png");            
            $(".startlight-red3").attr("src", "./images/DomeLight_onRed-100px.png");            
            $(".startlight-red4").attr("src", "./images/DomeLight_onRed-100px.png");
            audio2.play();
        } 
        else if (objFrame.count_down == 1) { 
            $(".startlight-red1").attr("src", "./images/DomeLight_onRed-100px.png");
            $(".startlight-red2").attr("src", "./images/DomeLight_onRed-100px.png");            
            $(".startlight-red3").attr("src", "./images/DomeLight_onRed-100px.png");            
            $(".startlight-red4").attr("src", "./images/DomeLight_onRed-100px.png");
            $(".startlight-red5").attr("src", "./images/DomeLight_onRed-100px.png");
            audio1.play();
        }
        else if (objFrame.count_down === 0) {
            audioAirhorn.play();
            audio0.play();            
        }
    }    
}