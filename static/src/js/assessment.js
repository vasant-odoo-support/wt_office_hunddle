odoo.define('wt_office_hunddle.assessment', function (require) {
'use strict';

	var core = require('web.core');

	var publicWidget = require('web.public.widget');

	publicWidget.registry.AssessmentOffice = publicWidget.Widget.extend({
	    selector: '.assessment_hunddle_main_cl',
	    events: {
	        'click .nexpev #prevBtn': '_onPrevAssess',
	        'click .nexpev #nextBtn': '_onNextAssess',	        
	    },
	    start: function () {
	        return this._super.apply(this, arguments);
	    },
	    _onPrevAssess: function(ev){
	    	if($(this.$el).find('form .tab.active').prev().length && $(this.$el).find('form .tab.active').prev().hasClass('tab')){
    			var sek = $(this.$el).find('form .tab.active').prev();
    			sek.addClass('active');
    			sek.next().removeClass('active');
    			this.$el.find('.prog .progress_step_cl.active').removeClass('active_done');
    			var prog = this.$el.find('.prog .progress_step_cl.active').prev();
    			prog.addClass('active');
    			prog.next().removeClass('active');
    			this.$el.find('.prog .progress_step_cl.active').removeClass('active_done');
    			$(this.$el).find('.nexpev #nextBtn').text('Next');
    		}
	    },
	    _onNextAssess: function(ev){

	    	var d = this.validateForm();
	    	if(d){
	    		if($(this.$el).find('form .tab.active').next().length && $(this.$el).find('form .tab.active').next().hasClass('tab')){
	    			var sek = $(this.$el).find('form .tab.active').next();
	    			sek.addClass('active');
	    			sek.prev().removeClass('active');
	    			this.$el.find('.prog .progress_step_cl.active').addClass('active_done');
	    			var prog = this.$el.find('.prog .progress_step_cl.active').next();
	    			prog.addClass('active');
	    			prog.prev().removeClass('active');
	    			if(!$(this.$el).find('form .tab.active').next().hasClass('tab')){
	    				$(this.$el).find('.nexpev #nextBtn').text('Submit');
	    			}
	    			this.$el.find('.prog .progress_step_cl')
	    		}else{
	    			this.$el.find('form').submit();
	    		}
	    	}
	    },

	    validateForm: function(){
	    	var x, y, i, valid = true;
		      y = $(this.$el).find('form .tab.active input');
		      _.each(y, function(el){
		      	if( $(el).prop( 'required' )){
		      		if($(el).val() == ""){
		      			valid = false;
		      			$(el).addClass('invalid');
		      		}
		      	}
		      });
		    return valid;
			}

	});
	publicWidget.registry.AssessmentOutput = publicWidget.Widget.extend({
		selector: '.assessment_output',
	    events: {
	    	'click .accordion': 'accoding_toggle_bar'
	    },
	    start: function () {
	    	this.$el.find('.progress-pie-chart').each(function(){
              var $ppc = $(this),
                  percent = parseInt($ppc.data('percent')),
                  deg = 360*percent/100;
              if (percent > 50) {
                  $ppc.addClass('gt-50');
              }
              if (percent <= 49) {
                  $ppc.addClass('red');
              } else if (percent >= 50 && percent <= 70) {
                  $ppc.addClass('orange');
              } else if (percent >= 71 && percent <= 100) {
                  $ppc.addClass('green');
              }

              $ppc.find('.ppc-progress-fill').css('transform','rotate('+ deg +'deg)');
              $ppc.find('.ppc-percents span').html('<cite>'+percent+'</cite>'+'%');
          });

	      return this._super.apply(this, arguments);
	    },
	    accoding_toggle_bar: function(ev){
	    	$(ev.currentTarget).toggleClass("active");
            var panel = $(ev.currentTarget).next()[0];
            if (panel.style.maxHeight) {
              panel.style.maxHeight = null;
            } else {
              panel.style.maxHeight = panel.scrollHeight + "px";
            }
	    }
	});
	
});