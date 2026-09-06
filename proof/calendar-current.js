(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.57af63a9dd3faeb4.js","sha256":"57af63a9dd3faeb4de6c9d2d51bbe115ac12e61d08456366a443ca4e68fd96a9","count":2402,"publishedAt":"2026-09-06T13:40:23Z","state":"calendar-state.json","stateSha256":"2b4896a94d1ac973da37d8940d5f51fe03a8a2d71fc09a72960c33f559c1ab8f"});
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
