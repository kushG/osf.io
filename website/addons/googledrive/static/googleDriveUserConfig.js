/**
* View model that controls the Google Drive configuration on the user settings page.
*/
'use strict';

var ko = require('knockout');
require('knockout-punches');
ko.punches.enableAll();
var $ = require('jquery');
var Raven = require('raven-js');
var bootbox = require('bootbox');

var language = require('osfLanguage').Addons.googledrive;
var osfHelpers = require('osfHelpers');


var GoogleDriveAccount = function(name, id) {
    this.name = name;
    this.id = id;
}

var ViewModel = function(name, url) {
    var self = this;
    self.name = name;
    self.accounts = ko.observableArray();

    self.userHasAuth = ko.observable(false);
    self.loaded = ko.observable(false);
    self.urls = ko.observable();

    //Helper-class variables
    self.message = ko.observable('');
    self.messageClass = ko.observable('text-info');


    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
    }).done(function(response) {
        var data =response.result;
        self.userHasAuth(data.userHasAuth);
        self.urls(data.urls);
        self.loaded(true);
    }).fail(function(xhr, textStatus, error) {
        self.changeMessage(
            'Could not retrieve settings. Please refresh the page or ' +
            'contact <a href="mailto: support@osf.io">support@osf.io</a> if the ' +
            'problem persists.', 'text-warning'
        );
        Raven.captureMessage('Could not GET Google Drive settings', {
            url: url,
            textStatus: textStatus,
            error: error
        });
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

    /** Create Authorization **/
    self.createAuth = function(){
//        $.getJSON(
//            self.urls().create
//        ).success(function(response){
//            window.location.href = response.url;
//            //TODO: Find a way to display this message
//            //self.changeMessage('Successfully authorized Google Drive account', 'text-primary');
//        }).fail(function(xhr, textStatus, error){
//            self.changeMessage('Could not authorize at this moment', 'text-danger');
//        });
          window.oauthComplete = function() {
              self.updateAccounts();
              self.changeMessage('Successfully authorized Google Drive account', 'text-primary');
          };

          window.open('/oauth/connect/' + self.name + '/');
    };

    /** Pop up confirm dialog for deleting user's access token. */
    self.deleteKey = function(account) {
        bootbox.confirm({
            title: 'Delete Google Drive Token for ' + account.name + '?',
            message: language.confirmDeauth,
            callback: function(confirmed) {
                if (confirmed) {
                    sendDeauth(account);
                }
            }
        });
    };

    /** Send DELETE request to deauthorize Drive */
    function sendDeauth(account) {
//        return $.ajax({
//            url: self.urls().delete,
//            type: 'DELETE'
//        }).done(function() {
//            window.location.reload();
//            self.changeMessage(language.deauthSuccess, 'text-info', 5000);
//        }).fail(function(textStatus, error) {
//            self.changeMessage(language.deauthError, 'text-danger');
//            Raven.captureMessage('Could not deauthorize Google Drive.', {
//                url: url,
//                textStatus: textStatus,
//                error: error
//            });
//        });

        var url = '/api/v1/oauth/accounts/' + account.id + '/';
        $.ajax({
            url: url,
            type: 'DELETE'
        }).done(function(data) {
            self.updateAccounts();
        }).fail(function(xhr, status, error) {
            Raven.captureMessage('Error while removing addon authorization for ' + account.id, {
                url: url, status: status, error: error
            });
        });
    }

    self.updateAccounts = function () {
        var url = '/api/v1/settings/' + self.name + '/accounts/';
        $.get(url).done(function(data) {
            self.accounts(data.accounts.map(function(account) {
                return new GoogleDriveAccount(account.display_name, account.id);
            }));
        }).fail(function(xhr, status, error) {
            Raven.captureMessage('Error while updating addon account', {
                url: url, status: status, error: error
            });
        });
    }

};

function GoogleDriveUserConfig(name, selector, url) {
    // Initialization code
    var self = this;
    self.viewModel = new ViewModel(name, url);
    self.viewModel.updateAccounts();
    $.osf.applyBindings(self.viewModel, selector);
}

module.exports = GoogleDriveUserConfig;
