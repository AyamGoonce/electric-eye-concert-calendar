(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.31c5d2fc7e513d5a.js","sha256":"31c5d2fc7e513d5a26eef64b05f79b00a57d724a2fdecb392c2163c64345b720","count":1709,"publishedAt":"2026-08-23T12:05:18Z","state":"calendar-state.json","stateSha256":"c2cf24248df9dd06108242aa692f835d6452ce269efebc1ae7bd77dd107359d0"});
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
