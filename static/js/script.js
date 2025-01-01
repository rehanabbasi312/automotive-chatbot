$(document).ready(function () {

    // loader
    setTimeout(function () {
        $('.loaders').fadeOut();
    }, 100);



    // scroll-Top
    $(window).scroll(function () {
        if ($(this).scrollTop() > 500) {
            $('.scrolltotop').fadeIn();
        } else {
            $('.scrolltotop').fadeOut();
        }

    });

    $('.scrolltotop').click(function () {
        $('html,body').animate({ scrollTop: 0 }, 1000);
        return false;
    });

    //smartmenus
    $(function () {
        $('#main-menu').smartmenus({
            subMenusSubOffsetX: 1,
            subMenusSubOffsetY: -8
        });
    });


    $(".toggle-password").click(function () {
        $(this).toggleClass("bi bi-eye");
        input = $(this).parent().find("input");
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });


    // fixedtop
    $(window).scroll(function () {
        var headerTopHeight = $(".header-area").outerHeight();
        var totalHeight = headerTopHeight;
        var utd = $(window).scrollTop();

        if (utd > totalHeight) {
            $(".header-area").addClass("shadows");
            $(".compare-top").addClass("fixed");
        } else {
            $(".header-area").removeClass("shadows");
            $(".compare-top").removeClass("fixed");
        }
        return false;
    });

    $(".navbar-toggler-icon").click(function () {
        $(".header-area").addClass("shadows");
    });



    // time-box 
    $('.available ul li').click(function () {
        $('.available ul li').removeClass("act");
        $(this).addClass("act");
        return false;
    });


    // duration tabs
    $('.duratio ul li').click(function () {
        $('.duratio ul li').removeClass("act");
        $(this).addClass("act");
        return false;
    });



    //slider
    $('.suggest').slick({
        dots: false,
        infinite: false,
        autoplay: false,
        slidesToShow: 6,
        slidesToScroll: 6,
        speed: 600,
        arrows: true,
        focusOnSelect: false,
        nextArrow: '<span class="next"><i class="bi bi-chevron-right"></i></span>',
        prevArrow: '<span class="prev"><i class="bi bi-chevron-left"></i></span>',
        responsive: [{
            breakpoint: 1600,
            settings: {
                slidesToShow: 5,
                slidesToScroll: 5,
            }
        }, {
            breakpoint: 1200,
            settings: {
                slidesToShow: 4,
                slidesToScroll: 4,
            }
        }, {
            breakpoint: 992,
            settings: {
                slidesToShow: 3,
                slidesToScroll: 3,
            }
        },
        {
            breakpoint: 768,
            settings: {
                slidesToShow: 3,
                slidesToScroll: 3,
            }
        },
        {
            breakpoint: 480,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 2,
            }
        }
        ]
    });



    // Slider for the remaining images
    $('.deails-slider .carousel').slick({
        dots: false,
        infinite: false,
        autoplay: false,
        slidesToShow: 1, // Use rows and slidesPerRow for layout
        slidesToScroll: 1,
        speed: 600,
        focusOnSelect: false,
        arrows: true,
        rows: 2, // Display in two rows
        slidesPerRow: 5, // Display 3 images per row
        nextArrow: '<span class="next"><i class="bi bi-chevron-right"></i></span>',
        prevArrow: '<span class="prev"><i class="bi bi-chevron-left"></i></span>',
        responsive: [
            {
                breakpoint: 1200,
                settings: {
                    rows: 2,
                    slidesPerRow: 5, // Show fewer images on smaller screens
                },
            },
            {
                breakpoint: 768,
                settings: {
                    rows: 1,
                    slidesPerRow: 5, // Single row on very small screens
                },
            },
        ],
    });




    $(".carcon .chexck").click(function () {
        $(".compare-area").addClass("show");
    });

    $(".delt").click(function () {
        $(".compare-area").removeClass("show");
    });


    (function ($) {

        $("#min_price1,#max_price1").on('change', function () {
            var min_price_range = parseInt($("#min_price1").val());
            var max_price_range = parseInt($("#max_price1").val());

            if (min_price_range > max_price_range) {
                $('#max_price1').val(min_price_range);
            }

            $("#slider-range1").slider({
                values: [min_price_range, max_price_range]
            });

        });


        $("#min_price1,#max_price1").on("paste keyup", function () {
            var min_price_range = parseInt($("#min_price1").val());
            var max_price_range = parseInt($("#max_price1").val());

            if (min_price_range == max_price_range) {

                max_price_range = min_price_range + 100;

                $("#min_price1").val(min_price_range);
                $("#max_price1").val(max_price_range);
            }

            $("#slider-range1").slider({
                values: [min_price_range, max_price_range]
            });

        });


        $(function () {
            $("#slider-range1").slider({
                range: true,
                orientation: "horizontal",
                min: 500,
                max: 60000,
                values: [10000, 50000],
                step: 100,

                slide: function (event, ui) {
                    if (ui.values[0] == ui.values[1]) {
                        return false;
                    }

                    $("#min_price1").val(ui.values[0]);
                    $("#max_price1").val(ui.values[1]);
                }
            });

            $("#min_price1").val($("#slider-range1").slider("values", 0));
            $("#max_price1").val($("#slider-range1").slider("values", 1));

        });

        $("#slider-range1").click(function () {
            var min_price = $('#min_price1').val();
            var max_price = $('#max_price1').val();

        });

    })(jQuery);



    //magnific
    $(function () {
        $('.magnific').magnificPopup({
            type: 'image',
            gallery: {
                enabled: true
            }
        });
    });

    //magnific
    $(function () {
        $('.magnific2').magnificPopup({
            type: 'image',
            gallery: {
                enabled: true
            }
        });
    });





});