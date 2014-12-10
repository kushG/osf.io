/**
 * View model that controls the Google Drive configuration on the user settings page.
 */
;(function (global, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['knockout', 'jquery', 'osfutils', 'language'], factory);
    } else if (typeof $script === 'function') {
        global.DriveUserConfig  = factory(ko, jQuery);
        $script.done('googledriveUserConfig');
    } else {
        global.DriveUserConfig  = factory(ko, jQuery);
    }
}(this, function(ko, $) {
    'use strict';

    var language = $.osf.Language.Addons.drive;

}))