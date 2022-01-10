odoo.define('wt_office_hunddle.Captcha', function (require) {
'use strict';

  var core = require('web.core');
  var publicWidget = require('web.public.widget');
  var _t = core._t;
  publicWidget.registry.Captcha = publicWidget.Widget.extend({
      selector: '#sign-up',
      events: {
          'click .reload-btn': '_onClickReload',
          'click .check-btn': '_onCheckButton',        
      },
      start: function () {
          var self = this;
          self.getCaptcha()
          var def = this._super.apply(this, arguments);
          return def;
      },
      removeContent: function(){
        var statusTxt = $(".status-text");
        var inputField = $(".input-area input");
        var captcha = $('.captcha');
        inputField.value = "";
        captcha.innerText = "";
        statusTxt.css("display", "none");
      },
      getCaptcha: function(){
        var self = this;
        self.removeContent();
        var captcha = $('.captcha');
        var innerText = "";
        let allCharacters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                             'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd',
                             'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                             't', 'u', 'v', 'w', 'x', 'y', 'z', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
        for (let i = 0; i < 6; i++) { //getting 6 random characters from the array
          let randomCharacter = allCharacters[Math.floor(Math.random() * allCharacters.length)];
          if(captcha && randomCharacter){
            innerText += ` ${randomCharacter}`; //passing 6 random characters inside captcha innerText
            captcha.text(innerText)
          }
        }
      },
      _onClickReload: function(ev){
        ev.preventDefault();
        var self = this;
        self.getCaptcha(); //calling getCaptcha when the page open
      },

      _onCheckButton: function(ev){
        var self = this;
        ev.preventDefault(); //preventing button from it's default behaviour
        var statusTxt = $(".status-text");
        var inputField = $(".input-area input");
        var captcha = $('.captcha');
        statusTxt.css("display", "block");
        var inputVal = inputField.val().split('').join(' ');
        if(inputVal === captcha.text().trim()){ //if captcha matched
          statusTxt.css("color",  "#4db2ec");
          statusTxt.text("Nice! You don't appear to be a robot.");
          $('#is_correct_captcha').attr('checked','checked');
          setTimeout(()=>{ //calling removeContent & getCaptcha after 2 seconds
            // self.removeContent();
            // self.getCaptcha();
          }, 2000);
        }else{
          statusTxt.css("color", "red");
          statusTxt.text("Captcha not matched. Please try again!");
        }
      },
    });
 });