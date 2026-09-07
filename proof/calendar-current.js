(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e75b615486a20aab.js","sha256":"e75b615486a20aabdfada9e2b485e728884f72e27b8a2b60e7ee5645fe77d24d","count":2475,"publishedAt":"2026-09-07T16:24:12Z","state":"calendar-state.json","stateSha256":"9b4c8cf4742783ccd97b8975096f6aaec3393c53fdac7c9a2abe7ba2153ea5a0"});
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
