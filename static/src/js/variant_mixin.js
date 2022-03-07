odoo.define('wt_office_hunddle.VariantMixin', function (require) {
'use strict';
    
    var ajax = require('web.ajax');
    var core = require('web.core');
    var utils = require('web.utils');
    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale');

    var _t = core._t;


    publicWidget.registry.WebsiteSale.include({

        init: function(){
            var self = this;
            var def = this._super.apply(this, arguments);
            if($('#qty-business-card option:selected').val()){
                $(".quantity").val($('#qty-business-card option:selected').val())
                $(".quantity").change()
            }
        },

        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);

            $("#qty-business-card").change(function(ev){
                console.log("========= $(this).val(); ====== ", $(this).val())
                $(".quantity").val($(this).val())
                $(".quantity").change()
            });

            $(".is_have_design").change(function(ev){
                ev.preventDefault();
                if($(this).val() == 'yes'){
                    console.log("--------- test ------- ")
                    // $("#photos_sample").empty();
                    $('.upload_button_front').show();
                    $('.upload_button_back').show();
                    $('.image_description').show();
                    $('.btn-send-design').show();
                    $('.upload-send-text').show();
                    $('.btn-letusdesign').hide();
                }
                if($(this).val() == 'no'){
                    // $("#photos_sample").empty();
                    console.log("--------- test no------- ")
                    $('.upload_button_front').hide();
                    $('.upload_button_back').hide();
                    $('.image_description').hide();
                    $('.btn-send-design').hide();
                    $('.upload-send-text').hide();
                    $('.btn-letusdesign').show();
                }
            });

            $("input[name$='customize_option']").change(function() {
                var customize_option = $(this).val();
                if(customize_option === 'image'){
                    $("#photos_sample").empty();
                    $('.image_description_1').show();
                    $('.image_description_2').hide();
                    $('.front_back_desc').show();
                    $('.image_description_3').hide();
                }
                if(customize_option === 'desc_image'){
                    // $("#photos_sample").empty();
                    $("#photos_front_back").empty();
                    $("#photo_front").empty();
                    $('.image_description_1').hide();
                    $('.image_description_2').show();
                    $('.image_description_3').show();
                    $('.front_back_desc').hide();
                }
                // console.log('___ customize_option : ', customize_option);
            });

            $("#show_customize").change(function(ev){
                ev.preventDefault();

                // console.log('___ this : ', this);
                // console.log('___ $(this).is(:checked) : ', $(this).is(':checked'));
                if($(this).is(':checked')){
                    // $('.image_data').show();
                    $('.image_description').show();
                }else{
                    // $('.image_data').hide();
                    $('.image_description').hide();
                }
            });


            $(".photo_front").change(function(ev){
                ev.preventDefault();

                $("#photos_front").empty();
                var cart_alert = $('#product_details').parent().find('#data_warning');
                cart_alert.empty();

                var self = this;
                var attach_count = this.files.length;
                var upload_files = [];

                for(let i=0;i<attach_count;i++){
                    let file = this.files[i];
                    let fr = new FileReader();
                    fr.onload = function () {
                        let data = fr.result;
                        $("#photos_front").append('<img src="'+data+'" class="img-thumbnail col-sm-6" style="width: 165px;height: auto !important;max-width: 165px !important;">');
                        data = data.split(',')[1];
                        let vals = {
                            name: self.files[i].name,
                            type: self.files[i].type,
                            data : data,
                        };
                        upload_files.push(vals);
                        let img_name = 'img_front_data_'+ i.toString();
                        let view = `<textarea  name="`+img_name+`"   class="`+img_name+`" 
                            style="display: none;" >`+JSON.stringify(vals);+`</textarea>`;
                        $('.image_data_div').append(view);
                    };
                    fr.readAsDataURL(file);
                }
                $('.custom_images').val(JSON.stringify(upload_files));
            });

            $(".photo_front_back").change(function(ev){
                ev.preventDefault();

                $("#photos_front_back").empty();
                var cart_alert = $('#product_details').parent().find('#data_warning');
                cart_alert.empty();

                var self = this;
                var attach_count = this.files.length;
                var upload_files = [];

                for(let i=0;i<attach_count;i++){
                    let file = this.files[i];
                    let fr = new FileReader();
                    fr.onload = function () {
                        let data = fr.result;
                        $("#photos_front_back").append('<img src="'+data+'" class="img-thumbnail col-sm-6" style="width: 165px;height: auto !important;max-width: 165px !important;">');
                        data = data.split(',')[1];
                        let vals = {
                            name: self.files[i].name,
                            type: self.files[i].type,
                            data : data,
                        };
                        upload_files.push(vals);
                        let img_name = 'img_front_back_data_'+ i.toString();
                        let view = `<textarea  name="`+img_name+`"   class="`+img_name+`" 
                            style="display: none;" >`+JSON.stringify(vals);+`</textarea>`;
                        $('.image_data_div').append(view);
                    };
                    fr.readAsDataURL(file);
                }
                $('.custom_images').val(JSON.stringify(upload_files));
            });

            $(".photo_sample").change(function(ev){
                ev.preventDefault();

                $("#photos_sample").empty();
                var cart_alert = $('#product_details').parent().find('#data_warning');
                cart_alert.empty();

                var self = this;
                var attach_count = this.files.length;
                var upload_files = [];

                for(let i=0;i<attach_count;i++){
                    let file = this.files[i];
                    let fr = new FileReader();
                    fr.onload = function () {
                        let data = fr.result;
                        let vals = {
                            name: self.files[i].name,
                            type: self.files[i].type,
                            data : data,
                        };
                        upload_files.push(vals);
                        let img_name = 'img_sample_data_'+ i.toString();
                        let view = `<textarea  name="`+img_name+`"   class="`+img_name+`" 
                            style="display: none;" >`+JSON.stringify(vals);+`</textarea>`;
                        $('.image_data_div').append(view);
                    };
                    fr.readAsDataURL(file);
                }
                $('.custom_images').val(JSON.stringify(upload_files));
            });

            return def;
        },

        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onClickAdd: function (ev) {
            ev.preventDefault();

            var cart_alert = $('#product_details').parent().find('#data_warning');
            cart_alert.empty();

            var $aSubmit = $(ev.currentTarget);
            var $form = $aSubmit.closest('form');
            var image = $form.find('#photo');
            var files = image && image.prop('files');

            var show_customize = $("#show_customize").is(':checked');

            // if(show_customize && files && files.length === 0){
            //     var cart_alert = $('#product_details').parent().find('#data_warning');
            //     cart_alert.append('<div class="alert alert-danger alert-dismissable" role="alert" id="data_warning">'+
            //         '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> Please upload atleast one image to continue.. </div>')
            //     return;
            // }

            var def = () => {
                this.isBuyNow = $(ev.currentTarget).attr('id') === 'buy_now';
                return this._handleAdd($(ev.currentTarget).closest('form'));
            };
            if ($('.js_add_cart_variants').children().length) {
                return this._getCombinationInfo(ev).then(() => {
                    return !$(ev.target).closest('.js_product').hasClass("css_not_available") ? def() : Promise.resolve();
                });
            }
            return def();
        },

    });

    return publicWidget.registry.WebsiteSaleOptions;

});


// if (files[x].size / 1024 / 1024 > 25) {
//                     this._alertDisplay(_t("File is too big. File size cannot exceed 25MB"));
//                     this._fileReset();
//                     // this._hidePreviewColumn();
//                     return;
//                 }