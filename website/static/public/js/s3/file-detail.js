webpackJsonp([7],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	var DeleteFile = __webpack_require__(47);

	new DeleteFile('#s3Scope', window.contextVars.node.urls);


/***/ },

/***/ 47:
/***/ function(module, exports, __webpack_require__) {

	/**
	 * Simple knockout model and view model for managing crud addon delete files on the
	 * file detail page.
	 */

	'use strict';
	var ko = __webpack_require__(15);
	__webpack_require__(7);
	var $ = __webpack_require__(13);
	var $osf = __webpack_require__(3);
	var bootbox = __webpack_require__(12);

	ko.punches.enableAll();

	function DeleteFileViewModel(urls) {
	    var self = this;

	    self.api_url = ko.observable(urls['delete_url']);
	    self.files_page_url = ko.observable(urls['files_page_url']);
	    self.deleting = ko.observable(false);

	    self.deleteFile = function(){
	        bootbox.confirm({
	            title: 'Delete file?',
	            message: 'Are you sure you want to delete this file? It will not be recoverable.',
	            callback: function(result) {
	                if(result) {
	                    self.deleting(true);
	                    var request = $.ajax({
	                        type: 'DELETE',
	                        url: self.api_url()
	                    });
	                    request.done(function() {
	                        window.location = self.files_page_url();
	                    });
	                    request.fail(function( jqXHR, textStatus ) {
	                        self.deleting(false);
	                        $osf.growl('Error:', 'Could not delete: ' + textStatus );
	                    });

	                }
	            }
	        });
	    };
	}
	// Public API
	function DeleteFile(selector, urls) {
	    this.viewModel = new DeleteFileViewModel(urls);
	    $osf.applyBindings(this.viewModel, selector);
	}

	module.exports = DeleteFile;


/***/ }

});