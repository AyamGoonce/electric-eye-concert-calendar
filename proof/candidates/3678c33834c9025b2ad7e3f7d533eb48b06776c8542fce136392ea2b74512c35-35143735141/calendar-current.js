(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3678c33834c9025b.js","sha256":"3678c33834c9025b2ad7e3f7d533eb48b06776c8542fce136392ea2b74512c35","count":2520,"publishedAt":"2026-09-16T20:02:52Z","state":"calendar-state.json","stateSha256":"e2c0724d57900362b5a717b9a7623a70975e7e26f35508412614bc26319ef8ab"});
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
