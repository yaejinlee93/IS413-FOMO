$(function(context){

  return function(){

    $('.img_item').mouseenter(function(){

          var ImgSrc = $(this).attr('src');

          $('.prod_img').attr('src', ImgSrc);
    });

  }
}(DMP_CONTEXT.get()))
