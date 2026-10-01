(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cad80eeaf61e2bc6.js","sha256":"cad80eeaf61e2bc66ebafa632944cf7076bf1429afe2c92ca01c446e3636d631","count":2227,"publishedAt":"2026-10-01T18:27:32Z","state":"calendar-state.json","stateSha256":"7e991f7be590cc35c2b87cd3c2b05323c2c481ff4a524d91bd9517a169db12ae","sourceState":"calendar-source-state.json","sourceStateSha256":"aadc9df695a85fc824a63097db4229d05cd04654f70ba1585be2220481e30631"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
