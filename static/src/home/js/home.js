odoo.define('wt_office_hunddle.Homepage', function (require) {
'use strict';

	var core = require('web.core');

	var publicWidget = require('web.public.widget');

	publicWidget.registry.Homepage = publicWidget.Widget.extend({
	    selector: '.homepage_wrap',
	    start: function () {
	    	$('.owl-carousel').owlCarousel({
                    loop: true,
                    margin: 10,
                    responsiveClass: true,
                    responsive: {
                      0: {
                      items: 1,
                      nav: false
                      },
                      600: {
                      items: 1,
                      nav: true
                      },
                      1000: {
                      items: 3,
                      nav: false,
                      loop: false,
                      margin: 20
                      }
                    }
            });
	        return this._super.apply(this, arguments);
	    }
	});
	
});