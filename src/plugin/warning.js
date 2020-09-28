// Extract the domain from the hostname
function parseDomain(url) {
    var domain = (new URL(url)).hostname,
        splitArr = domain.split('.'),
        arrLen = splitArr.length;

    // Check if there is a subdomain 
    if (arrLen > 2) {
        domain = splitArr[arrLen - 2] + '.' + splitArr[arrLen - 1];
        // Check if it's using a ccTLD
        if (splitArr[arrLen - 2].length == 2 && splitArr[arrLen - 1].length == 2) {
            domain = splitArr[arrLen - 3] + '.' + domain;
        }
    }
    
    return domain;
}

// When "Back to safety" is clicked, go back
function primaryClickHandler(e) {
	chrome.storage.local.get(function(result){
		window.location.href=result.site_to_go_back_to;
	})
}

// When "Learn more" is clicked, show the detail text,
// set the link destination, and inject the domain name
// into the text
function secondaryClickHandler(e) {
	document.getElementById("details").style.display="block";

	chrome.storage.local.get(function(result){
		url = result.disinfo_domain;
		domain = parseDomain(url);
		document.getElementById("proceed-link").setAttribute('href',url);
		document.getElementById("disinfo-domain").innerHTML = domain;
		document.getElementById("disinfo-domain-in-link").innerHTML = domain;
	});
}

// When "Proceed" is clicked, add the domain to the 
// list of cleared sites and then navigate to the page
function proceedClickHandler(e) {
	chrome.storage.local.get(function(result){
		cleared_domain = parseDomain(result.disinfo_domain);
		cleared_sites = result.cleared_sites;
		cleared_sites.push(cleared_domain);
		chrome.storage.local.set({"cleared_sites": cleared_sites}, function() {
        	console.log('Added ' + cleared_domain + " to cleared_sites");
    	});
	});
}

// Register the listeners and inject the domain name into the main message
document.addEventListener('DOMContentLoaded', function () {
	document.getElementById('primary-button').addEventListener('click', primaryClickHandler);
	document.getElementById('details-button').addEventListener('click', secondaryClickHandler);
	document.getElementById('proceed-link').addEventListener('click', proceedClickHandler);

	chrome.storage.local.get(function(result){
		document.getElementById('disinfo-domain-in-main-message').innerHTML=parseDomain(result.disinfo_domain);
	});
	
});