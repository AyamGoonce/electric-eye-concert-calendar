(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a0480e8e88617cbc.js","sha256":"a0480e8e88617cbcbd1ebe74f18f16d7719b2105ec7c1e6851c0ff2d7cdc2f1a","count":2495,"publishedAt":"2026-09-08T23:30:42Z","state":"calendar-state.json","stateSha256":"ef81c0696fb468b4e2be600824710ff8081bac2c5f9d26dca2fad6bee0ce46f8"});
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
