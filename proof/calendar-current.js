(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ca1b9ae853f7cdf7.js","sha256":"ca1b9ae853f7cdf70af87418c6a826d8813bef9f8eb07b82382bc7dd1b9f6518","count":1823,"publishedAt":"2026-08-28T09:31:34Z","state":"calendar-state.json","stateSha256":"b15d1f19bd6a8b9b95e6b905bce079b2b776add3a2161185d11279e14a0e71ad"});
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
