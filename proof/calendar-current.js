(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.272f8d57d64505ef.js","sha256":"272f8d57d64505ef25a75e60e6ad54572cc54b0ab3b3c633dcec5d0cb2cd1b4d","count":1731,"publishedAt":"2026-08-24T19:04:35Z","state":"calendar-state.json","stateSha256":"1fb3bffa57236b448d2e04d16a34e31a1784e9fce028482cea0525827ced4efd"});
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
