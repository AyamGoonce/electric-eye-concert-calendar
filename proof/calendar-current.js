(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d0b951ea5d553717.js","sha256":"d0b951ea5d553717b588cd5b9ed3d63cc77fcb98551ab89c9dc65df6b520b230","count":2441,"publishedAt":"2026-09-13T12:02:51Z","state":"calendar-state.json","stateSha256":"8591e5d14116663f417e7a185b3a06ffeddd05b61c63a855f133b72c1f4c51af"});
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
