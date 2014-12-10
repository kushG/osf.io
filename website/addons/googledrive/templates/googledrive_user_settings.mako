<div id="googledriveAddonScope" class="addon-settings scripted">

<h4 class="addon-title">
    Google Drive
</h4>
<small class="authorized-by">
    <span>authorized by xyz</span>
    <!-- Delete Access Token Button -->
    <!--Create Access token Button-->
    <a class="pull-right text-primary addon-auth"Create Access token> </a>
</small>



<div class="help-block">
    <%include file="profile/addon_permissions.mako" />
</div>


</div> <!--End of googledriveAddonScope -->


<script>
    $script(['/static/addons/googledrive/googledriveUserConfig.js'], function() {
        // Endpoint for googledrive user settings
        var url = '/api/v1/settings/drive-creds/';
        // Start up the Dropbox Config manager
        var drive = new DriveUserConfig('#googledriveAddonScope', url);
    });
</script>