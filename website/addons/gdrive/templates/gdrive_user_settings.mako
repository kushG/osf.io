<!-- TODO -->
<h4 class="addon-title">
    Google Drive
</h4>

<div id="driveAddonScope"class="addon-settings scripted">
    <!-- Delete Access Token Button-->
    <div data-bind="if: userHasAuth() && loaded()">
        <button data-bind="click:deleteKey" class="btn btn-danger">
            Delete Access Token
        </button>
    </div>
    <!-- Create Access Token Button -->
    <div data-bind="if: !userHasAuth() && loaded()">
        <button data-bind="click:createAuth" class="btn btn-primary">
            Create Access Token
        </button>
    </div>

    <!-- Flashed Messages -->
    <div class="help-block">
        <p data-bind="html: message, attr: {class: messageClass}"></p>
    </div>


</div>

<script>
    $script(['/static/addons/gdrive/gdriveUserConfig.js'], function() {
        //Endpoint for Drive user settings
        var url = '/api/v1/settings/gdrive';
        // Start up the Drive Config Manager
        var drive = new GdriveUserConfig('#driveAddonScope', url);
    });

</script> 