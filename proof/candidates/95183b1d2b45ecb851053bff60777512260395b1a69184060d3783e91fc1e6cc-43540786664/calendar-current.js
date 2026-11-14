(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.95183b1d2b45ecb8.js","sha256":"95183b1d2b45ecb851053bff60777512260395b1a69184060d3783e91fc1e6cc","count":2137,"publishedAt":"2026-11-14T01:28:39Z","state":"calendar-state.json","stateSha256":"f0a8571bebe2a79441ef6a6fe7dfd8e489246012e216b5d06249d976fc52c605","sourceState":"calendar-source-state.json","sourceStateSha256":"4f3c3bcdaea5f50d76368944336d457baa94838adbd3e9c07fb3b82e27099ace"});
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
