
$(document).ready(function(){
	$("#cus-nav-toggle-btn").on("click", function(){
		$(".cus-main-navigation").slideToggle({
			duration:200,
			start: function() {
			    $(this).css('display','flex');
			  }
		});
	});

	$(window).scroll(function(){
  		if($(document).scrollTop() > 5)
		{
			$(".cus-sticky-top").css({"padding":"0"});
			$(".cus-img-logo").css({"width":"250px", "height": "50px"});   
		}
		if($(document).scrollTop() < 5){
			$(".cus-sticky-top").css({"padding":""});
			$(".cus-img-logo").css({"width":"", "height": ""});   
		}
	});
});