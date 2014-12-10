<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Files</%def>

<div class="row">
<div class="col-md-8">
    <div class='help-block'>
        % if 'write' in user['permissions'] and not disk_saving_mode:
            <p>To Upload: Drag files from your desktop into a folder below OR click an upload (<button class="btn btn-default btn-mini" disabled><i class="icon-upload"></i></button>) button.</p>
        % endif
    </div>
</div><!-- end col-md-->

<div class="col-md-4">
    <input role="search" class="form-control" placeholder="Search files..." type="text" id="fileSearch" autofocus>
</div>
</div><!--end row -->

 ## TODO: This progressbar is used else where; separate into a template include
<div id="treeGrid" class="filebrowser">
<div class="fangorn-loading"> <i class="icon-spinner fangorn-spin"></i> <p class="m-t-sm fg-load-message"> Loading files...  </p> </div>
</div>

<script type="text/javascript">
$(document).ready(function(){
  function displayMessage(){if(used.length===7){used=[]}var e=pickUnique();used.push(e);var t=$(".fg-load-message");if(t.length>0){t.text(loadingText[e]+"...")}else{stopRefresh()}}function stopRefresh(){clearInterval(msg)}function pickUnique(){var e=Math.floor(Math.random()*15)+1;if(used.indexOf(e)!==-1){pickUnique()}else{return e}}var msg=setInterval(function(){displayMessage()},2e3);var loadingText=["Adjusting Bell Curves","Aligning Covariance Matrices","Applying Theatre Soda Layer","Calculating Llama Expectoration Trajectory","Deciding What Message to Display Next","Gesticulating Mimes","Projecting Law Enforcement Pastry Intake","Setting Universal Physical Constants","Calibrating warp drive","Removing bad memories","Reorganizing distribution matrix","Validating assumptions","Scrambling launch codes","Allocating head space","Revising life goals","Pushing up elephants up the stairs"];var used=[]
  });
</script>


<%def name="stylesheets()">
${parent.stylesheets()}
% for stylesheet in tree_css:
<link rel='stylesheet' href='${stylesheet}' type='text/css' />
% endfor
</%def>

<%def name="javascript_bottom()">
${parent.javascript_bottom()}
% for script in tree_js:
<script type="text/javascript" src="${script}"></script>
% endfor
<script>
window.ondragover = function(e) { e.preventDefault(); };
window.ondrop = function(e) { e.preventDefault(); };


$script.ready(['fangorn'], function() {

    $.ajax({
      url:  nodeApiUrl + 'files/grid/'
    })
    .done(function( data ) {
        console.log("data", data);
        var fangornOpts = {
            placement : 'project-files',
            divID: 'treeGrid',
            filesData: data.data

        };
        console.log("fangorn", Fangorn);
        var filebrowser = new Fangorn(fangornOpts);
    });

});


</script>
</%def>





<%doc>

<div id="filebrowserProgressBar" class="progress progress-striped active">
    <div class="progress-bar"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">
        <span class="sr-only">Loading</span>
    </div>
</div>
<div id="myGrid" class="filebrowser hgrid"></div>
</%doc>

<%doc>
<%def name="stylesheets()">
${parent.stylesheets()}
% for stylesheet in tree_css:
<link rel='stylesheet' href='${stylesheet}' type='text/css' />
% endfor
</%def>

<%def name="javascript_bottom()">
${parent.javascript_bottom()}
% for script in tree_js:
<script type="text/javascript" src="${script}"></script>
% endfor
<script>
// Don't show dropped content if user drags outside grid
window.ondragover = function(e) { e.preventDefault(); };
window.ondrop = function(e) { e.preventDefault(); };

$script.ready(['rubeus'], function() {
    var rubeusOpts = {
        data: nodeApiUrl + 'files/grid/',
        searchInput: '#fileSearch'
    };
    % if disk_saving_mode:
    rubeusOpts.uploads = false;
    % endif
    var filebrowser = new Rubeus('#myGrid', rubeusOpts);
});

</script>
</%def>
</%doc>
