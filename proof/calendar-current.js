(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a6c647d0498558d8.js","sha256":"a6c647d0498558d8c4e5233f2d10c19e47a18f337a6c5ec584051c0b56904949","count":2494,"publishedAt":"2026-09-06T11:12:02Z","state":"calendar-state.json","stateSha256":"beaaf95e5b722d7c1ac9a84e462db7648eb8d3e68c2e95387b267459103e2384"});
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
