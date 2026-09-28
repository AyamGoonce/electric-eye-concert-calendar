(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.02e34a02388dea89.js","sha256":"02e34a02388dea89a2b214a7554faa37ca65d8454ee570a73ae91709c7d7bef0","count":2067,"publishedAt":"2026-09-28T12:08:30Z","state":"calendar-state.json","stateSha256":"e163a5873d80ceb0775a6e277941e6ec3f941bf4af95a293d88498d033cfb810","sourceState":"calendar-source-state.json","sourceStateSha256":"ad7e0c7b485e4c94578c3e725ae62eade63c818ef23042b1198b2944e3885a18"});
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
