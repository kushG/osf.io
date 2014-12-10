/**
 * Module that controls the Google Drive node settings. Includes Knockout view-model
 * for syncing data.
 */
;(function (global, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['knockout', 'jquery', 'osfutils', 'knockoutpunches'], factory);
    } else {
        global.GdriveNodeConfig  = factory(ko, jQuery);
    }
}(this, function(ko, $) {
    // Enable knockout punches
    ko.punches.enableAll();

    var ViewModel = function(url) {
        var self = this;
        self.url = url;
        // TODO: Initialize observables, computes, etc. here
        self.nodeHasAuth = ko.observable(false);
        self.userHasAuth = ko.observable(false);
        self.folder = ko.observable({name : null, path : null});
        self.api_key = ko.observable();
        self.client_key = ko.observable();
        self.scope = ko.observable();
        self.owner = ko.observable();
        self.loadedSettings = ko.observable(false);
        self.urls = ko.observable({});
        self.ownerName = ko.observable();
        // Currently selected folder, an Object of the form {name: ..., path: ...}
        self.selected = ko.observable(null);
        self.userIsOwner = ko.observable(false);

        var access_token;


        // Flashed messages
        self.message = ko.observable('');
        self.messageClass = ko.observable('text-info');


        // Get data from the config GET endpoint
        function onFetchSuccess(response) {
            // Update view model
            self.nodeHasAuth(response.result.nodeHasAuth);
            self.userHasAuth(response.result.userHasAuth);
            self.urls(response.result.urls);
            self.owner(response.result.urls.owner);
            self.ownerName(response.result.ownerName);
            self.client_key(response.result.client_key);
            self.api_key(response.result.api_key);
            self.scope(response.result.scope);
            access_token = response.result.access_token;
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

        /** Calls Google picker API & selects a folder
         * to replace existing folder
         */
        self.changeFolder = function() {
            $.getScript('https://apis.google.com/js/api.js?onload=onApiLoad', function () {

                gapi.load('picker', {'callback': onPickerApiLoad });

                function onPickerApiLoad() {

                    var docsView = new google.picker.DocsView().
                        setIncludeFolders(true).
                        setSelectFolderEnabled(true);

                    var picker = new google.picker.PickerBuilder().
                        addView(docsView).
//                        addView(google.picker.ViewId.FOLDERS).
                        setOAuthToken(access_token).
                        setDeveloperKey(self.api_key()).
                        enableFeature(google.picker.Feature.MULTISELECT_ENABLED).
                        setCallback(pickerCallback).
                        build();
                    picker.setVisible(true);
                }

                // callback for picker API
                function pickerCallback(data) {
                    var url = 'nothing';
                    if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
                        var doc = data[google.picker.Response.DOCUMENTS][0];
                        id = doc[google.picker.Document.ID];
                        name = doc[google.picker.Document.NAME];
                        console.log(id);
                        console.log(name);

                        //Get folder & files using drive service
                        $.getJSON(
                            self.urls().get_folders,
                            {
                                'folder-id': id
                            },
                            function (response) {
                                console.log(response);
                                var result = response.result;
                                if (result != null) {
                                    var Items = []
                                    for (var child = 0; child < result.length; child++) {
                                        Items.push({
                                            name: result[child].title,
                                            id: result[child].id,
                                            kind: "item"
                                        })
                                    }
                                }
                                console.log(Items);


                                var files = [
                                    {
                                        id: id,
                                        name: name,
                                        kind: 'folder',
                                        children: Items
                                    }
                                ]
                                // Treebeard options
                                var options = {
                                    divID: "treebeard",
                                    filesData: files,     // Array variable to be passed in
                                    rowHeight: 35,
                                    paginate: false,
                                    showPaginate: false,
                                    uploads: false,
                                    columnTitles: function () {
                                        return [
                                            {
                                                title: "ID",
                                                width: "10%",
                                                sortType: "text",
                                                sort: false
                                            },
                                            {
                                                title: "Name",
                                                width: "60%",
                                                sortType: "text",
                                                sort: true
                                            },
                                            {
                                                title: "Kind",
                                                width: "15%",
                                                sortType: "text",
                                                sort: false
                                            }
                                        ]
                                    },
                                    resolveRows: function (item) {
                                        return [
                                            {
                                                data: "id",
                                                filter: false
                                            },
                                            {
                                                data: "name",
                                                filter: true,
                                                folderIcons: true
                                            },
                                            {
                                                data: "kind",
                                                filter: false
                                            }
                                        ]
                                    },
                                    allowMove: false
                                }

                                var filebrowser = new Fangorn(options);
                            });
                        self.changeMessage('You picked: ' + name, 'text-primary');

                    }


                }
            });
        }

//        self.showFolders = ko.computed(function(){
//            return self.nodeHasAuth();
//        })
        self.showFolders = ko.observable(true);

       /** Computed functions for the linked and selected folders' display text.*/

        self.folderName = ko.computed(function() {
            // Invoke the observables to ensure dependency tracking
            var nodeHasAuth = self.nodeHasAuth();
            var folder = self.folder();
            return (nodeHasAuth && folder) ? folder.name : '';
        });

        self.selectedFolderName = ko.computed(function() {
            var userIsOwner = self.userIsOwner();
            var selected = self.selected();
            return (userIsOwner && selected) ? selected.name : '';
        });

        /**
         * Must be used to update radio buttons and knockout view model simultaneously
         */
        self.cancelSelection = function() {
            self.selected(null);
        };

          /** Callback for chooseFolder action.
        *   Just changes the ViewModel's self.selected observable to the selected
        *   folder.
        */
        function onPickFolder(evt, item) {
            evt.preventDefault();
            self.selected({name: 'GoogleDrive' + item.data.path, path: item.data.path});
            var filePath = $("[data-bind='attr.href: urls().files']").text().trim();
            var filePathTokenized = filePath.split("/");
            return false; // Prevent event propagation
        }


         /**
         * Activates the Treebeard folder picker.
         */
        self.activatePicker = function() {
            self.currentDisplay(self.PICKER);
            // Only load folders if they haven't already been requested
            if (!self.loadedFolders()) {
                // Show loading indicator
                //self.loading(true);
                $(self.folderPicker).folderpicker({
                    onPickFolder: onPickFolder,
                    initialFolderName : self.folderName(),
                    // Fetch Dropbox folders with AJAX
                    filesData: self.urls().folders, // URL for fetching folders
                    // Lazy-load each folder's contents
                    // Each row stores its url for fetching the folders it contains
                    fetchUrl: function(row) {
                        return row.urls.folders;
                    },
                    resolveLazyloadUrl : function(tree, item){
                        return item.data.urls.folders;
                    },
                    oddEvenClass : {
                        odd : 'dropbox-folderpicker-odd',
                        even : 'dropbox-folderpicker-even'
                    },
                    ajaxOptions: {
                       error: function(xhr, textStatus, error) {
                            self.loading(false);
                            self.changeMessage('Could not connect to Dropbox at this time. ' +
                                                'Please try again later.', 'text-warning');
                            Raven.captureMessage('Could not GET get Dropbox contents.', {
                                textStatus: textStatus,
                                error: error
                            });
                        }
                    },
                    init: function() {
                        // Hide loading indicator
                        self.loading(false);
                        // Set flag to prevent repeated requests
                        self.loadedFolders(true);
                    }
                });
            };
        };


    };

    function GdriveNodeConfig(selector, url) {
        // Initialization code
        var self = this;
        self.viewModel = new ViewModel(url);
        $.osf.applyBindings(self.viewModel, selector);
    }
    return GdriveNodeConfig;


}));
