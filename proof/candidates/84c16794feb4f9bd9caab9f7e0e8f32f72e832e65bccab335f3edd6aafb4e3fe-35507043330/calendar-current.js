(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.84c16794feb4f9bd.js","sha256":"84c16794feb4f9bd9caab9f7e0e8f32f72e832e65bccab335f3edd6aafb4e3fe","count":2094,"publishedAt":"2026-09-20T11:11:54Z","state":"calendar-state.json","stateSha256":"863dec6de0a75048da33a5feb1248645ff5f3bbc19060259f082c44c268ea3f4"});
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
