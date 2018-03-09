console.log(DMP_CONTEXT.get())
$(function(context) {
    return function () {
      var container = $('#catalog_container')

      container.load('/catalog/index.products/' +  context.cid + '/')

      var pnum = 1
      var pmax = context.num_pages

      $('#previous_page').click(function(){
        $('#catalog_container').load('/catalog/index.products/' +  context.cid + '/' + pnum)


        if (pnum > 1) {
          pnum--
          $('#catalog_container').load('/catalog/index.products/' +  context.cid + '/' + pnum)
          $('#page_number').text(pnum)
        }
      })

      $('#next_page').click(function(){

        if (pnum < pmax) {
          pnum += 1
          $('#catalog_container').load('/catalog/index.products/' +  context.cid + '/' + pnum)
          $('#page_number').text(pnum)
        }
      })
    }
}(DMP_CONTEXT.get()));
