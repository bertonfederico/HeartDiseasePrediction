// Controllers for slideshow
var slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
	showSlides(slideIndex += n);
}

function currentSlide(n) {
  	showSlides(slideIndex = n);
}

function showSlides(n) {
	let i;
	const slides = document.getElementsByClassName("mySlides");
	const dots = document.getElementsByClassName("dot");
	if (n > slides.length) {slideIndex = 1}
	if (n < 1) {slideIndex = slides.length}
	for (i = 0; i < slides.length; i++) {
		slides[i].style.display = "none";
	}
	for (i = 0; i < dots.length; i++) {
		dots[i].className = dots[i].className.replace(" active", "");
	}
	slides[slideIndex-1].style.display = "block";
	dots[slideIndex-1].className += " active";
}



// Controllers for form
var currentTab = 0;
showTab(currentTab);

function showTab(n) {
	var x = document.getElementsByClassName("tab");
	x[n].style.display = "block";
	document.getElementById("submitBtn").style.display = "none";
	if (n == 0) {
		document.getElementById("prevBtn").style.display = "none";
	} else {
		document.getElementById("prevBtn").style.display = "inline";
	}
	if (n == (x.length - 1)) {
		document.getElementById("submitBtn").style.display = "inline";
		document.getElementById("nextBtn").style.display = "none";
	} else {
		document.getElementById("nextBtn").style.display = "inline";
	}
}

function nextPrev(n) {
	var x = document.getElementsByClassName("tab");
	x[currentTab].style.display = "none";
	currentTab = currentTab + n;
	showTab(currentTab);
}