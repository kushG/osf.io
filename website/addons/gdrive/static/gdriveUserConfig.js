/**
 * Module that controls the Google Drive user settings. Includes Knockout view-model
 * for syncing data.
 */

;(function (global, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['knockout', 'jquery', 'osfutils', 'language','knockoutpunches'], factory);
    } else {
        global.GdriveUserConfig  = factory(ko, jQuery);
    }
}(this, function(ko, $) {
    // Enable knockout punches
    ko.punches.enableAll();

    var language = $.osf.Language.Addons.gdrive;
    var ViewModel = function(url) {
        var self = this;
        self.userHasAuth = ko.observable(false);
        self.api_key = ko.observable();
        self.client_key = ko.observable();
        self.scope = ko.observable();
        self.urls = ko.observable();
        self.loaded = ko.observable(false);
        self.message = ko.observable('');
        self.messageClass = ko.observable('text-info');
        var pickerApiLoaded = false;
        self.access_token = ko.observable();
        var postToken = false;


            $.ajax({
            url: url, type: 'GET', dataType: 'json',
            success: function(response) {
                var data = response.result;
                self.userHasAuth(data.userHasAuth);
                self.urls(data.urls);
                self.loaded(true);
                self.api_key(data.api_key);
                self.client_key(data.client);
                self.scope(data.scope);
//
            },
            error: function(xhr, textStatus, error){
                self.changeMessage('Could not retrieve settings. Please refresh the page or ' +
                    'contact <a href="mailto: support@osf.io">support@osf.io</a> if the ' +
                    'problem persists.', 'text-warning');
                Raven.captureMessage('Could not GET Google Drive settings', {
                    url: url,
                    textStatus: textStatus,
                    error: error
                });
            }
        });


       /** Change the flashed status message */
        self.changeMessage = function(text, css, timeout) {
            self.message(text);
            var cssClass = css || 'text-info';
            self.messageClass(cssClass);
            if (timeout) {
                // Reset message after timeout period
                setTimeout(function() {
                    self.message('');
                    self.messageClass('text-info');
                }, timeout);
            }
        };


        self.createAuth = function(){
            $.getScript('https://apis.google.com/js/api.js?onload=onApiLoad', function()
            {

                gapi.load('auth', {'callback': onAuthApiLoad});
                gapi.load('picker', {'callback': onPickerApiLoad});



                function onAuthApiLoad() {
                window.gapi.auth.authorize(
                    {
                      'client_id': self.client_key(),
                      'scope': self.scope(),
                      'immediate': false
                    },
                    handleAuthResult);
                }

                function onPickerApiLoad() {
                pickerApiLoaded = true;
                }

                function handleAuthResult(authResult) {
                if (authResult && !authResult.error) {
                  self.access_token(authResult.access_token);
                  postToken = true;
                  postAccessToken();
                }
            }});
        };

        function postAccessToken()
        {
            if(postToken)
            {
                $.osf.postJSON(
                    self.urls().create,
                    {'access_token': self.access_token()}
                    ).done(function () {
                        window.location.reload();
                    }).fail(function(response){
                        self.changeMessage('Could not authorize at this moment', 'text-danger');
                    });
            }
        }


        /** Pop up confirm dialog for deleting user's access token. */
        self.deleteKey = function() {
            bootbox.confirm({
                title: 'Delete Google Drive Token?',
                message: language.confirmDeauth,
                callback: function(confirmed) {
                    if (confirmed) {
                        sendDeauth();
                    }
                }
            });
        };

        /** Send DELETE request to deauthorize Drive */
        function sendDeauth() {
            return $.ajax({
                url: self.urls().delete,
                type: 'DELETE',
                success: function() {
                    window.location.reload();
                    self.changeMessage(language.deauthSuccess, 'text-info', 5000);

                },
                error: function(textStatus, error) {
                    self.changeMessage(language.deauthError, 'text-danger');
                    Raven.captureMessage('Could not deauthorize Dropbox.', {
                        url: url,
                        textStatus: textStatus,
                        error: error
                    });
                }
            });
        }


    };

    function GdriveUserConfig(selector, url) {
        // Initialization code
        var self = this;
        self.viewModel = new ViewModel(url);
        $.osf.applyBindings(self.viewModel, selector);
    }
        return GdriveUserConfig;

}));
