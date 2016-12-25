$(document).ready(function() {
  // alert('hello');

  $("#checkAllBoxes").click(function(){
    var checked_status = this.checked;
    $("input[name='reflag']").each(function(){
      this.checked = checked_status;
    });
  });

  $("#masterFlag").change(function(){
    var masterFlagValue = $(this).val() - 1;
    $("select[name='personFlag']").each(function(){
      this.selectedIndex = masterFlagValue;
    })
    console.log('masterFlagValue');
  });


  // Toggles display/hide of sidebar on small canvases
  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });


  // quick search logic/ajax call
  function executeQuickSearch(searchString){
    $.ajax({
      url: '/crm/quick_search/',
      type: 'POST',
      data: {'search_terms': searchString,},
      success: function(data){
        $('#main-panel').html(data);
      }
    });
  }


  // Execute quick search when search button clicked
  $('body').on('click', '#quick-search', function(){
    var searchTerms = $('#quick-search-term').val().trim();
    if (searchTerms.length > 0) {
      executeQuickSearch(searchTerms);
    };
  })


  // Execute quick search when enter pressed in quick search field
  $('body').on('keyup', '#quick-search-term', function(event){
    if (event.keyCode == 13) {
      var searchTerms = $(this).val().trim();
      if (searchTerms.length > 0) {
        executeQuickSearch(searchTerms);
      };
    };
  })

});
