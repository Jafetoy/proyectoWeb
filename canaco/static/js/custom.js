(function () {

	'use strict'


	AOS.init({
		duration: 800,
		easing: 'slide',
		once: true
	});

	var preloader = function() {

		var loader = document.querySelector('.loader');
		var overlay = document.getElementById('overlayer');

		function fadeOut(el) {
			if (!el) return;
			el.style.transition = 'opacity 200ms ease-out';
			el.style.opacity = 0;
			window.setTimeout(function() {
				el.style.display = 'none';
			}, 200);
		};

		setTimeout(function() {
			fadeOut(loader);
			fadeOut(overlay);
		}, 200);
	};
	preloader();

	var tinyslider = function() {

		var slider = document.querySelectorAll('.features-slider');
		var postSlider = document.querySelectorAll('.post-slider');
		var testimonialSlider = document.querySelectorAll('.testimonial-slider');
		
		
		
		if ( slider.length> 0 ) {
			var tnsSlider = tns({
				container: '.features-slider',
				mode: 'carousel',
				speed: 700,
				items: 3,
				// center: true,
				gutter: 30,
				loop: false,
				edgePadding: 80,
				controlsPosition: 'bottom',
				// navPosition: 'bottom',
				nav: false,
				// autoplay: true,
				// autoplayButtonOutput: false,
				controlsContainer: '#features-slider-nav',
				responsive: {
					0: {
						items: 1
					},
					700: {
						items: 2
					},
					900: {
						items: 3
					}
				}
			});
		}

		if ( postSlider.length> 0 ) {
			var tnsPostSlider = tns({
				container: '.post-slider',
				mode: 'carousel',
				speed: 700,
				items: 3,
				// center: true,
				gutter: 30,
				loop: true,
				edgePadding: 10,
				controlsPosition: 'bottom',
				navPosition: 'bottom',
				nav: true,
				autoplay: true,
				autoplayButtonOutput: false,
				controlsContainer: '#post-slider-nav',
				responsive: {
					0: {
						items: 1
					},
					700: {
						items: 2
					},
					900: {
						items: 3
					}
				}
			});
		}

		if ( testimonialSlider.length> 0 ) {
			var tnsTestimonialSlider = tns({
				container: '.testimonial-slider',
				mode: 'carousel',
				speed: 700,
				items: 1,
				// center: true,
				gutter: 30,
				loop: true,
				edgePadding: 10,
				controlsPosition: 'bottom',
				navPosition: 'bottom',
				nav: true,
				autoplay: true,
				autoplayButtonOutput: false,
				controlsContainer: '#testimonial-slider-nav',
				controls: false,
				responsive: {
					0: {
						items: 1
					},
					700: {
						items: 1
					},
					900: {
						items: 1
					}
				}
			});
		}

		
	}
	tinyslider();

	var lightboxVideo = GLightbox({
		selector: '.glightbox'
	});

	// Toggle password visibility (minimal eye icon)
	document.addEventListener('click', function (e) {
		var btn = e.target.closest('.toggle-password-btn');
		if (!btn) return;
		e.preventDefault();

		var wrapper = btn.closest('.password-wrapper');
		if (!wrapper) return;

		var input = wrapper.querySelector('input');
		if (!input) return;

		var icon = btn.querySelector('i');
		if (input.type === 'password') {
			input.type = 'text';
			if (icon) {
				icon.classList.remove('bi-eye');
				icon.classList.add('bi-eye-slash');
			}
		} else {
			input.type = 'password';
			if (icon) {
				icon.classList.remove('bi-eye-slash');
				icon.classList.add('bi-eye');
			}
		}
	});

})()