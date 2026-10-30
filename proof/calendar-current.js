(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f8a0188424cae685.js","sha256":"f8a0188424cae6859e30d9f78a7b2c8c4d8b17f0f74bebd5ed4f4aa65ed0201c","count":2085,"publishedAt":"2026-10-30T18:06:11Z","state":"calendar-state.json","stateSha256":"9f2d57147430d9b7c5eeecbfc49571c3b9c89ea82ac9d5ab045d0927b8459685","sourceState":"calendar-source-state.json","sourceStateSha256":"a7b41f56636b7ad3e423222b714895800d399fb3d828c6cea516cad74ed222f3"});
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
