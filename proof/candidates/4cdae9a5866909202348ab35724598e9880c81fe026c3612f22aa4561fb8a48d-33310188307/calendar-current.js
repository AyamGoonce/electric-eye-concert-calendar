(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4cdae9a586690920.js","sha256":"4cdae9a5866909202348ab35724598e9880c81fe026c3612f22aa4561fb8a48d","count":2061,"publishedAt":"2026-08-30T12:05:56Z","state":"calendar-state.json","stateSha256":"7bc9678ae1bf32e07292dbd708347f3e5d8dd4cb4c11bfac2113ae3735b658b8"});
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
