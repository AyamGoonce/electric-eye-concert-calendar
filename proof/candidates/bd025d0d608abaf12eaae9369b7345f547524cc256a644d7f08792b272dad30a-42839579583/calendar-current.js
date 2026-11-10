(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bd025d0d608abaf1.js","sha256":"bd025d0d608abaf12eaae9369b7345f547524cc256a644d7f08792b272dad30a","count":2210,"publishedAt":"2026-11-10T14:59:07Z","state":"calendar-state.json","stateSha256":"2c7c477c755aaa4c7e5db16fd3ba5950326588e24458bcd907de930f5cb9f08b","sourceState":"calendar-source-state.json","sourceStateSha256":"b786238d1d5a1a157da21cd80a66e10d9702b669ba1ecbf3fa3502f28c40aa98"});
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
