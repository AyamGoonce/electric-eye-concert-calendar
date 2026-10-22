(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0fb721893d7e2607.js","sha256":"0fb721893d7e2607269a7f422bf9905e6cb6162667305f51bb999c73bade95ad","count":2091,"publishedAt":"2026-10-22T17:18:36Z","state":"calendar-state.json","stateSha256":"6ef478d0e93d7632695bb531538346fcd2f4cb81669cb46f175a8de2c06e71f3","sourceState":"calendar-source-state.json","sourceStateSha256":"3a68d3a06ad857a70986c142ffdda4a48cb201e4682ad45f7c84de990278687e"});
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
