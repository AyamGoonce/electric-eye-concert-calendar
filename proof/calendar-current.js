(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.beb4c6b8de0311ff.js","sha256":"beb4c6b8de0311ff531d326ed0e12761ceedf74bf933f8482d23acea658aa601","count":2400,"publishedAt":"2026-09-06T23:50:21Z","state":"calendar-state.json","stateSha256":"26825b8be170b04a6cc1062af54b00f2374213f39a4dd72cd94fefcd51188df0"});
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
