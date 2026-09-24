(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1ae103dded35e85f.js","sha256":"1ae103dded35e85f7ca222523b3b289b1e6a3ee3005c59c33a8e84b6bd7463e3","count":2145,"publishedAt":"2026-09-24T17:25:05Z","state":"calendar-state.json","stateSha256":"0f6c50af588c5471dd90acf41ad4d70dad413cd10fb13f5a0cd943d052814000","sourceState":"calendar-source-state.json","sourceStateSha256":"051d832f4f5aa5d5863eff5894d8ab6a03b21ea897a09bf8cd34ba5c8aa5dcff"});
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
