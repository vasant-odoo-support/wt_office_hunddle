odoo.define('wt_office_hunddle.Homepage', function (require) {
'use strict';

	var core = require('web.core');

	var publicWidget = require('web.public.widget');

	publicWidget.registry.Homepage = publicWidget.Widget.extend({
	    selector: '.homepage_wrap',
	    start: function () {
	    	$('.owl-carousel').owlCarousel({
            loop: true,
            center: true,
            items: 3,
            margin: 30,
            autoplay: true,
            dots:true,
            nav:false,
            autoplayTimeout: 1500,
            smartSpeed: 350,
            responsive: {
              0: {
                items: 1
              },
              768: {
                items: 2
              },
              1170: {
                items: 3
              }
            }
          });
	        return this._super.apply(this, arguments);
	    }
	});
	
});