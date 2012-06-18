


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
$(document).ajaxStart(function(){
  $('#curr_position').val('Moving stage...')
});



