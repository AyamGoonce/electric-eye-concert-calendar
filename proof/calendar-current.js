(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.556a11c09fa5f00b.js","sha256":"556a11c09fa5f00b636a41508697c55f5103efc649b7adeedc42facf4719f704","count":2443,"publishedAt":"2026-09-08T14:10:31Z","state":"calendar-state.json","stateSha256":"db763327f30c6b7cdc7579efca8f30df2d1069082d6a8c131ee24a2641f49049"});
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
