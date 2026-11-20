(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b33175827ce040e0.js","sha256":"b33175827ce040e0415412c01f927256f10b56fc520db412e7a234abafae9321","count":2137,"publishedAt":"2026-11-20T02:22:41Z","state":"calendar-state.json","stateSha256":"37b4a331de4a2469cbe728110fa5d3f2af6f08041f2d649fa9bc66a45ae5afb0","sourceState":"calendar-source-state.json","sourceStateSha256":"b5d5588c63ce4036a1fc8fdcacbef264965b01892ed8745092f5703d2f19c088"});
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
