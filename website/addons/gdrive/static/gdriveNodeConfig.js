
/**
* Module that controls the Dropbox node settings. Includes Knockout view-model
* for syncing data, and HGrid-folderpicker for selecting a folder.
*/
'use strict';

var ko = require('knockout');
require('knockout-punches');
var $ = require('jquery');
var bootbox = require('bootbox');
var Raven = require('raven-js');

var FolderPicker = require('folderpicker');
var ZeroClipboard = require('zeroclipboard');
ZeroClipboard.config('/static/vendor/bower_components/zeroclipboard/dist/ZeroClipboard.swf');
var $osf = require('osfHelpers');

ko.punches.enableAll();
/**
    * Knockout view model for the Google Drive node settings widget.
    */
    var ViewModel = function(url, selector, folderPicker) {
        var self = this;
        self.url = url;
        self.nodeHasAuth = ko.observable(false);
        self.userHasAuth = ko.observable(false);
        // whether current user is authorizer of the addon
        self.userIsOwner = ko.observable(false);

        //Api key required for Google picker
        self.access_token = ko.observable();

        self.owner = ko.observable();
        self.ownerName = ko.observable();
        self.urls = ko.observable();
        self.folder = ko.observable({name: null, path: null});
        self.loadedFolders = ko.observable(false);
        self.loading = ko.observable(false);
        self.currentFolder = ko.observable("None");

        //Folderpicker specific
        self.folderPicker =  folderPicker;
        self.selected = ko.observable(null);
        self.showFileTypes = ko.observable(false);
        var setOwner;

        self.loadedSettings = ko.observable(false);
        self.selectedFileTypeOption = ko.observable('');

        // Flashed messages
        self.message = ko.observable('');
        self.messageClass = ko.observable('text-info');

        // Get data from the config GET endpoint
        function onFetchSuccess(response) {
            // Update view model
            self.nodeHasAuth(response.result.nodeHasAuth);
            self.userHasAuth(response.result.userHasAuth);
            self.userIsOwner(response.result.userIsOwner);
            self.urls(response.result.urls);
            self.ownerName(response.result.ownerName);
            self.owner(response.result.urls.owner);
            self.access_token (response.result.access_token);
            self.currentFolder(response.result.currentFolder);

            if(self.currentFolder() == null)
                self.currentFolder('None');
            self.loadedSettings(true);
        }
        function onFetchError(xhr, textstatus, error) {
            self.message('Could not fetch settings.');
        }
        function fetch() {
            $.ajax({url: self.url, type: 'GET', dataType: 'json',
                    success: onFetchSuccess,
                    error: onFetchError
            });
        }

        fetch();
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


        /** Whether or not to show the Create Access Token button */
        self.showTokenCreateButton = ko.computed(function() {
            // Invoke the observables to ensure dependency tracking
            var userHasAuth = self.userHasAuth();
            var nodeHasAuth = self.nodeHasAuth();
            var loaded = self.loadedSettings();
            return !userHasAuth && !nodeHasAuth && loaded;
        });

        self.createAuth = function(){

                    $.osf.postJSON(
                    self.urls().create
                    ).success(function(response){
                        window.location.href = response.url;
                        self.changeMessage('Successfully authorized Google Drive account', 'text-primary');
                    }).fail(function(){
                        self.changeMessage('Could not authorize at this moment', 'text-danger');
                    });
        };



         /**
         * Whether or not to show the Import Access Token Button
         */
        self.showImport = ko.computed(function() {
            // Invoke the observables to ensure dependency tracking
            var userHasAuth = self.userHasAuth();
            var nodeHasAuth = self.nodeHasAuth();
            var loaded = self.loadedSettings();
            return userHasAuth && !nodeHasAuth && loaded;
        });

        // Callback for when PUT request to import user access token
        function onImportSuccess(response) {
            var msg = response.message || 'Successfully imported access token from profile.';
            self.changeMessage(msg, 'text-success', 3000);
            window.location.reload();
        }

        function onImportError() {
            self.message('Error occurred while importing access token.');
            self.messageClass('text-danger');
        }

        /**
         * Send PUT request to import access token from user profile.
         */
        self.importAuth = function() {
            bootbox.confirm({
                title: 'Import Google Drive Access Token?',
                message: 'Are you sure you want to authorize this project with your Google Drive access token?',
                callback: function(confirmed) {
                    if (confirmed) {
                        return $.osf.putJSON(self.urls().importAuth, {})
                            .done(onImportSuccess)
                            .fail(onImportError);
                    }
                }
            });
        };


        /**
         * Send DELETE request to deauthorize this node.
         */
        function sendDeauth() {
            return $.ajax({
                url: self.urls().deauthorize,
                type: 'DELETE',
                success: function() {
                    // Update observables
                    self.nodeHasAuth(false);
                    self.changeMessage('Deauthorized Google Drive.', 'text-warning', 3000);
                },
                error: function() {
                    self.changeMessage('Could not deauthorize Google Drive because of an error. Please try again later.',
                        'text-danger');
                }
            });
        }

        /** Pop up a confirmation to deauthorize Dropbox from this node.
         *  Send DELETE request if confirmed.
         */
        self.deauthorize = function() {
            bootbox.confirm({
                title: 'Deauthorize Google Drive?',
                message: 'Are you sure you want to remove this Google Drive authorization?',
                callback: function(confirmed) {
                    if (confirmed) {
                        return sendDeauth();
                    }
                }
            });
        };


        /** Callback for chooseFolder action.
        *   Just changes the ViewModel's self.selected observable to the selected
        *   folder.
        */
        function onPickFolder(evt, item) {
                evt.preventDefault();
                self.selected({name:item.data.path.path, path: item.data.path, id: item.data.id});
                return false; // Prevent event propagation
        }


        /** Calling Google Drive API & arranging data as
         * required for treebeard Hgrid
         */

        self.changeFolder = function() {
                    $(self.folderPicker).folderpicker({
                        onPickFolder: onPickFolder,
                        filesData: self.urls().get_folders,
                        // Lazy-load each folder's contents
                        // Each row stores its url for fetching the folders it contains

                        resolveLazyloadUrl : function(item){
                             return item.data.urls.get_folders;
                        },
                        ajaxOptions: {
                            error: function (xhr, textStatus, error) {
                                self.loading(false);
                                self.changeMessage('Could not connect to Google Drive at this time. ' +
                                    'Please try again later.', 'text-warning');
                                Raven.captureMessage('Could not GET get Google Drive contents.', {
                                    textStatus: textStatus,
                                    error: error
                                });
                            }
                        },
                        folderPickerOnload: function () {
                        }
                    });
        }


        self.showFolders = ko.computed(function(){
            return self.nodeHasAuth();
        })

        self.selectedFolderName = ko.computed(function() {
        var userIsOwner = self.userIsOwner();
        var selected = self.selected();
        return (userIsOwner && selected) ? selected.name : '';
        });


        function onSubmitSuccess(response) {
        self.changeMessage('Successfully linked "' + self.selected().name +
            '". Go to the <a href="' +
            self.urls().files + '">Files page</a> to view your files.',
            'text-success', 5000);
        // Update folder in ViewModel
        self.folder(response.result.folder);
        self.urls(response.result.urls);
        }

        function onSubmitError() {
            self.changeMessage('Could not change settings. Please try again later.', 'text-danger');
        }

        /**
            * Send a PUT request to change the linked Dropbox folder.
            */
        self.submitSettings = function() {
            $osf.putJSON(self.urls().config, ko.toJS(self))
                .done(onSubmitSuccess)
                .fail(onSubmitError);
        };


    };

    function GdriveNodeConfig(selector, url, folderPicker) {
        // Initialization code
        var self = this;
        self.viewModel = new ViewModel(url, selector, folderPicker);
        $.osf.applyBindings(self.viewModel, selector);
    }

    module.exports= GdriveNodeConfig;