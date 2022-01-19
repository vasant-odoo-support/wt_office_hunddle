odoo.define('wt_office_hunddle.printing_products', function (require) {
'use strict';

	var core = require('web.core');
	var publicWidget = require('web.public.widget');

	var slideIndex = 0;
	var global_ref = false
	publicWidget.registry.PrintingProducts = publicWidget.Widget.extend({
	    selector: '#printing_products',

	    events: {
	        // 'click #prevBtn': '_onPrevAssess',
	        // 'click #nextBtn': '_onNextAssess',	        
	    },
	    start: function () {
	    	var self = this;
	    	global_ref = self;
			self.showSlides();
	        return this._super.apply(this, arguments);
	    },
	    showSlides: function() {
	      var self = this;
	      var i;
		  var slides = $(".mySlides");
		  for (i = 0; i < slides.length; i++) {
		    slides[i].style.display = "none";
		  }
		  slideIndex++;
		  if (slideIndex > slides.length) {slideIndex = 1}
		  slides[slideIndex-1].style.display = "block";
		  setTimeout(global_ref.showSlides, 3000); // Change image every 2 seconds
	    }
	});
});