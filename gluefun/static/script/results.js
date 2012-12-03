/**
 * jQuery ready handler.
 */
$(function() {

    /**
     * Function to kick-off polling the server for results. If results are not
     * yet available, this function calls itself recursively via a timeout
     * until they are.
     */
    var get_results = function() {

        $.get('/results/', null,
              function(data) {
                  if (data) {
                      if (data.task_completion === 100) {
                          $('#working').hide();
                          $('#complete').fadeIn('slow');
                          $('#results').html(data.html);
                      } else {
                          var width = 'width: ' + data.task_completion + '%;';
                          $('.bar').attr('style', width);
                          setTimeout(
                              function() {
                                  get_results();
                              },
                              5000);
                      }
                  }
              },
              'json');
    }

    get_results();

});
