(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.59081558027ea71d.js","sha256":"59081558027ea71d532465b6ccbe6a23bb9bf668c670e55737b42f4d53445e68","count":2504,"publishedAt":"2026-09-10T04:53:03Z","state":"calendar-state.json","stateSha256":"2c9f2a78a6159088b49413c06aaa0e474a8f54b8bf8bb5497d216a3e771b0681"});
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
