% if len(nodes):
    <ul class="list-group ${'sortable' if sortable and 'write' in user['permissions'] else ''}">
        % for each in nodes:
            <div mod-meta='{
                    "tpl": "util/render_node.mako",
                    "uri": "${each['api_url']}get_summary/",
                    "view_kwargs": {
                        "rescale_ratio": ${rescale_ratio},
                        "primary": ${int(each['primary'])},
                        "link_id": "${each['id']}",
                        "uid": "${user_id}"
                    },
                    "replace": true
                }'></div>
        % endfor
    ## TODO: make sure these templates are only included once on a page.
    <%include file='_log_templates.mako'/>
    </ul>
    <script>
    % if sortable and 'write' in user['permissions']:
          $(function(){
              $('.sortable').sortable({
                  containment: '#containment',
                  tolerance: 'pointer',
                  items: '> li',
                  stop: function(event, ui){
                      var sortListElm = this;
                      var idList = $(sortListElm).sortable(
                          'toArray',
                          {attribute: 'node_reference'}
                      );
                      NodeActions.reorderChildren(idList, sortListElm);
                  }
              });
          });
    % endif
    </script>
    % elif user.get('is_profile', False):
    <div class="help-block">
      You have no public ${pluralized_node_type}.
        <p>
            Find out how to make your ${pluralized_node_type}
            <a href="https://osf.io/getting-started/#privacy" target="_blank">public</a>.
        </p>
    </div>
% elif profile is not UNDEFINED:  # On profile page and user has no public projects/components
    <div class="help-block">This user has no public ${pluralized_node_type}.</div>
% else:
    <div class="help-block">No ${pluralized_node_type} to display.</div>
% endif
