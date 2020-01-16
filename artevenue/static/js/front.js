$(function () {

    $('.shop-detail-carousel').owlCarousel({
        items: 1,
        thumbs: true,
        nav: false,
        dots: false,
        loop: true,
        autoplay: true,
        thumbsPrerendered: true
    });


    $('#main-slider').owlCarousel({
        items: 1,
		responsiveClass:true,
        nav: false,
		//navText: ["",""],
        //dots: true,
		loop:true,
        autoplay: true,
        autoplayHoverPause: true,
        //dotsSpeed: 400,
		autoheight:true,
		autowidth:true,
		//width: 300
		
    });


    $('#get-inspired').owlCarousel({
        items: 1,
        nav: false,
        dots: true,
        autoplay: true,
        autoplayHoverPause: true,
        dotsSpeed: 400
    });


    $('.product-slider').owlCarousel({
        items: 3,
        dots: true,
        nav: false,
		//navText: ["<i class='fa fa-chevron-left' aria-hidden='true'></i>","<i class='fa fa-chevron-right' aria-hidden='true'></i>"],
		loop:true,
        autoplay: true,
		autoWidth: false,
        responsive: {
            480: {
                items: 3
            },
            765: {
                items: 4
            },
            991: {
                items: 7
            },
            1200: {
                items: 10
            }
        }
    });

	
	$('.collection-slider').owlCarousel({
        items: 1,
        dots: false,
        nav: true,
		navText: ["<i class='fa fa-chevron-left' aria-hidden='true'></i>","<i class='fa fa-chevron-right' aria-hidden='true'></i>"],
		loop:true,
        autoplay: true,
        responsive: {
            480: {
                items: 1
            },
            765: {
                items: 3
            },
            991: {
                items: 5
            },
            1200: {
                items: 7
            }
        },

    });


    // productDetailGallery(4000);
    utils();

    // ------------------------------------------------------ //
    // For demo purposes, can be deleted
    // ------------------------------------------------------ //

    var stylesheet = $('link#theme-stylesheet');
    $("<link id='new-stylesheet' rel='stylesheet'>").insertAfter(stylesheet);
    var alternateColour = $('link#new-stylesheet');

    if ($.cookie("theme_csspath")) {
        alternateColour.attr("href", $.cookie("theme_csspath"));
    }

    $("#colour").change(function () {

        if ($(this).val() !== '') {

            var theme_csspath = 'css/style.' + $(this).val() + '.css';

            alternateColour.attr("href", theme_csspath);

            $.cookie("theme_csspath", theme_csspath, {
                expires: 365,
                path: document.URL.substr(0, document.URL.lastIndexOf('/'))
            });

        }

        return false;
    });

});



$(window).on('load', function () {
    $(this).alignElementsSameHeight();
});

$(window).resize(function () {
    setTimeout(function () {
        $(this).alignElementsSameHeight();
    }, 150);
});


/* product detail gallery */

// function productDetailGallery(confDetailSwitch) {
//     $('.thumb:first').addClass('active');
//     timer = setInterval(autoSwitch, confDetailSwitch);
//     $(".thumb").click(function(e) {
//
// 	switchImage($(this));
// 	clearInterval(timer);
// 	timer = setInterval(autoSwitch, confDetailSwitch);
// 	e.preventDefault();
//     }
//     );
//     $('#mainImage').hover(function() {
// 	clearInterval(timer);
//     }, function() {
// 	timer = setInterval(autoSwitch, confDetailSwitch);
//     });
//
//     function autoSwitch() {
// 	var nextThumb = $('.thumb.active').closest('div').next('div').find('.thumb');
// 	if (nextThumb.length == 0) {
// 	    nextThumb = $('.thumb:first');
// 	}
// 	switchImage(nextThumb);
//     }
//
//     function switchImage(thumb) {
//
// 	$('.thumb').removeClass('active');
// 	var bigUrl = thumb.attr('href');
// 	thumb.addClass('active');
// 	$('#mainImage img').attr('src', bigUrl);
//     }
// }

function utils() {


    /* click on the box activates the radio */

    $('#checkout').on('click', '.box.shipping-method, .box.payment-method', function (e) {
        var radio = $(this).find(':radio');
        radio.prop('checked', true);
    });
    /* click on the box activates the link in it */

    $('.box.clickable').on('click', function (e) {

        window.location = $(this).find('a').attr('href');
    });
    /* external links in new window*/

    $('.external').on('click', function (e) {

        e.preventDefault();
        window.open($(this).attr("href"));
    });
    /* animated scrolling */

    $('.scroll-to, .scroll-to-top').click(function (event) {

        var full_url = this.href;
        var parts = full_url.split("#");
        if (parts.length > 1) {

            scrollTo(full_url);
            event.preventDefault();
        }
    });

    function scrollTo(full_url) {
        var parts = full_url.split("#");
        var trgt = parts[1];
        var target_offset = $("#" + trgt).offset();
        var target_top = target_offset.top - 100;
        if (target_top < 0) {
            target_top = 0;
        }

        $('html, body').animate({
            scrollTop: target_top
        }, 1000);
    }
}


$.fn.alignElementsSameHeight = function () {
    $('.same-height-row').each(function () {

        var maxHeight = 0;

        var children = $(this).find('.same-height');

        children.height('auto');

        if ($(document).width() > 768) {
            children.each(function () {
                if ($(this).innerHeight() > maxHeight) {
                    maxHeight = $(this).innerHeight();
                }
            });

            children.innerHeight(maxHeight);
        }

        maxHeight = 0;
        children = $(this).find('.same-height-always');

        children.height('auto');

        children.each(function () {
            if ($(this).innerHeight() > maxHeight) {
                maxHeight = $(this).innerHeight();
            }
        });

        children.innerHeight(maxHeight);

    });



}


/* Magnify Image with a glass */
function magnify(imgID, zoom) {
  var img, glass, w, h, bw;
  img = document.getElementById(imgID);

  /*create magnifier glass:*/
  glass = document.createElement("DIV");
  glass.setAttribute("class", "img-magnifier-glass");

  /*insert magnifier glass:*/
  img.parentElement.insertBefore(glass, img);

  /*set background properties for the magnifier glass:*/
  glass.style.backgroundImage = "url('" + img.src + "')";
  glass.style.backgroundRepeat = "no-repeat";
  glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
  bw = 3;
  w = glass.offsetWidth / 2;
  h = glass.offsetHeight / 2;

  /*execute a function when someone moves the magnifier glass over the image:*/
  glass.addEventListener("mousemove", moveMagnifier);
  img.addEventListener("mousemove", moveMagnifier);
  
  /*and also for touch screens:*/
  glass.addEventListener("touchmove", moveMagnifier);
  img.addEventListener("touchmove", moveMagnifier);
  
  //img.addEventListener("mouseleave", glass.remove());
  //img.addEventListener("touchend", glass.remove());
  
  function moveMagnifier(e) {
	var pos, x, y;
	/*prevent any other actions that may occur when moving over the image*/
	e.preventDefault();
	/*get the cursor's x and y positions:*/
	pos = getCursorPos(e);
	x = pos.x;
	y = pos.y;
	/*prevent the magnifier glass from being positioned outside the image:*/
	if (x > img.width - (w / zoom)) {x = img.width - (w / zoom);}
	if (x < w / zoom) {x = w / zoom;}
	if (y > img.height - (h / zoom)) {y = img.height - (h / zoom);}
	if (y < h / zoom) {y = h / zoom;}
	/*set the position of the magnifier glass:*/
	glass.style.left = (x - w) + "px";
	glass.style.top = (y - h) + "px";
	/*display what the magnifier glass "sees":*/
	glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
  }

  function getCursorPos(e) {
	var a, x = 0, y = 0;
	e = e || window.event;
	/*get the x and y positions of the image:*/
	a = img.getBoundingClientRect();
	/*calculate the cursor's x and y coordinates, relative to the image:*/
	x = e.pageX - a.left;
	y = e.pageY - a.top;
	/*consider any page scrolling:*/
	x = x - window.pageXOffset;
	y = y - window.pageYOffset;
	return {x : x, y : y};
  }
  

}		

/* Remove the magnifying glass over the image */
function removeGlass(){
	var x = document.getElementsByClassName("img-magnifier-glass");
    x[0].parentNode.removeChild(x[0]);
}	

/* For the counter moving up */
$(document).ready(function() {
	// jQuery counterUp
	if(jQuery().counterUp) {
		$('[data-counter-up]').counterUp({
			delay: 20,
		});
	}
})

