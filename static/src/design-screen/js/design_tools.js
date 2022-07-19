odoo.define('wt_office_hunddle.DesignTools', function (require) {
'use strict';

	var core = require('web.core');
	var publicWidget = require('web.public.widget');
	var ajax = require('web.ajax');

	publicWidget.registry.DesignTools = publicWidget.Widget.extend({
	    selector: '#design_tool_wrap',
	    events: {
	        'click #save-design': '_saveDesign',
	    },
	    start: function () {
	        return this._super.apply(this, arguments);
	    },
	    _saveDesign: function(ev){
	    	console.log("------------ called -----")
	    	console.log("============")
	        var status = $("#imageBack").hasClass("active");
	        if (status == true) {
	          this.saveImage("b");
	        } else {
	          this.saveImage("a");
	        }
	    },
      	saveImage: function(e) {
	        if (e == "b") {
	          var node = document.getElementById("DesignImgBack");
	          html2canvas(node,{allowTaint:true}).then((c) => {
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
				    // Do something here
				    location.reload()
				});
	            // $("body").append(c);
	          });
	        } else if (e == "a") {
	          var node = document.getElementById("DesignImgFront");
	          html2canvas(node,{allowTaint:true}).then((c) => {
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
				    // Do something here
				    location.reload()
				});
	           // $("body").append(c);
	          });
	        }
        }
	});
});