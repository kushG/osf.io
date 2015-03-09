

<div id="googleDriveAddonScope" class="addon-settings scripted">
    <h4 class="addon-title">
        Google Drive
        <small>
            <!-- Delete Access Token Button-->
            <span data-bind="foreach:accounts">
                <div>
                    authorized
                    <span>by {{ name }}</span>
                    <a data-bind="click: $root.deleteKey" class="text-danger pull-right addon-auth">
                        Delete Access Token
                    </a>
                </div>
            </span>
        </small>
    </h4>
    <div>
    <!-- Create Access Token Button -->
        <a data-bind="click:createAuth" class="btn btn-primary">
            Connect Account
        </a>
    </div>


    <!-- Flashed Messages -->
    <div class="help-block">
        <p data-bind="html: message, attr: {class: messageClass}"></p>
    </div>
</div>

<%include file="profile/addon_permissions.mako" />
