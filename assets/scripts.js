var expected_canvas_count = 0;

$(document).ready(function(){

    var pagination = $('details').find('.previous-next-container');
    pagination.remove();

    if(expected_canvas_count > 0){
        var canvas_check = setInterval(checkForCanvases, 3000);
    }

    var datepicker_fixer = setInterval(date_picker_closer, 3500);

    var css_fixer = setInterval(removeBaddCss, 3500);
    // console.log('set remove css interval');

    $('#react-entry-point').keydown(function(e) {
        var code = e.keyCode || e.which;
    
        if (code === 13 ) {  
            // e.preventDefault();
            // myFunction();
            $(document.activeElement).click();
        }
    });

    // Callback function to execute when mutations are observed
    const callback = function(mutationsList, observer) {
        // Use traditional 'for loops' for IE 11
        for(const mutation of mutationsList) {
            if (mutation.type === 'attributes') {
                if(mutation.attributeName == 'height' || mutation.attributeName == 'width' ){
                    // console.log('The ' + mutation.attributeName + ' attribute was modified.');
                    // console.log('The mutation ' + mutation.target);
                    canvasDimensionsAdjustment(mutation.target);
                }
            }
        }
    };

    function date_picker_closer(){
        console.log("looking for datepicker");
        if($('#react-entry-point')){
            clearInterval(datepicker_fixer);
            $('#react-entry-point').keyup(function(e) {
                var code = e.keyCode || e.which;
            
                if (code === 9) {  
                    // e.preventDefault();
                    // myFunction();
                    console.log($(document.activeElement));
                    if($(document.activeElement).parents('#date_picker_range').length){
                        console.log('focused');
                        $('.DateRangePicker_picker').show();
                    }else{
                        $('.DateRangePicker_picker').hide();
                    }
                }
            });

            $('.DateInput_input').focus(function(){
                $('.DateRangePicker_picker').show();
            });
        }
    }

    var ariaFixes = setInterval(function(){
        var dropdowns = $('.Select-input input');
        dropdowns.removeAttr('aria-owns');
        var header_script = $('head script');
        header_script.removeAttr('charset');
        // dropdowns.attr('role', 'option');
    }, 3000);

    // Create an observer instance linked to the callback function
    const observer = new MutationObserver(callback);

    function removeBaddCss(){
        $("head").find('style').each(function () {
            // console.log('removing css');
            html = $(this).html();
            if(html.match(/border-color:\s*transparent\s*inherit\s*transparent\s*transparent\s*!important/gm)){
                $(this).html( html.replace(/border-color:\s*transparent\s*inherit\s*transparent\s*transparent\s*!important/gm,"") );
            }
        });
        
    }

    function canvasDimensionsAdjustment(canvas){
        if(canvas.getAttribute('width') % 1 != 0){
            // console.log('not whole number', mutation.target.getAttribute('width'));
            canvas.setAttribute('width', Math.round(canvas.getAttribute('width')));
        }
        if(canvas.getAttribute('height') % 1 != 0){
            // console.log('not whole number', mutation.target.getAttribute('heightheight'));
            canvas.setAttribute('height', Math.round(canvas.getAttribute('height')));
        }
    }

    function checkForCanvases(){
        console.log('checking for canvases');
        var canvases = $('canvas');
        if(canvases.size() > 0){
            console.log('canvases found: '+canvases.size(), canvases );
            canvasObserver(canvases);
            canvases.each(function(){
                canvasDimensionsAdjustment(this);
            });
            if(canvases.size() >= expected_canvas_count){
                clearInterval(canvas_check);
                console.log('stopped checking for canvases');
            }
            
            return true;
        }
        return false;
    }
    
    
    function canvasObserver(canvases){
        // Select the node that will be observed for mutations
        var targetNodes = canvases;
    
        // Options for the observer (which mutations to observe)
        const config = { attributes: true, childList: true, subtree: true };
    
        // Start observing the target node for configured mutations
        // observer.observe(targetNode, config);
        targetNodes.each(function(){
            observer.observe(this, config);
        });
    }
});