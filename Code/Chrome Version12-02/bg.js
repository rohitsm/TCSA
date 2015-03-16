
chrome.browserAction.onClicked.addListener(function(tab) {
  //chrome.tabs.create({'url': chrome.extension.getURL('keyGen.html')}, function(tab) {
  	chrome.tabs.create({'url': 'https://155.69.145.226'}, function(tab) {
    // Tab opened.
  });
});