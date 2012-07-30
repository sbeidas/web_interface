
function saveImage(id){
    
    var oCanvas=$('#'+id).children('canvas')
    //var oCanvas2=$('#'+id).children('div').children('canvas')
    

    

      w= oCanvas[0].width;
      h= oCanvas[0].height;



      var newCanvas = $('<canvas id="tempcanvas" />').attr('width',w).attr('height',h)[0];
      var newContext =newCanvas.getContext("2d");   
      $(oCanvas).each(function() {
        newContext.drawImage(this, 0, 0);
      });
      //$(oCanvas2).each(function() {
       // newContext.drawImage(this, 0, 0);
      //});
      
      dataURL= newCanvas.toDataURL("image/png"); // Base64 encoded data url string
       return(dataURL)

    
}
var pol_experiment={
    scan: function() {
        $.ajax({
        url: ' /polScan ',
        cache: 'false',
        data: {
            'input_pol_start': $('#input_pol_start').val(),
            'input_pol_end': $('#input_pol_end').val(),
            'input_pol_step': $('#input_pol_step').val(),
            
            'output_pol_start': $('#output_pol_start').val(),
            'output_pol_end': $('#output_pol_end').val(),
            'output_pol_step': $('#output_pol_step').val()
        },
        type: 'post',
        async: 'false',
            success: function(data) {
            date=new Date().getTime()
            divName='chart'+ date
            $('#plots').append('<div style="width: 1750px" id='+divName+'>')
            var plot1 = $.jqplot('chart'+ date, [data], {
                legend: {show:false},
                axes:{
                  xaxis:{
                  tickOptions:{
                    
                    angle: -30
                  },
                  tickRenderer:$.jqplot.CanvasAxisTickRenderer,
                    label:'Angle', 
                  labelOptions:{
                    fontFamily:'Helvetica',
                    fontSize: '12pt'
                  },
                  labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                  }, 
                  yaxis:{
                    
                    renderer:$.jqplot.LogAxisRenderer,
                    tickOptions:{
 
                        labelPosition: 'middle', 
                        angle:-30
                    },
                    tickRenderer:$.jqplot.CanvasAxisTickRenderer,
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                    labelOptions:{
                        fontFamily:'Helvetica',
                        fontSize: '12pt'
                    },
                    label:''
                  }
                },
                highlighter: {
                    show: true ,    
                    sizeAdjust: 10,
      
                },
                cursor:{
                show: true, 
                zoom: true
                } ,
            });
             href="'"+saveImage(divName)+"'"
             $('#'+divName).append("</div><a  target='_blank'  href="+href+" style='position: relative;margin-right:-150px; margin-top:100px;float:right;' >"+"<input type='button' value='Save plot as Image' "+"</a>")
             
             
            },
            
            error: function() {
                    console.log();
            },
        });
    },
    
    stopScan: function() {
        $.ajax({
        url: ' /stopPolScan ',
        cache: 'false',
        data: {

        },
        type: 'post',
        async: 'false',
            success: function(data) {
            
            },
            error: function() {
                    console.log();
            },
        });
    },

    
   
}
var sample_rotation={
    anglescan: function() {
        $.ajax({
        url: ' /anglescan ',
        cache: 'false',
        data: {
            'sample_rotation_start': $('#sample_rotation_start').val(),
            'sample_rotation_end': $('#sample_rotation_end').val(),
            'sample_rotation_velocity': $('#sample_rotation_velocity').val()
        },
        type: 'post',
        async: 'false',
            success: function(data) {

            $('#curr_position').val(data)
            },
            error: function() {
                    console.log();
            },
        });
    },
    move_sample_stage: function() {
        $.ajax({
        url: ' /movesamplestage ',
        cache: 'false',
        data: {
            'move_sample_stage': angle,
        },
        type: 'post',
        async: 'false',
            success: function(data) {

            $('#curr_position').val(data)
            },
            error: function() {
                    console.log();
            },
        });
    }
    
   
}

var liquid_handler={
    serialDilute: function() {
        $.ajax({
        url: ' /serialDilution ',
        cache: 'false',
        data: {
            'max_conc': $('#max_conc').val(),
            'min_conc': $('#min_conc').val(),
            'sample_count': $('#sample_count').val()
        },
        type: 'post',
        async: 'false',
            success: function(data) {

             alert('Great Success')
            },
            error: function() {
                    console.log();
            },
        });
    },
        prepareSample: function() {
        $.ajax({
        url: ' /serialDilutionPrepareSample ',
        cache: 'false',
        data: {

        },
        type: 'post',
        async: 'false',
            success: function(data) {

             alert('Great Success')
            },
            error: function() {
                    console.log();
            },
        });
    },
       
}



$(document).ready(function() {

    if (typeof console == "undefined") {
        console = { log: function() {} };
    }

    // on the main page load we show the splash screen 
    // and register start and highscores for clicks

    $('.sample_rotation_scan').click( function() {

            sample_rotation.anglescan();
    });
    $('.move_minus_15').click( function() {
            angle=parseInt($('#curr_position').val())-15
            sample_rotation.move_sample_stage( );
    });
    $('.move_plus_15').click( function() {
            angle=parseInt($('#curr_position').val())+15
            sample_rotation.move_sample_stage( );
    });
    $('.serial_delution_submit').click( function() {

        liquid_handler.serialDilute( );
    });
        $('.serial_delution_prepare_sample').click( function() {

        liquid_handler.prepareSample( );
    });
        $('.pol_scan_submit').click( function() {
        
        pol_experiment.scan();
    });
        $('.pol_scan_stop').click( function() {

        pol_experiment.stopScan( );
    });
});


  /**  $(document).ready(function() {

  // Setup the ajax indicator
  $('body').append('<div id="ajaxBusy"><p><img src="devices/static/images/loading.gif"></p></div>');

  $('#ajaxBusy').css({
    display:"none",
    margin:"0px",
    paddingLeft:"0px",
    paddingRight:"0px",
    paddingTop:"0px",
    paddingBottom:"0px",
    position:"absolute",
    right:"3px",
    top:"3px",
     width:"auto"
  });
});
**/
// Ajax activity indicator bound to ajax start/stop document events

$(document).ajaxStop(function(){
    $('#ajaxBusy').hide();;
    
  
});

$(document).ajaxStart(function(){

    $('#ajaxBusy').show();
  
});






