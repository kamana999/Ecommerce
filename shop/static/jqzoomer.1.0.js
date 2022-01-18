/*
Copyright (c) 2014, Armande Bayanes, http://jqzoomer.strongtechsolutions.com.ph
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by the <organization>.
4. Neither the name of the <organization> nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Armande Bayanes ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Armande Bayanes BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/* jQuery plugin named "jqzoomer".
 * 
 *  @author     Armande Bayanes (tuso@programmerspride.com)
 *  @date       November 18, 2014
 *  @liscense   FREE of use.
 *  @example
 *      1.  $('#element_id').jqzoomer()
 *      2.  jQuery('#element_id').jqzoomer()
 *      3.  $('.element_class').jqzoomer()
 *      4.  jQuery('.element_class').jqzoomer()
 * */
jQuery.fn.jqzoomer = function(){
    
    return this.each(function() {
        
        var subject = jQuery(this); /* Get the subject element (AS canvas). */

        var image_obj = jQuery('img', subject);
        var image = image_obj.attr('src');

        jQuery(image_obj).one('load', function() {

            var image_w = this.width;
            var image_h = this.height;
            
            /* Fit subject with the width and height of the default image. */
            subject.css('width', image_w).css('height', image_h).css('overflow', 'hidden');
            
            /* Position the default image. */
            image_obj.css('position', 'relative').css({ top: 0, left: 0 });

            jQuery('a', subject).bind('click onclick', function(event) {
                event.preventDefault(); /* Disable clicking of a. */
            });

            var image_zoom = jQuery('a', subject).attr('href'); // Get the large image.
            var image_zoom_w = 0;
            var image_zoom_h = 0;

            var image_zoom_obj = new Image() ;            
            jQuery(image_zoom_obj).one('load', function() {

                image_zoom_w = this.width;
                image_zoom_h = this.height;

                /* Bind the subject element with these events. */
                subject.bind('mousemove mouseout', function(event) {

                    if(event.type == 'mousemove') {

                        /* @start: Will position the mouse inside the canvas only. */
                        var mouse_x = event.pageX - subject.offset().left;
                        var mouse_y = event.pageY - subject.offset().top;
                        /* @end: Will position the mouse inside the canvas only. */

                        var goto_x = (Math.round((mouse_x / image_w) * 100) / 100) * (image_zoom_w - image_w);
                        var goto_y = (Math.round((mouse_y / image_h) * 100) / 100) * (image_zoom_h - image_h);

                        console.log('mouse_x: '+ mouse_x + ', mouse_y: '+ mouse_y);
                        console.log('image_w: '+ image_w + ', image_h: '+ image_h);

                        image_obj.css('cursor', 'crosshair').attr('src', image_zoom).css({ left: -goto_x, top: -goto_y });

                    } else if(event.type == 'mouseout') {

                        image_obj.css('cursor', 'default').attr('src', image).css({ top: 0, left: 0 });
                    }
                });
            });

            jQuery(image_zoom_obj).attr('src', image_zoom);
        });
    });
};