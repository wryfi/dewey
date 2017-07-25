$(function() {
    // function to grab parameters out of URL
    $.get_url_param = function(parameter) {
        var url = window.location.search.substring(1);
        var url_vars = url.split('&');
        for (var i = 0; i < url_vars.length; i++) {
            var parameter_name = url_vars[i].split('=');
            if (parameter_name[0] == parameter) {
                return parameter_name[1];
            }
        }
    };
})