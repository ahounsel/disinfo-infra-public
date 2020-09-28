var tabRecords = {}; //Global var to store all TabRecords

// Constructor for a TabRecord
// Stores the current URL and prior URL for a tab
function TabRecord(_url,_priorUrl) {
    this.currentURL = (typeof _url !== 'string') ? "" : _url;
    this.priorURL = (typeof _priorUrl !== 'string') ? "" : _priorUrl;
}

// If it's the first time we've seen this tab, create a record for it
function createTabRecordIfNeeded(tabId) {
    if(!tabRecords.hasOwnProperty(tabId) || typeof tabRecords[tabId] !== 'object') {
        tabRecords[tabId] = new TabRecord();
    }
}

// Update a tab record after it has navigated to a new URL
function updateTabRecord(details) {
    createTabRecordIfNeeded(details.tabId);
    if(details.frameId !== 0){  // Main frame only
        return;
    }

    tabRecords[details.tabId].priorURL = tabRecords[details.tabId].currentURL;
    tabRecords[details.tabId].currentURL = details.url;
}

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
    
    console.log(domain);
    return domain;
}

// If the site is in our disinformation list 
// and it has not been cleared in this session,
// show the warning
function warnDisinfoSite(details){
    createTabRecordIfNeeded(details.tabId);
    var domain = parseDomain(details.url);

    chrome.storage.local.get(function(result){
        cleared_sites = result.cleared_sites;

        if (cleared_sites.indexOf(domain) < 0){    //If the site has not been cleared
            if (classified_xhr.responseText.split(",").indexOf(domain) >= 0){   //If the site is disinformation
                console.log('Disinfo URL:',details.url);
                console.log('Prior URL:',tabRecords[details.tabId].currentURL);

                var urlToGoBackTo = tabRecords[details.tabId].currentURL;
                urlToGoBackTo = (typeof urlToGoBackTo === 'string') ? urlToGoBackTo : '';

                chrome.storage.local.set({"disinfo_domain": details.url}, function() {});
                chrome.storage.local.set({"site_to_go_back_to": urlToGoBackTo}, function() {});

                chrome.tabs.update(details.tabId,{url: "warning.html"},function(tab){
                    if(chrome.runtime.lastError){
                        if(chrome.runtime.lastError.message.indexOf('No tab with id:') > -1){
                            console.log('Error:',chrome.runtime.lastError.message)
                        } else {
                            console.log('Error:',chrome.runtime.lastError.message)
                        }
                    }
                });
            }
        } else {
            console.log("Skipping cleared site: " + domain);
        }
    });
}

//Add listeners at startup
chrome.webNavigation.onCompleted.addListener(updateTabRecord);
chrome.webNavigation.onBeforeNavigate.addListener(warnDisinfoSite);

//Get the URLs for all current tabs when extension is installed
chrome.tabs.query({},tabs => {
    tabs.forEach(tab => {
        createTabRecordIfNeeded(tab.id);
        tabRecords[tab.id].currentURL = tab.url;
        warnDisinfoSite({
            tabId : tab.id,
            frameId : 1,
            url : tab.url
        });

    });
});

//Read the list of disinformation sites
var classified_sites_url = chrome.runtime.getURL('classified_sites.txt');
var classified_xhr = new XMLHttpRequest();
classified_xhr.open('GET', classified_sites_url, true);
classified_xhr.send(null);

//Create the empty list of cleared sites
chrome.storage.local.set({"cleared_sites": []}, function() {
	console.log('Cleared sites: []');
});
