(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.34749c205d1cf71a.js","sha256":"34749c205d1cf71af70577bc6d45a8a6796d88f75b595e028908e3afcdc3e6b4","count":2040,"publishedAt":"2026-11-05T16:54:26Z","state":"calendar-state.json","stateSha256":"bce2d773c4321b9a4ee9e90f5f8f6486e6fdeb0d2e3af86414b328caa0b1b4ce","sourceState":"calendar-source-state.json","sourceStateSha256":"c41e9d2a23ff8646900139be0f5aed1e0e417bd64d0a449a9833e4cb2fec67c3"});
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
