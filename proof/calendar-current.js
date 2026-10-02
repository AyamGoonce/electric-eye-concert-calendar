(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b8eddf6416c45ee3.js","sha256":"b8eddf6416c45ee31f5f90be05d88efcaaf7caaa63988510f872ff463e87e6da","count":2215,"publishedAt":"2026-10-02T10:27:29Z","state":"calendar-state.json","stateSha256":"87ff07eb32178ac7ef995b52b930a9dd1d918eafdb0412749d2c5c545fb6010f","sourceState":"calendar-source-state.json","sourceStateSha256":"9b5630c8e6c73ddb5e18abe2a00dc2f9e33607967386ef3d417eedd7699a3448"});
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
