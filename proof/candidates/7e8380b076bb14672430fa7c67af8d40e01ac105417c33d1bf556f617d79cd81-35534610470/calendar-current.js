(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7e8380b076bb1467.js","sha256":"7e8380b076bb14672430fa7c67af8d40e01ac105417c33d1bf556f617d79cd81","count":2175,"publishedAt":"2026-09-20T20:13:38Z","state":"calendar-state.json","stateSha256":"7776b8f4026a886eded9ad54684655dcc29d7d6d61dbc6924b45158f76936acc"});
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
