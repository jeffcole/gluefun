/**
 * spin.js jQuery plugin which provides the ability to call .spin() on a jQuery
 * object.
 */
$.fn.spin = function(opts) {
  this.each(function() {
    var $this = $(this),
        data = $this.data();

    if (data.spinner) {
      data.spinner.stop();
      delete data.spinner;
    }
    if (opts !== false) {
      data.spinner = new Spinner($.extend({color: $this.css('color')}, opts)).spin(this);
    }
  });
  return this;
};

/**
 * spin.js options.
 */
var opts = {
  lines: 13, // The number of lines to draw
  length: 7, // The length of each line
  width: 4, // The line thickness
  radius: 10, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  color: '#000', // #rgb or #rrggbb
  speed: 1, // Rounds per second
  trail: 60, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'spinner', // The CSS class to assign to the spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: 'auto', // Top position relative to parent in px
  left: 'auto' // Left position relative to parent in px
};

/**
 * jQuery ready handler.
 */
$(function() {

    $('#complete').hide();

    /**
     * Function to kick-off polling the server for results. If results are not
     * yet available, this function calls itself recursively via a timeout
     * until they are.
     */
    var get_results = function() {

        $('#spinner').spin();
        
        $.get('/results/', null,
              function(data) {
                  if (data && (data !== 'None')) {
                      $('#working').hide();
                      $('#complete').fadeIn('slow');
                      $('#results').html(data);
                  } else {
                      setTimeout(
                          function() {
                              get_results();
                          },
                          5000);
                  }
              },
              'html');
    }

    get_results();

});
