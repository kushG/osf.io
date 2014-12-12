webpackJsonp([27],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	var DropboxUserConfig = __webpack_require__(44);

	// Endpoint for dropbox user settings
	var url = '/api/v1/settings/dropbox/';
	// Start up the Dropbox Config manager
	new DropboxUserConfig('#dropboxAddonScope', url);


/***/ },

/***/ 44:
/***/ function(module, exports, __webpack_require__) {

	/**
	* View model that controls the Dropbox configuration on the user settings page.
	*/
	'use strict';
	var ko = __webpack_require__(15);
	__webpack_require__(7);
	ko.punches.enableAll();
	var $ = __webpack_require__(13);
	var Raven = __webpack_require__(14);
	var bootbox = __webpack_require__(12);

	var language = __webpack_require__(71).Addons.dropbox;
	var osfHelpers = __webpack_require__(3);
	function ViewModel(url) {
	    var self = this;
	    self.userHasAuth = ko.observable(false);
	    // Whether the auth token is valid
	    self.validCredentials = ko.observable(true);
	    self.dropboxName = ko.observable();
	    self.urls = ko.observable({});
	    // Whether the initial data has been loaded.
	    self.loaded = ko.observable(false);
	    self.nNodesAuthorized = 0;
	    // Update above observables with data from server
	    $.ajax({
	        url: url, type: 'GET', dataType: 'json',
	        success: function(response) {
	            var data = response.result;
	            self.userHasAuth(data.userHasAuth);
	            self.dropboxName(data.dropboxName);
	            self.urls(data.urls);
	            self.loaded(true);
	            self.validCredentials(data.validCredentials);
	            self.nNodesAuthorized = data.nNodesAuthorized;
	            if (!self.validCredentials()) {
	                self.changeMessage('Could not retrieve Dropbox settings at ' +
	                    'this time. The Dropbox addon credentials may no longer be valid.' +
	                    ' Try deauthorizing and reauthorizing Dropbox.',
	                    'text-warning');
	            } else if (self.userHasAuth() && self.nNodesAuthorized === 0) {
	                self.changeMessage('Add-on successfully authorized. To link this add-on to an OSF project, ' +
	                    'go to the settings page of the project, enable Dropbox, and choose content to connect.',
	                    'text-success');
	            }
	        },
	        error: function(xhr, textStatus, error){
	            self.changeMessage('Could not retrieve settings. Please refresh the page or ' +
	                'contact <a href="mailto: support@osf.io">support@osf.io</a> if the ' +
	                'problem persists.', 'text-warning');
	            Raven.captureMessage('Could not GET Dropbox settings', {
	                url: url,
	                textStatus: textStatus,
	                error: error
	            });
	        }
	    });
	    // Flashed messages
	    self.message = ko.observable('');
	    self.messageClass = ko.observable('text-info');

	    /** Send DELETE request to deauthorize Dropbox */
	    function sendDeauth() {
	        return $.ajax({
	            url: self.urls().delete,
	            type: 'DELETE',
	            success: function() {
	                // Page must be refreshed to remove the list of authorized nodes
	                window.location.reload();
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

	    /** Pop up confirm dialog for deleting user's access token. */
	    self.deleteKey = function() {
	        bootbox.confirm({
	            title: 'Delete Dropbox Token?',
	            message: language.confirmDeauth,
	            callback: function(confirmed) {
	                if (confirmed) {
	                    sendDeauth();
	                }
	            }
	        });
	    };
	}

	function DropboxUserConfig(selector, url) {
	    var self = this;
	    self.selector = selector;
	    self.url = url;
	    // On success, instantiate and bind the ViewModel
	    self.viewModel = new ViewModel(url);
	    osfHelpers.applyBindings(self.viewModel, selector);
	}
	module.exports = DropboxUserConfig;


/***/ },

/***/ 71:
/***/ function(module, exports, __webpack_require__) {

	module.exports = {
	    // TODO
	    makePublic: null,
	    makePrivate: null,

	    Addons: {
	        dataverse: {
	            userSettingsError: 'Could not retrieve settings. Please refresh the page or ' +
	                'contact <a href="mailto: support@osf.io">support@osf.io</a> if the ' +
	                'problem persists.',
	            confirmUserDeauth: 'Are you sure you want to unlink your Dataverse ' +
	                'account? This will revoke access to Dataverse for all ' +
	                'projects you have authorized.',
	            confirmNodeDeauth: 'Are you sure you want to unlink this Dataverse account? This will ' +
	                'revoke the ability to view, download, modify, and upload files ' +
	                'to studies on the Dataverse from the OSF. This will not remove your ' +
	                'Dataverse authorization from your <a href="/settings/addons/">user settings</a> ' +
	                'page.',
	            deauthError: 'Could not unlink Dataverse at this time.',
	            deauthSuccess: 'Unlinked your Dataverse account.',
	            authError: 'There was a problem connecting to the Dataverse.',
	            authInvalid: 'Your Dataverse username or password is invalid.',
	            authSuccess: 'Your Dataverse account was linked.',
	            studyDeaccessioned: 'This study has already been deaccessioned on the Dataverse ' +
	                'and cannot be connected to the OSF.',
	            forbiddenCharacters: 'This study cannot be connected due to forbidden characters ' +
	                'in one or more of the study\'s file names. This issue has been forwarded to our ' +
	                'development team.',
	            setStudyError: 'Could not connect to this study.',
	            widgetInvalid: 'The Dataverse credentials associated with ' +
	                'this node appear to be invalid.',
	            widgetError: 'There was a problem connecting to the Dataverse.'
	        },
	        dropbox: {
	            // Shown on clicking "Delete Access Token" for dropbox
	            confirmDeauth: 'Are you sure you want to delete your Dropbox access ' +
	                'key? This will revoke access to Dropbox for all projects you have ' +
	                'authorized.',
	            deauthError: 'Could not deauthorize Dropbox at this time',
	            deauthSuccess: 'Deauthorized Dropbox.'
	        },
	        // TODO
	        github: {

	        },
	        s3: {

	        }
	    }
	};


/***/ }

});