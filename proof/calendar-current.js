(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0c1583ab27ab2339.js","sha256":"0c1583ab27ab2339aaccccc68371e7f95b6743911cb76462ee044769dafe6c88","count":2076,"publishedAt":"2026-10-24T23:21:53Z","state":"calendar-state.json","stateSha256":"09f9575618e13822edc7ffef6e72b4079260aacbb299f019f1299b50ca6fd39f","sourceState":"calendar-source-state.json","sourceStateSha256":"f919cf9649bbe90a1834bb71f2824ed9c0c58511f1d51045fb1bdca44f41a2f3"});
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
