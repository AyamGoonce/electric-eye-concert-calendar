(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2d04ea73808f4eb2.js","sha256":"2d04ea73808f4eb2e3aa4a9f25d78db6478790d6703fd6d56e35e30f50fb9bc9","count":2029,"publishedAt":"2026-11-06T11:36:16Z","state":"calendar-state.json","stateSha256":"bb2a830655675220930664691f4b88106fd22e2c722d11c5974afd2f382e3e0c","sourceState":"calendar-source-state.json","sourceStateSha256":"16ec956c3a94e460856933192f0ee06692db44f4baf514659ad73edfc6f59fc2"});
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
