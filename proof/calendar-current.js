(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.efffb22319ecebb7.js","sha256":"efffb22319ecebb7eaf4f7309ed06221e029dbfe6559b9107ce319bd29aaa909","count":2468,"publishedAt":"2026-09-06T12:36:05Z","state":"calendar-state.json","stateSha256":"ea3cef5756d7994cc8b37c748d9a469f15e319660dd0b8b74bc5dfb72d149c13"});
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
