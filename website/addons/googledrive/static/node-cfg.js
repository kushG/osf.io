var GoogleDriveNodeConfig = require('./googleDriveNodeConfig.js');

var url = window.contextVars.node.urls.api + 'googledrive/config/';
new GoogleDriveNodeConfig('googledrive', '#googleDriveAddonScope', url, '#myGoogleDriveGrid');
