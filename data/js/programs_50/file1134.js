var installapp = navigator.mozApps.install(manifestURL);
installapp.onsuccess = function(data) {
  // An App was installed.
};
installapp.onerror = function() {
 // An App was not installed, more information at 
 // installapp.error.name
};
