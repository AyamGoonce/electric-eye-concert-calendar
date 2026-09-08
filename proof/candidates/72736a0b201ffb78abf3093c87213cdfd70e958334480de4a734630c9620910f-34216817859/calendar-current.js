(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.72736a0b201ffb78.js","sha256":"72736a0b201ffb78abf3093c87213cdfd70e958334480de4a734630c9620910f","count":2492,"publishedAt":"2026-09-08T10:51:47Z","state":"calendar-state.json","stateSha256":"8cbf17e63b321f6dfa53c4515d758b2c37b5ff23886c52cdeedb7c197c58f37d"});
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
