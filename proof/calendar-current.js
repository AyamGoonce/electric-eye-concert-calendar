(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e4b97f58ca45e81d.js","sha256":"e4b97f58ca45e81d0d15c9ba7f66b73a25d613e61e47feed6b7b7a66df8699f5","count":2475,"publishedAt":"2026-09-07T23:41:39Z","state":"calendar-state.json","stateSha256":"13455bc1ee6b048c3ac84dbd7fd39e9a9f21dbf25e1bd832f4d89d1b350aab9c"});
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
