(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bd7cb89097a2ac82.js","sha256":"bd7cb89097a2ac82885c2b858da6dca38889588785105e35d2d2de1bc3f14a30","count":2035,"publishedAt":"2026-11-05T13:10:50Z","state":"calendar-state.json","stateSha256":"2cf0f871acd7def2762b04a54538481c0c26423a3a685cfde8d2510504656494","sourceState":"calendar-source-state.json","sourceStateSha256":"2e2f2a06298dad80fa588b9ac396d6fb0c408a88c8503b63e06b40b835ea4727"});
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
