odoo.define('wt_office_hunddle.custom', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
	
	$(document).ready(function(){
		AOS.init();
		$("header .dropdown").hover(function(){
	        var dropdownMenu = $(this).children(".dropdown-menu");
	        if(dropdownMenu.is(":visible")){
	            dropdownMenu.parent().toggleClass("open");
	        }
	    });
	    $(".fullwidth-carousel").owlCarousel({
            autoplay: true,
            autoplayTimeout: 5000,
            loop: true,
            items: 1,
            dots: false,
            nav: true,
            navText: [
                '<i class="pe-7s-angle-left"></i>',
                '<i class="pe-7s-angle-right"></i>'
            ]
        });
        var windowHeight = $(window).height();
        $('.fullscreen').height(windowHeight); 
        var TM_countDownTimer = function() {
            var $clock = $('#clock');
            var endingdate = $clock.data("endingdate");
            $clock.countdown(endingdate, function(event) {
                var countdown_text = '' +
                    '<ul class="countdown-timer">' +
                    '<li>%D <span>Days</span></li>' +
                    '<li>%H <span>Hours</span></li>' +
                    '<li>%M <span>Minutes</span></li>' +
                    '<li>%S <span>Seconds</span></li>' +
                    '</ul>';
                $(this).html(event.strftime(countdown_text));
            });
        }
        // $.stellar({
        //         horizontalScrolling: false,
        //         responsive: true,
        // });
        var t = setTimeout(function() {
        	TM_countDownTimer();
        },0); 
        
	});
	
});