(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f2d3732be8deccb8.js","sha256":"f2d3732be8deccb85f74b4994bdbf7656da257cff8974a29feddd320262ceb7f","count":2472,"publishedAt":"2026-09-12T21:15:29Z","state":"calendar-state.json","stateSha256":"f32c450e05cc994020dc96011aa78afe938fde9145d4f56fd3283318e71f5fb7"});
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
