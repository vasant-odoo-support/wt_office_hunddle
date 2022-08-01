odoo.define('wt_office_hunddle.DesignTools', function (require) {
'use strict';

	var core = require('web.core');
	var publicWidget = require('web.public.widget');
	var ajax = require('web.ajax');

	publicWidget.registry.DesignTools = publicWidget.Widget.extend({
	    selector: '#design_tool_wrap',
	    events: {
	        'click #save-design': '_saveDesign',
	        'click #confirm_order': '_confirmOrder',
	    },
	    start: function () {
	        return this._super.apply(this, arguments);
	    },
	    _saveDesign: function(ev){
	    	this.saveImage(ev);
	    },
      	saveImage: function(e) {
		  this.save_front()
	      this.save_back()
        },
        save_front: function(){
        	$("#imageFront").addClass("active");
        	var status = $("#imageFront").click()
        	var node2 = document.getElementById("DesignImgFront");
        	html2canvas(node2,{allowTaint:true}).then((c) => {
		        var base64String = c.toDataURL("image/jpeg").split(';base64,')[1];
		        console.log(base64String);
	           	ajax.jsonRpc('/web/dataset/call_kw', 'call', {
				    'model': 'res.users',
				    'method': 'check_work',
				    'args': [],
				    'kwargs': {
				        'context': {'front-image': base64String},
				    }
				}).then(function (data) {
				    if(data){
				    	return true
				    }
				});
			});
        },
        save_back: function(){
        	var el = $("#imageBack")
        	el.addClass("active");
        	el.click()
        	var node1 = document.getElementById("DesignImgBack");
          	console.log("-------- node 1 ===== ", node1)
          	html2canvas(node1,{allowTaint:true}).then((c) => {
				var base64String = c.toDataURL("image/jpeg").split(';base64,')[1];
				console.log(base64String);
				ajax.jsonRpc('/web/dataset/call_kw', 'call', {
				    'model': 'res.users',
				    'method': 'check_work',
				    'args': [],
				    'kwargs': {
				        'context': {'back-image': base64String},
				    }
				}).then(function (data) {
				    console.log("---------data ----- ", data)
				    if(data){
				    	location.reload()
				    }
				});
          	});
        },
        _confirmOrder: function(e) {
        	var front = $('#front').is(':checked')
        	var back = $('#back').is(':checked')
        	var product = $('#front_image').attr('data-id')
        	var description = $('#design-desc').val()
        	var quantity = $('#quantity').val()
        	ajax.jsonRpc('/web/dataset/call_kw', 'call', {
			    'model': 'project.task',
			    'method': 'create_design_tasks',
			    'args': [{'front_image': front, 'back_image': back, 'design_product_id': product, 'description': description, 'quantity': quantity}],
			    'kwargs': {
			        'context': {},
			    }
			}).then(function (data) {
			    // Do something here
			    location.href = "/thankyou"
			});
        }
	});
});
