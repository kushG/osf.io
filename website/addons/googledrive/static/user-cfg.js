var GoogleDriveUserConfig = require('../../../static/js/addonSettings.js');

// Endpoint for google drive user settings
var url = '/api/v1/settings/googledrive';
// Start up the Google Drive Config manager
new GoogleDriveUserConfig('googledrive', '#googleDriveAddonScope', url);
