(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.841545632e0e007b.js","sha256":"841545632e0e007bf050255a86188ed39095f519ad2c5225ed95c457180c1d65","count":2129,"publishedAt":"2026-11-25T17:18:57Z","state":"calendar-state.json","stateSha256":"7473c48a57af38ba87422037bde53a7fcd8a8d8c7783c0943eb5dc43ff238098","sourceState":"calendar-source-state.json","sourceStateSha256":"20f046c212c71e15e03df188c07157817984f2572ed925f6027583e21c9747ec"});
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
