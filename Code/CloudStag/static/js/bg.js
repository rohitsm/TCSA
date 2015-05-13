
chrome.browserAction.onClicked.addListener(function(tab) {
  //chrome.tabs.create({'url': chrome.extension.getURL('keyGen.html')}, function(tab) {
  	chrome.tabs.create({'url': '../templates/test.html'}, function(tab) {
    // Tab opened.
  });
});