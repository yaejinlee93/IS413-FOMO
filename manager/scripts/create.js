$(document).ready(function() {
       // JQuery code to be added in here.
       $("#id_type").on('change', function() {
         if(this.value === "BulkProduct")
         {
           $(".RentalProduct").closest('p').hide();
           $(".IndividualProduct").closest('p').hide();
           $(".BulkProduct").closest('p').show();
         }
         else if(this.value === "IndividualProduct")
         {
           $(".BulkProduct").closest('p').hide();
           $(".RentalProduct").closest('p').hide();
           $(".IndividualProduct").closest('p').show();
         }
         else if(this.value === "RentalProduct")
         {
           $(".BulkProduct").closest('p').hide();
           $(".IndividualProduct").closest('p').hide();
           $(".RentalProduct").closest('p').show();
         }
       });

       $('#id_type').on('focus', function(){
         if(this.value === "BulkProduct")
         {
           $(".RentalProduct").closest('p').hide();
           $(".IndividualProduct").closest('p').hide();
           $(".BulkProduct").closest('p').show();
         }
         else if(this.value === "IndividualProduct")
         {
           $(".BulkProduct").closest('p').hide();
           $(".RentalProduct").closest('p').hide();
           $(".IndividualProduct").closest('p').show();
         }
         else if(this.value === "RentalProduct")
         {
           $(".BulkProduct").closest('p').hide();
           $(".IndividualProduct").closest('p').hide();
           $(".RentalProduct").closest('p').show();
         }
       });

       $('#id_type').focus();
   })
